import * as React from "react"
import { cn } from "@/lib/utils"
import { type PlayerForm } from "@/lib/api"
import { InformaticsChip } from "../ui/InformaticsChip"

interface PlayerRowProps {
  player: PlayerForm;
  theme: { primary: string };
}

export function PlayerRow({ player, theme }: PlayerRowProps) {
  const [isHovered, setIsHovered] = React.useState(false);
  const pfi = player.pfi;
  const isHot = pfi >= 80;
  
  return (
    <div 
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={cn(
        "flex flex-col gap-3 p-4 rounded-xl border border-white/5 glass-carbon transition-all duration-300 group",
        pfi < 40 && "opacity-60 grayscale-[0.3]"
      )}
      style={{ 
        borderColor: isHovered ? `${theme.primary}50` : undefined,
        boxShadow: isHovered ? `0 0 20px ${theme.primary}15` : undefined
      }}
    >
      <div className="flex justify-between items-start">
        <div className="flex flex-col gap-1">
          <span 
            className="font-space-grotesk text-[13px] font-bold text-white transition-colors tracking-tight uppercase"
            style={{ color: isHovered ? theme.primary : undefined }}
          >
            {player.name}
          </span>
          <InformaticsChip 
            label={player.role || 'ASSET'} 
            variant="carbon" 
            className="px-2 py-0 h-4 border-none bg-white/5 text-[8px]" 
          />
        </div>
        <div 
          className={cn(
            "font-space-grotesk text-sm font-black",
            !isHot && "text-white/60"
          )}
          style={{ 
            color: isHot || isHovered ? theme.primary : undefined,
            textShadow: isHot || isHovered ? `0 0 10px ${theme.primary}80` : undefined 
          }}
        >
          {pfi.toFixed(0)}
        </div>
      </div>
      
      <div className="w-full h-[6px] bg-black/40 rounded-full overflow-hidden border border-white/[0.03]">
        <div
          className="h-full transition-all duration-1000 rounded-full"
          style={{ 
            width: `${Math.min(100, (pfi / 120) * 100)}%`,
            backgroundColor: isHot || isHovered ? theme.primary : 'rgba(255,255,255,0.2)',
            boxShadow: isHot || isHovered ? `0 0 10px ${theme.primary}99` : undefined
          }}
        />
      </div>
    </div>
  );
}
