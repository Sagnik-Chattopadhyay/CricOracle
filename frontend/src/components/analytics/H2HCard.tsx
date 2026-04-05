import * as React from "react"
import { cn } from "@/lib/utils"
import { type PredictionData } from "@/lib/api"
import { AnalyticsCard } from "./AnalyticsCard"
import { getTeamTheme } from "@/lib/themes"

interface H2HCardProps {
  h2h: PredictionData['h2h'];
  teamA: string;
  teamB: string;
  previewMatches: any[];
  getTeamFlag: (name: string, size?: "sm" | "lg") => React.ReactNode;
  format: string;
}

export function H2HCard({ h2h, teamA, teamB, previewMatches, getTeamFlag, format }: H2HCardProps) {
  const teamAWins = h2h.team_a_wins;
  const teamBWins = h2h.team_b_wins;
  const total = h2h.total;

  const themeA = getTeamTheme(teamA);
  const themeB = getTeamTheme(teamB);
  
  return (
    <AnalyticsCard title="HISTORICAL RIVALRY" className="col-span-full">
      <div className="flex flex-col gap-16 py-8">
        
        {/* Head to Head Main Stats */}
        <div className="flex justify-between items-center px-12 md:px-24">
          <div className="flex flex-col items-center gap-6">
            <div 
              className="bg-black/60 p-6 rounded-full border shadow-2xl transition-all duration-500 hover:scale-110"
              style={{ borderColor: `${themeA.primary}40`, boxShadow: `0 0 40px ${themeA.primary}15` }}
            >
              {getTeamFlag(teamA, "lg")}
            </div>
            <div className="text-center">
              {/* Team name removed for logo-only display */}
              <span 
                className="font-space-grotesk text-8xl font-black tracking-tighter"
                style={{ color: themeA.primary }}
              >
                {teamAWins}
              </span>
              <span className="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] block mt-1">WINS</span>
            </div>
          </div>

          <div className="flex flex-col items-center gap-8">
            <div className="w-[1px] h-24 bg-gradient-to-b from-transparent via-white/10 to-transparent" />
            <div className="font-space-grotesk text-4xl font-black text-white/5 italic select-none">VS</div>
            <div className="flex flex-col items-center gap-1">
              <span className="text-[10px] font-black text-white/20 tracking-[0.5em] uppercase">MATCHES</span>
              <span className="font-space-grotesk text-2xl font-black text-white italic">{total}</span>
            </div>
            <div className="w-[1px] h-24 bg-gradient-to-b from-transparent via-white/10 to-transparent" />
          </div>

          <div className="flex flex-col items-center gap-6">
            <div 
              className="bg-black/60 p-6 rounded-full border shadow-2xl transition-all duration-500 hover:scale-110"
              style={{ borderColor: `${themeB.primary}40`, boxShadow: `0 0 40px ${themeB.primary}15` }}
            >
              {getTeamFlag(teamB, "lg")}
            </div>
            <div className="text-center">
              {/* Team name removed for logo-only display */}
              <span 
                className="font-space-grotesk text-8xl font-black tracking-tighter"
                style={{ color: themeB.primary }}
              >
                {teamBWins}
              </span>
              <span className="text-[10px] font-black text-white/20 uppercase tracking-[0.3em] block mt-1">WINS</span>
            </div>
          </div>
        </div>

        {/* Recent Engagements */}
        <div className="flex flex-col gap-8">
          <div className="flex items-center gap-3 px-2">
            <div className="h-[1px] w-12 bg-white/20" />
            <span className="font-space-grotesk text-[10px] font-black text-white/40 uppercase tracking-[0.6em]">Historical Archive</span>
            <div className="h-[1px] w-12 bg-white/20" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {previewMatches.length > 0 ? (
              previewMatches.slice(0, 3).map((match, i) => (
                <div key={i} className="group relative p-8 rounded-[2rem] bg-white/[0.02] border border-white/5 transition-all duration-500 hover:border-white/20 hover:bg-white/[0.04]">
                  <div className="flex justify-between items-start mb-6">
                    <span className="font-mono text-[9px] text-white/20 uppercase tracking-widest font-black">{match.date}</span>
                    <span className="text-[10px] font-black text-white/40 tracking-widest uppercase">{format}</span>
                  </div>
                  
                  <div className="flex flex-col gap-6">
                    <div className="flex flex-col gap-4">
                      {match.scoreboard.map((sb: any, idx: number) => (
                        <div key={idx} className="flex justify-between items-center">
                          <img src={sb.logo} alt={sb.team} className="w-8 h-8 object-contain" title={sb.team} />
                          <span className="font-space-grotesk text-lg font-black text-white italic">{sb.runs}/{sb.wickets}</span>
                        </div>
                      ))}
                    </div>
                    
                    <div className="pt-6 border-t border-white/5 flex items-center justify-between">
                       <div className="flex items-center gap-3">
                          <img src={match.winner_logo} alt="Winner" className="w-6 h-6 object-contain" />
                          <span className="font-space-grotesk text-[10px] font-black text-white/60 uppercase tracking-tight italic">
                            {match.result.replace(teamA, "").replace(teamB, "").replace("won by", "win by").trim()}
                          </span>
                       </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full py-16 flex flex-col items-center gap-4 rounded-[2rem] bg-white/[0.01] border border-white/5 border-dashed">
                <div className="w-6 h-6 rounded-full border-2 border-white/5 border-t-white/30 animate-spin" />
                <span className="text-[9px] text-white/20 uppercase tracking-[0.6em] font-black">Syncing_Archive_Vector</span>
              </div>
            )}
          </div>
        </div>

      </div>
    </AnalyticsCard>
  )
}
