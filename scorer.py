from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, and_
from models import Delivery, Match, Team, Venue, Player
from form_engine import FormEngine
from db import SessionLocal, get_canonical_team_name
import pandas as pd

class MatchScorer:
    """
    The Engine Room of CricPredict.
    Calculates win probability based on weighted factors.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.form_engine = FormEngine(db)

    def calculate_h2h_advantage(self, team_a_id, team_b_id, match_format):
        """Pillar 2: Recent Head-to-Head History (Last 5 Encounters)"""
        h2h_matches = (
            self.db.query(Match).filter(
                ((Match.team_a_id == team_a_id) & (Match.team_b_id == team_b_id)) |
                ((Match.team_a_id == team_b_id) & (Match.team_b_id == team_a_id))
            )
            .filter(Match.format == match_format)
            .order_by(desc(Match.date))
            .limit(5)
            .all()
        )
        
        if not h2h_matches:
            return 0.5 # Neutral
            
        team_a_wins = sum(1 for m in h2h_matches if m.winner_id == team_a_id)
        # Weighted older matches slightly less? 
        # For simplicity, let's stick to pure win rate of the last 5 as requested.
        return team_a_wins / len(h2h_matches)

    def get_recent_team_momentum(self, team_id, match_format, limit=5):
        """Calculates win rate in the last 5 matches against any opponent."""
        recent_matches = (
            self.db.query(Match)
            .filter((Match.team_a_id == team_id) | (Match.team_b_id == team_id))
            .filter(Match.format == match_format)
            .order_by(desc(Match.date))
            .limit(limit)
            .all()
        )
        
        if not recent_matches:
            return 0.5
            
        wins = sum(1 for m in recent_matches if m.winner_id == team_id)
        return wins / len(recent_matches)

    def get_top_performers_from_recent_match(self, team_id, match_format):
        """Identifies 'Top Performers' (MVP candidates) from the team's most recent match."""
        recent_match = (
            self.db.query(Match)
            .filter((Match.team_a_id == team_id) | (Match.team_b_id == team_id))
            .filter(Match.format == match_format)
            .order_by(desc(Match.date))
            .first()
        )
        
        if not recent_match:
            return []
            
        # Get top 3 batters by runs
        top_batters = (
            self.db.query(
                Player.name,
                func.sum(Delivery.runs_off_bat).label('runs'),
                func.count(Delivery.delivery_id).label('balls')
            )
            .join(Delivery, Player.player_id == Delivery.batsman_id)
            .filter(Delivery.match_id == recent_match.match_id)
            .filter(Delivery.batting_team_id == team_id)
            .group_by(Player.name)
            .order_by(desc('runs'))
            .limit(2)
            .all()
        )

        # Get top 2 bowlers by wickets
        top_bowlers = (
            self.db.query(
                Player.name,
                func.count(Delivery.player_dismissed_id).label('wickets'),
                func.sum(Delivery.runs_off_bat + Delivery.extras).label('runs_conceded')
            )
            .join(Delivery, Player.player_id == Delivery.bowler_id)
            .filter(Delivery.match_id == recent_match.match_id)
            .filter(Delivery.bowling_team_id == team_id)
            .group_by(Player.name)
            .order_by(desc('wickets'), ('runs_conceded'))
            .limit(2)
            .all()
        )

        performers = []
        for b in top_batters:
            performers.append({
                "name": b.name,
                "stat": f"{b.runs} ({b.balls})",
                "role": "Batsman",
                "match_date": str(recent_match.date)
            })
        for bw in top_bowlers:
            if bw.wickets > 0:
                performers.append({
                    "name": bw.name,
                    "stat": f"{bw.wickets} wkts",
                    "role": "Bowler",
                    "match_date": str(recent_match.date)
                })
        
        return performers

    def calculate_venue_advantage(self, team_id, venue_id, match_format):
        """Pillar 4: Venue Mastery (15% Weight)"""
        venue_matches = self.db.query(Match).filter(
            (Match.venue_id == venue_id) & 
            ((Match.team_a_id == team_id) | (Match.team_b_id == team_id))
        ).filter(Match.format == match_format).all()
        
        if not venue_matches:
            return 0.5 # Neutral
            
        team_wins = sum(1 for m in venue_matches if m.winner_id == team_id)
        return team_wins / len(venue_matches)

    def get_team_form_score(self, team_id, match_format):
        """Pillar 1: Player Form Index (30% Weight)"""
        # Improved: Fetch players from the most recent match for this team
        recent_match = self.db.query(Match).filter(
            (Match.team_a_id == team_id) | (Match.team_b_id == team_id)
        ).filter(Match.format == match_format).order_by(desc(Match.date)).first()
        
        if not recent_match:
            return 0.5
            
        # Get unique players from that match for this team
        player_ids = self.db.query(Delivery.batsman_id).filter(
            Delivery.match_id == recent_match.match_id,
            Delivery.batting_team_id == team_id
        ).distinct().all()
        
        player_ids = [p[0] for p in player_ids]
        
        if not player_ids:
            return 0.5
            
        pfi_scores = []
        for p_id in player_ids:
            pfi = self.form_engine.calculate_pfi(p_id, match_format)
            if pfi > 0:
                pfi_scores.append(min(pfi / 100, 1.0))
        
        return sum(pfi_scores) / len(pfi_scores) if pfi_scores else 0.5

    def get_team_squad(self, team_id, match_format):
        """Fetch active squad players and their PFI.
        
        Priority 1: Use curated squad data (franchise_team_id / intl_team_id columns)
                     This reflects the LATEST 2025 roster after trades/auctions.
        Priority 2: Fall back to players from recent match deliveries (legacy behavior)
        """
        from sqlalchemy import text
        
        # Determine which column to query based on format
        if match_format == 'IPL':
            squad_players = self.db.execute(
                text("SELECT player_id FROM players WHERE franchise_team_id = :tid"),
                {"tid": team_id}
            ).fetchall()
        else:
            # For T20I, ODI, Tests - use international team mapping
            squad_players = self.db.execute(
                text("SELECT player_id FROM players WHERE intl_team_id = :tid"),
                {"tid": team_id}
            ).fetchall()
        
        # If curated squad exists, use it
        if squad_players:
            all_player_ids = [row[0] for row in squad_players]
        else:
            # Fallback: infer from recent match deliveries (legacy behavior)
            recent_matches = self.db.query(Match).filter(
                (Match.team_a_id == team_id) | (Match.team_b_id == team_id)
            ).filter(Match.format == match_format).order_by(desc(Match.date)).limit(3).all()
            
            if not recent_matches:
                return []
                
            match_ids = [m.match_id for m in recent_matches]
            
            batters = self.db.query(Delivery.batsman_id).filter(
                Delivery.match_id.in_(match_ids), Delivery.batting_team_id == team_id
            ).distinct().all()
            
            non_strikers = self.db.query(Delivery.non_striker_id).filter(
                Delivery.match_id.in_(match_ids), Delivery.batting_team_id == team_id
            ).distinct().all()
            
            bowlers = self.db.query(Delivery.bowler_id).filter(
                Delivery.match_id.in_(match_ids), Delivery.bowling_team_id == team_id
            ).distinct().all()
            
            all_player_ids = list(set(
                [p[0] for p in batters] + [p[0] for p in non_strikers] + [p[0] for p in bowlers]
            ))
        
        # Cap at 15 for performance
        if len(all_player_ids) > 15:
            all_player_ids = all_player_ids[:15]

        squad = []
        for p_id in all_player_ids:
            player = self.db.query(Player).filter(Player.player_id == p_id).first()
            if player:
                pfi_data = self.form_engine.calculate_pfi(player.player_id, match_format)
                
                bat_style = player.batting_style
                bowl_style = player.bowling_style
                
                if not bat_style:
                    bat_style = "Right-Handed Batsman"
                
                if not bowl_style and pfi_data["role"] in ["Bowler", "All-rounder"]:
                    bowl_style = "Right-Arm Fast Bowler" if hash(player.name) % 2 == 0 else "Right-Arm Off Spin Bowler"
                
                encoded_name = player.name.replace(" ", "+")
                avatar_url = f"https://ui-avatars.com/api/?name={encoded_name}&background=random&color=fff&size=128"
                
                squad.append({
                    "name": player.name,
                    "pfi": pfi_data["total"],
                    "batting_pfi": pfi_data["batting"],
                    "bowling_pfi": pfi_data["bowling"],
                    "role": pfi_data["role"],
                    "image_url": avatar_url,
                    "batting_style": bat_style,
                    "bowling_style": bowl_style
                })
        return sorted(squad, key=lambda x: x['pfi'], reverse=True)

    def predict_match(self, team_a_name, team_b_name, venue_name, match_format='IPL'):
        """
        Combines all pillars to predict win probability with detailed stats.
        """
        # Smart Team Lookup
        def find_team(name, fmt):
            name = get_canonical_team_name(name)
            print(f"--- DEBUG: find_team('{name}', '{fmt}') ---")
            # Priority 1: Exact Match
            team = self.db.query(Team).filter(Team.name == name).first()
            if team: 
                print(f"Matched P1 Exact: {team.name}")
                return team
            
            # Priority 2: Fuzzy match with Team Type filter
            ttype = 'Franchise' if fmt == 'IPL' else 'International'
            team = self.db.query(Team).filter(Team.name.ilike(f"%{name}%"), Team.team_type == ttype).first()
            if team: 
                print(f"Matched P2 Fuzzy+Type: {team.name}")
                return team
            
            # Priority 3: Fuzzy match fallback
            team = self.db.query(Team).filter(Team.name.ilike(f"%{name}%")).first()
            if team: print(f"Matched P3 Fallback: {team.name}")
            return team

        team_a = find_team(team_a_name, match_format)
        team_b = find_team(team_b_name, match_format)
        
        # Smart Venue Lookup
        venue = self.db.query(Venue).filter(Venue.name == venue_name).first()
        if not venue:
            venue = self.db.query(Venue).filter(Venue.name.ilike(f"%{venue_name}%")).first()
        
        if not team_a or not team_b:
            return {"error": f"Teams not found: {team_a_name if not team_a else ''} {team_b_name if not team_b else ''}"}
            
        # Pillar 2: Head-to-Head (Analytically Last 5, UI Global)
        all_h2h_matches = (
            self.db.query(Match).filter(
                ((Match.team_a_id == team_a.team_id) & (Match.team_b_id == team_b.team_id)) |
                ((Match.team_a_id == team_b.team_id) & (Match.team_b_id == team_a.team_id))
            )
            .filter(Match.format == match_format)
            .order_by(desc(Match.date))
            .all()
        )
        
        # Stats for UI (All Time)
        h2h_stats = {
            "total": len(all_h2h_matches),
            "team_a_wins": sum(1 for m in all_h2h_matches if m.winner_id == team_a.team_id),
            "team_b_wins": sum(1 for m in all_h2h_matches if m.winner_id == team_b.team_id),
            "draws": sum(1 for m in all_h2h_matches if m.winner_id is None)
        }
        
        # Advantage for Calculation (Last 5 focus)
        recent_h2h = all_h2h_matches[:5]
        recent_a_wins = sum(1 for m in recent_h2h if m.winner_id == team_a.team_id)
        h2h_adv = recent_a_wins / len(recent_h2h) if len(recent_h2h) > 0 else 0.5
        
        # Pillar 4: Venue Advantage (15% Weight)
        venue_adv_a = self.calculate_venue_advantage(team_a.team_id, venue.venue_id if venue else None, match_format)
        venue_adv_b = self.calculate_venue_advantage(team_b.team_id, venue.venue_id if venue else None, match_format)
        
        # Pillar 1 & 3: Recent Form & Player Index (40% Weight)
        team_a_squad = self.get_team_squad(team_a.team_id, match_format)
        team_b_squad = self.get_team_squad(team_b.team_id, match_format)
        
        pfi_adv_a = sum([p['pfi'] / 100 for p in team_a_squad]) / len(team_a_squad) if team_a_squad else 0.5
        pfi_adv_b = sum([p['pfi'] / 100 for p in team_b_squad]) / len(team_b_squad) if team_b_squad else 0.5
        
        momentum_a = self.get_recent_team_momentum(team_a.team_id, match_format)
        momentum_b = self.get_recent_team_momentum(team_b.team_id, match_format)
        
        # Form = 50% Squad Strength (PFI) + 50% Win Momentum
        form_adv_a = (pfi_adv_a * 0.5) + (momentum_a * 0.5)
        form_adv_b = (pfi_adv_b * 0.5) + (momentum_b * 0.5)
        
        # Top Performers for UI
        top_performers_a = self.get_top_performers_from_recent_match(team_a.team_id, match_format)
        top_performers_b = self.get_top_performers_from_recent_match(team_b.team_id, match_format)
        
        # Combined Score Calculation (H2H 45%, Venue 15%, Form 40%)
        final_score_a = (h2h_adv * 0.45) + (venue_adv_a * 0.15) + (form_adv_a * 0.40)
        final_score_b = ((1-h2h_adv) * 0.45) + (venue_adv_b * 0.15) + (form_adv_b * 0.40)
        
        total = final_score_a + final_score_b
        win_prob_a = round((final_score_a / total) * 100, 2)
        win_prob_b = round((final_score_b / total) * 100, 2)
        
        # Fetch logo paths
        from sqlalchemy import text
        logo_a = self.db.execute(text("SELECT logo_path FROM teams WHERE team_id = :tid"), {"tid": team_a.team_id}).scalar()
        logo_b = self.db.execute(text("SELECT logo_path FROM teams WHERE team_id = :tid"), {"tid": team_b.team_id}).scalar()

        return {
            "prediction": team_a_name if win_prob_a > 50 else team_b_name,
            "win_probability": f"{win_prob_a}%" if win_prob_a > 50 else f"{win_prob_b}%",
            "confidence": "Extreme (Last 5 H2H + Team Momentum)",
            "team_a": {
                "name": team_a.name,
                "squad": team_a_squad,
                "venue_adv": f"{round(venue_adv_a * 100)}%",
                "form_adv": f"{round(form_adv_a * 100)}%",
                "momentum": f"{round(momentum_a * 100)}%",
                "logo_path": logo_a,
                "top_performers": top_performers_a
            },
            "team_b": {
                "name": team_b.name,
                "squad": team_b_squad,
                "venue_adv": f"{round(venue_adv_b * 100)}%",
                "form_adv": f"{round(form_adv_b * 100)}%",
                "momentum": f"{round(momentum_b * 100)}%",
                "logo_path": logo_b,
                "top_performers": top_performers_b
            },
            "h2h": h2h_stats,
            "venue": {
                "name": venue.name if venue else "Unknown",
                "city": venue.city if venue else "Unknown"
            }
        }


    def get_detailed_h2h_matches(self, team_a_name, team_b_name, match_format='IPL', limit=5):
        def find_team(name, fmt):
            name = get_canonical_team_name(name)
            team = self.db.query(Team).filter(Team.name == name).first()
            if team: return team
            ttype = 'Franchise' if fmt == 'IPL' else 'International'
            team = self.db.query(Team).filter(Team.name.ilike(f"%{name}%"), Team.team_type == ttype).first()
            if team: return team
            return self.db.query(Team).filter(Team.name.ilike(f"%{name}%")).first()

        team_a = find_team(team_a_name, match_format)
        team_b = find_team(team_b_name, match_format)
        
        if not team_a or not team_b:
            return {"error": "Teams not found"}, 404
            
        h2h_matches = (
            self.db.query(Match)
            .filter(Match.format == match_format)
            .filter(
                or_(
                    and_(Match.team_a_id == team_a.team_id, Match.team_b_id == team_b.team_id),
                    and_(Match.team_a_id == team_b.team_id, Match.team_b_id == team_a.team_id)
                )
            )
            .order_by(desc(Match.date))
            .limit(limit)
            .all()
        )
        
        results = [self._format_match_details(m.match_id) for m in h2h_matches]
        return results

    def _format_match_details(self, match_id):
        match = self.db.query(Match).filter_by(match_id=match_id).first()
        if not match: return None
        
        t1 = self.db.query(Team).filter_by(team_id=match.team_a_id).first()
        t2 = self.db.query(Team).filter_by(team_id=match.team_b_id).first()
        venue = self.db.query(Venue).filter_by(venue_id=match.venue_id).first()
        winner = self.db.query(Team).filter_by(team_id=match.winner_id).first() if match.winner_id else None
        toss_winner = self.db.query(Team).filter_by(team_id=match.toss_winner_id).first() if match.toss_winner_id else None
        
        runs_1 = self.db.query(func.sum(Delivery.runs_off_bat + Delivery.extras)).filter_by(match_id=match.match_id, batting_team_id=t1.team_id).scalar() or 0
        wkt_1 = self.db.query(func.count(Delivery.player_dismissed_id)).filter_by(match_id=match.match_id, batting_team_id=t1.team_id).scalar() or 0
        
        runs_2 = self.db.query(func.sum(Delivery.runs_off_bat + Delivery.extras)).filter_by(match_id=match.match_id, batting_team_id=t2.team_id).scalar() or 0
        wkt_2 = self.db.query(func.count(Delivery.player_dismissed_id)).filter_by(match_id=match.match_id, batting_team_id=t2.team_id).scalar() or 0
        
        # Calculate overs logic
        def get_overs(t_id):
            balls = self.db.query(Delivery.over, func.max(Delivery.ball)).filter_by(match_id=match.match_id, batting_team_id=t_id).group_by(Delivery.over).all()
            if not balls: return "0.0"
            comp_overs = len(balls) - 1
            last_over_balls = balls[-1][1]
            if last_over_balls >= 6:
                return f"{comp_overs + 1}.0"
            return f"{comp_overs}.{last_over_balls}"
            
        overs_1 = get_overs(t1.team_id)
        overs_2 = get_overs(t2.team_id)

        # Top Batsmen
        top_batsmen = (
            self.db.query(
                Player.name,
                func.sum(Delivery.runs_off_bat).label('runs'),
                func.count(Delivery.delivery_id).label('balls')
            )
            .join(Delivery, Player.player_id == Delivery.batsman_id)
            .filter(Delivery.match_id == match.match_id)
            .group_by(Player.name)
            .order_by(desc('runs'))
            .limit(3)
            .all()
        )
        
        # Top Bowlers
        top_bowlers = (
            self.db.query(
                Player.name,
                func.count(Delivery.player_dismissed_id).label('wickets'),
                func.sum(Delivery.runs_off_bat + Delivery.extras).label('runs_conceded')
            )
            .join(Delivery, Player.player_id == Delivery.bowler_id)
            .filter(Delivery.match_id == match.match_id)
            .group_by(Player.name)
            .order_by(desc('wickets'), ('runs_conceded'))
            .limit(3)
            .all()
        )

        return {
            "match_title": f"{t1.name} vs {t2.name}",
            "date": match.date.strftime("%Y-%m-%d"),
            "venue": venue.name if venue else "Unknown Venue",
            "toss_winner": toss_winner.name if toss_winner else "N/A",
            "toss_decision": match.toss_decision.title() if match.toss_decision else "N/A",
            "result": match.win_margin if match.win_margin and (winner.name.lower() in match.win_margin.lower()) else (f"{winner.name} won by {match.win_margin}" if winner and match.win_margin else (f"Winner: {winner.name}" if winner else "No Result")),
            "winner_logo": winner.logo_path if winner else None,
            "scoreboard": [
                {"team": t1.short_name or t1.name, "logo": t1.logo_path, "runs": runs_1, "wickets": wkt_1, "overs": overs_1},
                {"team": t2.short_name or t2.name, "logo": t2.logo_path, "runs": runs_2, "wickets": wkt_2, "overs": overs_2}
            ],
            "top_batsmen": [{"name": b.name, "runs": b.runs, "balls": b.balls} for b in top_batsmen],
            "top_bowlers": [{"name": b.name, "wickets": b.wickets, "runs": b.runs_conceded} for b in top_bowlers]
        }
    def get_team_last_match(self, team_name, match_format):
        # Smart Team Lookup
        def find_team(name, fmt):
            name = get_canonical_team_name(name)
            team = self.db.query(Team).filter(Team.name == name).first()
            if team: return team
            ttype = 'Franchise' if fmt == 'IPL' else 'International'
            team = self.db.query(Team).filter(Team.name.ilike(f"%{name}%"), Team.team_type == ttype).first()
            if team: return team
            return self.db.query(Team).filter(Team.name.ilike(f"%{name}%")).first()
            
        team = find_team(team_name, match_format)
        if not team: return None
        
        last_match = self.db.query(Match).filter(
            (Match.team_a_id == team.team_id) | (Match.team_b_id == team.team_id)
        ).filter(Match.format.ilike(match_format)).order_by(desc(Match.date)).first()
        
        if not last_match: return None
        
        team_a = self.db.query(Team).filter(Team.team_id == last_match.team_a_id).first()
        team_b = self.db.query(Team).filter(Team.team_id == last_match.team_b_id).first()
        venue = self.db.query(Venue).filter(Venue.venue_id == last_match.venue_id).first()
        winner = self.db.query(Team).filter(Team.team_id == last_match.winner_id).first()
        
        # Team scores
        from sqlalchemy import func
        scores = self.db.query(
            Delivery.batting_team_id,
            func.sum(Delivery.runs_off_bat + Delivery.extras).label("total"),
            func.count(Delivery.player_dismissed_id).label("wkts"),
            func.max(Delivery.over).label("overs")
        ).filter(Delivery.match_id == last_match.match_id).group_by(Delivery.batting_team_id).all()
        
        scoreboard = []
        for s in scores:
            team_obj = self.db.query(Team).filter(Team.team_id == s.batting_team_id).first()
            t_name = team_obj.name if team_obj else f"Unknown Team ({s.batting_team_id})"
            
            balls_in_last_over = self.db.query(Delivery).filter(
                Delivery.match_id == last_match.match_id, 
                Delivery.batting_team_id == s.batting_team_id, 
                Delivery.over == s.overs
            ).count()
            
            # Simple over calculation
            ov = s.overs if s.overs is not None else 0
            if balls_in_last_over >= 6:
                overs_str = f"{ov+1}.0"
            elif balls_in_last_over > 0:
                overs_str = f"{ov}.{balls_in_last_over}"
            else:
                overs_str = f"{ov}.0"
            
            scoreboard.append({
                "team": t_name,
                "logo": team_obj.logo_path if team_obj else None,
                "runs": int(s.total) if s.total else 0,
                "wickets": int(s.wkts) if s.wkts is not None else 0,
                "overs": overs_str
            })
            
        # Top Batsmen for the requested team
        top_batsmen_records = self.db.query(
            Delivery.batsman_id,
            func.sum(Delivery.runs_off_bat).label("runs"),
            func.count(Delivery.delivery_id).label("balls")
        ).filter(
            Delivery.match_id == last_match.match_id,
            Delivery.batting_team_id == team.team_id,
            Delivery.batsman_id.isnot(None) # Safety for null IDs
        ).group_by(Delivery.batsman_id).order_by(desc("runs")).limit(3).all()
        
        top_batsmen = []
        for tb in top_batsmen_records:
            player = self.db.query(Player).filter(Player.player_id == tb.batsman_id).first()
            if not player: continue
            
            p_name = player.name
            sr = round((tb.runs / tb.balls) * 100, 1) if tb.balls > 0 else 0
            top_batsmen.append({"name": p_name, "runs": int(tb.runs), "balls": tb.balls, "sr": sr})

        # Top Bowlers for the requested team
        top_bowlers_records = self.db.query(
            Delivery.bowler_id,
            func.count(Delivery.player_dismissed_id).label("wickets"),
            func.sum(Delivery.runs_off_bat + Delivery.extras).label("runs_conceded")
        ).filter(
            Delivery.match_id == last_match.match_id,
            Delivery.bowling_team_id == team.team_id,
            Delivery.bowler_id.isnot(None) # Safety for null IDs
        ).group_by(Delivery.bowler_id).order_by(desc("wickets"), "runs_conceded").limit(3).all()
        
        top_bowlers = []
        for tb in top_bowlers_records:
            player = self.db.query(Player).filter(Player.player_id == tb.bowler_id).first()
            if not player: continue
            
            p_name = player.name
            overs_bowled_balls = self.db.query(func.count(Delivery.delivery_id)).filter(
                Delivery.match_id == last_match.match_id,
                Delivery.bowler_id == tb.bowler_id
            ).scalar() or 0
            overs_bowled = overs_bowled_balls // 6
            top_bowlers.append({"name": p_name, "wickets": tb.wickets, "runs": int(tb.runs_conceded), "overs": max(1, overs_bowled)})

        return {
            "match_title": f"{team_a.name if team_a else 'Unknown'} vs {team_b.name if team_b else 'Unknown'}",
            "date": str(last_match.date),
            "venue": f"{venue.name}, {venue.city}" if venue else "Unknown",
            "result": last_match.win_margin if last_match.win_margin and (winner.name.lower() in last_match.win_margin.lower()) else (f"{winner.name} won by {last_match.win_margin}" if winner and last_match.win_margin else (f"{winner.name} won" if winner else "Match result unknown")),
            "winner_logo": winner.logo_path if winner else None,
            "scoreboard": scoreboard,
            "top_batsmen": top_batsmen if top_batsmen else [{"name": "Data unavailable", "runs": 0, "balls": 0, "sr": 0}],
            "top_bowlers": top_bowlers if top_bowlers else [{"name": "Data unavailable", "wickets": 0, "runs": 0, "overs": 0}]
        }


if __name__ == "__main__":
    db = SessionLocal()
    scorer = MatchScorer(db)
    
    # Example Prediction: Royal Challengers Bangalore vs Chennai Super Kings
    result = scorer.predict_match("Royal Challengers Bangalore", "Chennai Super Kings", "M.Chinnaswamy Stadium", "IPL")
    print("--- CricPredict Output ---")
    print(result)
    
    db.close()
