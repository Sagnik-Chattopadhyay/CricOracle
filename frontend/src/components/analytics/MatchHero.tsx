import * as React from "react"
import { cn } from "@/lib/utils"
import { type PredictionData } from "@/lib/api"
import { AnalyticsCard } from "./AnalyticsCard"
import { getTeamTheme } from "@/lib/themes"

interface MatchHeroProps {
  prediction: PredictionData;
  teamA: string;
  teamB: string;
  getTeamFlag: (name: string, size?: "sm" | "lg") => React.ReactNode;
}

// Helper removed as theme engine is now centralized

export function MatchHero({ prediction, teamA, teamB, getTeamFlag }: MatchHeroProps) {
  const winProb = parseFloat(prediction.win_probability || "50");
  const winner = prediction.prediction;
  const isTeamAWinner = winner === teamA;
  
  // Calculate probability for Team A specifically
  const teamAProb = isTeamAWinner ? winProb : (100 - winProb);

  const themeA = getTeamTheme(teamA);
  const themeB = getTeamTheme(teamB);
  
  return (
    <AnalyticsCard className="col-span-full" title="WIN PROBABILITY" themeColor={themeA.primary}>
      <div className="relative flex flex-col items-center gap-16 py-12">
        
        <div className="w-full flex flex-col md:flex-row items-center justify-between gap-12 md:gap-24">
          {/* Team A Panel */}
          <div className="flex-1 flex flex-col items-center gap-8">
            <div 
              className="relative p-2 rounded-full transition-all duration-700 shadow-2xl"
              style={{ backgroundColor: `${themeA.primary}15`, border: `1px solid ${themeA.primary}30` }}
            >
              <div className="p-4 bg-black/40 rounded-full">
                {getTeamFlag(teamA, "lg")}
              </div>
            </div>
            <div className="text-center">
              {/* Team name removed for logo-only display */}
              <div 
                className="font-space-grotesk text-7xl font-black tracking-tighter"
                style={{ color: themeA.primary }}
              >
                {teamAProb.toFixed(1)}<span className="text-2xl ml-1 opacity-40">%</span>
              </div>
            </div>
          </div>

          {/* Central Probability Core */}
          <div className="flex flex-col items-center gap-10 w-full md:w-[480px]">
            <div className="h-4" /> {/* Spacer */}

            <div className="relative w-full h-4 bg-white/5 rounded-full overflow-hidden border border-white/5">
              <div 
                className="absolute inset-y-0 left-0 transition-all duration-1000 ease-out z-10"
                style={{ width: `${teamAProb}%`, backgroundColor: themeA.primary }}
              />
              <div 
                className="absolute inset-y-0 right-0 transition-all duration-1000 ease-out"
                style={{ width: `${100 - teamAProb}%`, backgroundColor: themeB.primary }}
              />
              <div 
                className="absolute top-0 bottom-0 w-1 bg-white z-20 shadow-[0_0_20px_white]" 
                style={{ left: `${teamAProb}%`, marginLeft: '-2px' }} 
              />
            </div>

            <div className="h-4" /> {/* Spacer */}
          </div>

          {/* Team B Panel */}
          <div className="flex-1 flex flex-col items-center gap-8">
            <div 
              className="relative p-2 rounded-full transition-all duration-700 shadow-2xl"
              style={{ backgroundColor: `${themeB.primary}15`, border: `1px solid ${themeB.primary}30` }}
            >
              <div className="p-4 bg-black/40 rounded-full">
                {getTeamFlag(teamB, "lg")}
              </div>
            </div>
            <div className="text-center">
              {/* Team name removed for logo-only display */}
              <div 
                className="font-space-grotesk text-7xl font-black tracking-tighter"
                style={{ color: themeB.primary }}
              >
                {(100 - teamAProb).toFixed(1)}<span className="text-2xl ml-1 opacity-40">%</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </AnalyticsCard>
  )
}
