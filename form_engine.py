from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import Delivery, Match, Player, PlayerForm
from db import SessionLocal
import datetime

class FormEngine:
    """
    Calculates Player Form Index (PFI) based on weighted recency.
    """
    _pfi_cache = {}
    
    def __init__(self, db: Session):
        self.db = db

    def calculate_pfi(self, player_id, match_format='T20I', window=5):
        """
        Calculates detailed PFI (Batting, Bowling, Total) and derives player role.
        Uses PlayerForm table as a persistent cache.
        """
        cache_key = f"{player_id}_{match_format}_{window}"
        if cache_key in self.__class__._pfi_cache:
            return self.__class__._pfi_cache[cache_key]
            
        # Check DB cache
        db_form = self.db.query(PlayerForm).filter_by(player_id=player_id, format=match_format).first()
        if db_form and db_form.last_updated:
            age = (datetime.datetime.utcnow() - db_form.last_updated).days
            if age < 3: # Use cache if less than 3 days old
                # We store a single score in DB, so we derive a basic result structure
                # This is a simplification; for full data we'd need more columns or JSON
                # For now, let's just return the cached total and assume neutral role
                result = {"batting": db_form.form_score, "bowling": db_form.form_score, "total": db_form.form_score, "role": "All-rounder"}
                self.__class__._pfi_cache[cache_key] = result
                return result

        from sqlalchemy import or_
        matches = (
            self.db.query(Match.match_id)
            .join(Delivery, Match.match_id == Delivery.match_id)
            .filter(Match.format == match_format)
            .filter(or_(Delivery.batsman_id == player_id, Delivery.bowler_id == player_id))
            .group_by(Match.match_id)
            .order_by(desc(Match.date))
            .limit(window)
            .all()
        )
        
        if not matches:
            result = {"batting": 0.0, "bowling": 0.0, "total": 50.0, "role": "Batter"}
            self.__class__._pfi_cache[cache_key] = result
            return result
            
        match_ids = [m[0] for m in matches]
        
        bat_stats = (
            self.db.query(
                Delivery.match_id,
                func.sum(Delivery.runs_off_bat).label('runs'),
                func.count(Delivery.delivery_id).label('balls')
            )
            .filter(Delivery.batsman_id == player_id, Delivery.match_id.in_(match_ids))
            .group_by(Delivery.match_id)
            .all()
        )
        bat_map = {r.match_id: {"runs": r.runs or 0, "balls": r.balls or 0} for r in bat_stats}

        bowl_stats = (
            self.db.query(
                Delivery.match_id,
                func.count(Delivery.delivery_id).label('balls_bowled'),
                func.sum(Delivery.runs_off_bat + Delivery.extras).label('runs_conceded'),
                func.count(Delivery.player_dismissed_id).label('wickets')
            )
            .filter(Delivery.bowler_id == player_id, Delivery.match_id.in_(match_ids))
            .group_by(Delivery.match_id)
            .all()
        )
        bowl_map = {r.match_id: {"balls": r.balls_bowled or 0, "runs": r.runs_conceded or 0, "wickets": r.wickets or 0} for r in bowl_stats}
        
        batting_scores, bowling_scores = [], []
        total_runs, total_balls_bowled = 0, 0
        
        for m_id in match_ids:
            # Batting stat aggregation
            bs = bat_map.get(m_id, {"runs": 0, "balls": 0})
            runs = bs["runs"]
            balls = bs["balls"]
            total_runs += runs
            sr = (runs / balls * 100) if balls > 0 else 0
            batting_scores.append((runs * 1.5) + (sr * 0.3))
            
            # Bowling stat aggregation
            bws = bowl_map.get(m_id, {"balls": 0, "runs": 0, "wickets": 0})
            balls_bowled = bws["balls"]
            total_balls_bowled += balls_bowled
            runs_conceded = bws["runs"]
            wickets = bws["wickets"]
            
            overs = balls_bowled / 6.0
            econ = (runs_conceded / overs) if overs > 0 else 10.0
            bowl_score = (wickets * 30) + (max(0, 10 - econ) * 5) if balls_bowled > 0 else 0
            bowling_scores.append(bowl_score)
            
        weights = [0.4, 0.25, 0.15, 0.1, 0.1][:len(match_ids)]
        total_w = sum(weights)
        weights = [w/total_w for w in weights]
        
        avg_bat = min(100, sum(s * w for s, w in zip(batting_scores, weights)))
        avg_bowl = min(100, sum(s * w for s, w in zip(bowling_scores, weights)))
        
        if total_balls_bowled > 12 and total_runs > 30:
            role = "All-rounder"
        elif total_balls_bowled > 12:
            role = "Bowler"
        else:
            role = "Batter"
            
        total_pfi = (avg_bat * 0.5) + (avg_bowl * 0.5) if role == "All-rounder" else (avg_bat if role == "Batter" else avg_bowl)
        
        result = {
            "batting": round(avg_bat, 1),
            "bowling": round(avg_bowl, 1),
            "total": round(total_pfi, 1) if total_pfi > 0 else 50.0,
            "role": role
        }

        # Save to DB cache
        try:
            db_form = self.db.query(PlayerForm).filter_by(player_id=player_id, format=match_format).first()
            if not db_form:
                db_form = PlayerForm(player_id=player_id, format=match_format)
                self.db.add(db_form)
            db_form.form_score = result["total"]
            db_form.last_updated = datetime.datetime.utcnow()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Warning: Failed to save PFI to DB: {e}")

        self.__class__._pfi_cache[cache_key] = result
        return result

    def update_all_player_forms(self):
        """Pre-calculates PFI for all players and saves to player_form table."""
        # This is a heavy operation, run once a week or on demand.
        players = self.db.query(Player).all()
        formats = ['IPL', 'T20I', 'ODI', 'Tests']
        
        for player in players:
            for fmt in formats:
                pfi = self.calculate_pfi(player.player_id, fmt)
                if pfi > 0:
                    form = self.db.query(PlayerForm).filter_by(player_id=player.player_id, format=fmt).first()
                    if form:
                        form.form_score = pfi
                        form.last_updated = datetime.datetime.utcnow()
                    else:
                        form = PlayerForm(player_id=player.player_id, format=fmt, form_score=pfi)
                        self.db.add(form)
        self.db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    engine = FormEngine(db)
    
    # Test for a known player (e.g., Virat Kohli or MS Dhoni)
    # I'll search for a player ID first
    sample_player = db.query(Player).first()
    if sample_player:
        pfi = engine.calculate_pfi(sample_player.player_id, 'IPL')
        print(f"PFI for {sample_player.name} (IPL): {pfi}")
    
    db.close()
