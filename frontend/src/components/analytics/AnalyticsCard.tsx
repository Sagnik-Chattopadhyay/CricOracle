import * as React from "react"
import { cn } from "@/lib/utils"

interface AnalyticsCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  subtitle?: string;
  variant?: 'default' | 'elevated' | 'glass';
  themeColor?: string;
}

const AnalyticsCard = React.forwardRef<HTMLDivElement, AnalyticsCardProps>(
  ({ className, title, subtitle, variant = 'glass', themeColor, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "relative rounded-[2.5rem] overflow-hidden transition-all duration-700",
          "hover:shadow-[0_0_80px_rgba(0,0,0,0.4)] group backdrop-blur-[24px]",
          variant === 'glass' && "bg-[#0a0a0a]/40 border border-white/5",
          variant === 'default' && "bg-[#0a0a0a]/60 border border-white/10",
          variant === 'elevated' && "bg-[#0a0a0a]/90 border border-white/20",
          className
        )}
        style={{ 
          boxShadow: themeColor ? `inset 0 0 20px ${themeColor}05` : undefined,
          borderColor: themeColor ? `${themeColor}20` : undefined
        }}
        {...props}
      >
        {/* Liquid Gradient Edge */}
        {themeColor && (
          <div 
            className="absolute -inset-[2px] rounded-[2.5rem] p-[2px] pointer-events-none opacity-20 group-hover:opacity-40 transition-opacity duration-700"
            style={{ 
              background: `linear-gradient(135deg, ${themeColor}, transparent 40%, transparent 60%, ${themeColor})` 
            }}
          />
        )}

        <div className="relative z-10">
          {(title || subtitle) && (
            <div className="px-10 py-8 border-b border-white/5">
              {title && (
                <h3 className="font-space-grotesk font-black text-2xl leading-tight tracking-tight text-white uppercase italic">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="font-space-grotesk text-[10px] text-white/30 mt-2 uppercase tracking-[0.4em] font-bold">
                  {subtitle}
                </p>
              )}
            </div>
          )}
          <div className={cn("px-10 py-10", !title && !subtitle && "p-10")}>
            {children}
          </div>
        </div>
      </div>
    )
  }
)
AnalyticsCard.displayName = "AnalyticsCard"

export { AnalyticsCard }
