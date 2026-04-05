import * as React from "react"
import { cn } from "@/lib/utils"
import { type TeamInfo } from "@/lib/api"
import { AnalyticsCard } from "./AnalyticsCard"
import { PlayerRow } from "./PlayerRow"
import { getTeamTheme } from "@/lib/themes"

interface SquadIntelligenceProps {
  teamA: TeamInfo;
  teamB: TeamInfo;
  getTeamFlag: (name: string, size?: "sm" | "lg") => React.ReactNode;
  fetchScoreboard: (team: string) => void;
}

export function SquadIntelligence({ teamA, teamB, getTeamFlag, fetchScoreboard }: SquadIntelligenceProps) {
  const themeA = getTeamTheme(teamA.name);
  const themeB = getTeamTheme(teamB.name);

  return (
    <AnalyticsCard title="SQUAD INTELLIGENCE" className="col-span-full">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
        {/* Team A */}
        <div className="flex flex-col gap-10">
          <div 
            className="flex justify-between items-center p-8 rounded-[2rem] bg-white/[0.03] border border-white/5 transition-all duration-500 hover:border-white/20 shadow-2xl"
            style={{ boxShadow: `inset 0 0 30px ${themeA.primary}08` }}
          >
            <div className="flex items-center gap-6">
              <div 
                className="bg-black/60 p-4 rounded-full border shadow-xl"
                style={{ borderColor: `${themeA.primary}40` }}
              >
                {getTeamFlag(teamA.name, "lg")}
              </div>
              {/* Team name removed for logo-only display */}
            </div>
            <div className="flex gap-10">
              <div className="text-right">
                <div className="text-[10px] text-white/20 uppercase tracking-[0.4em] font-black mb-1">MOMENTUM</div>
                <div 
                  className="text-4xl font-black tracking-tighter"
                  style={{ color: themeA.primary }}
                >
                  {teamA.momentum || "0%"}
                </div>
              </div>
              <div className="text-right pl-10 border-l border-white/5">
                <div className="text-[10px] text-white/20 uppercase tracking-[0.4em] font-black mb-1">UNIT_PFI</div>
                <div className="text-4xl font-black tracking-tighter text-white/80">{teamA.form_adv}</div>
              </div>
            </div>
          </div>
          
          {/* Top Performers A */}
          {teamA.top_performers && teamA.top_performers.length > 0 && (
            <div className="p-8 rounded-[2rem] bg-white/[0.02] border border-white/5 flex flex-col gap-6">
               <div 
                className="text-[10px] font-black uppercase tracking-[0.5em] flex items-center gap-3"
                style={{ color: themeA.primary }}
               >
                 <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: themeA.primary }} />
                 TOP PERFORMERS
               </div>
               <div className="grid grid-cols-2 gap-6">
                 {teamA.top_performers.map((p, i) => (
                   <div key={i} className="flex flex-col gap-1 group">
                      <span className="text-sm text-white font-black tracking-tight group-hover:text-primary transition-colors">{p.name}</span>
                      <span className="font-mono text-[9px] text-white/20 uppercase tracking-widest">{p.role} // {p.stat}</span>
                   </div>
                 ))}
               </div>
            </div>
          )}
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {teamA.squad.map((player) => (
              <PlayerRow key={player.name} player={player} theme={themeA} />
            ))}
          </div>
          
          <button 
            onClick={() => fetchScoreboard(teamA.name)}
            className="w-full py-6 rounded-2xl border border-white/5 bg-white/[0.02] text-[10px] font-black tracking-[0.5em] uppercase text-white/30 hover:text-white hover:bg-white/5 transition-all active:scale-[0.98]"
          >
            LAST MATCH
          </button>
        </div>

        {/* Team B */}
        <div className="flex flex-col gap-10">
          <div 
            className="flex justify-between items-center p-8 rounded-[2rem] bg-white/[0.03] border border-white/5 transition-all duration-500 hover:border-white/20 shadow-2xl"
            style={{ boxShadow: `inset 0 0 30px ${themeB.primary}08` }}
          >
            <div className="flex items-center gap-6">
              <div 
                className="bg-black/60 p-4 rounded-full border shadow-xl"
                style={{ borderColor: `${themeB.primary}40` }}
              >
                {getTeamFlag(teamB.name, "lg")}
              </div>
              {/* Team name removed for logo-only display */}
            </div>
            <div className="flex gap-10">
              <div className="text-right">
                <div className="text-[10px] text-white/20 uppercase tracking-[0.4em] font-black mb-1">MOMENTUM</div>
                <div 
                  className="text-4xl font-black tracking-tighter"
                  style={{ color: themeB.primary }}
                >
                  {teamB.momentum || "0%"}
                </div>
              </div>
              <div className="text-right pl-10 border-l border-white/5">
                <div className="text-[10px] text-white/20 uppercase tracking-[0.4em] font-black mb-1">UNIT_PFI</div>
                <div className="text-4xl font-black tracking-tighter text-white/80">{teamB.form_adv}</div>
              </div>
            </div>
          </div>
          
          {/* Top Performers B */}
          {teamB.top_performers && teamB.top_performers.length > 0 && (
            <div className="p-8 rounded-[2rem] bg-white/[0.02] border border-white/5 flex flex-col gap-6">
               <div 
                className="text-[10px] font-black uppercase tracking-[0.5em] flex items-center gap-3"
                style={{ color: themeB.primary }}
               >
                 <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: themeB.primary }} />
                 TOP PERFORMERS
               </div>
               <div className="grid grid-cols-2 gap-6">
                 {teamB.top_performers.map((p, i) => (
                   <div key={i} className="flex flex-col gap-1 group">
                      <span className="text-sm text-white font-black tracking-tight group-hover:text-primary transition-colors">{p.name}</span>
                      <span className="font-mono text-[9px] text-white/20 uppercase tracking-widest">{p.role} // {p.stat}</span>
                   </div>
                 ))}
               </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {teamB.squad.map((player) => (
              <PlayerRow key={player.name} player={player} theme={themeB} />
            ))}
          </div>
          
          <button 
            onClick={() => fetchScoreboard(teamB.name)}
            className="w-full py-6 rounded-2xl border border-white/5 bg-white/[0.02] text-[10px] font-black tracking-[0.5em] uppercase text-white/30 hover:text-white hover:bg-white/5 transition-all active:scale-[0.98]"
          >
            LAST MATCH
          </button>
        </div>
      </div>
    </AnalyticsCard>
  )
}
