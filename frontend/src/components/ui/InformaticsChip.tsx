import React from 'react';
import { cn } from '@/lib/utils';

interface InformaticsChipProps {
  label: string;
  value?: string | number;
  icon?: React.ReactNode;
  active?: boolean;
  className?: string;
  variant?: 'emerald' | 'carbon';
}

export const InformaticsChip: React.FC<InformaticsChipProps> = ({
  label,
  value,
  icon,
  active = false,
  className,
  variant = 'carbon',
}) => {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-medium tracking-wider uppercase border",
        "font-space-grotesk transition-all duration-300",
        variant === 'emerald' 
          ? "bg-primary/20 border-primary text-primary shadow-[0_0_15px_rgba(16,185,129,0.2)]" 
          : "bg-black/40 border-white/10 text-muted-foreground hover:border-primary/40",
          active && "border-primary text-primary",
        className
      )}
    >
      {active && (
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-primary"></span>
        </span>
      )}
      {icon && <span className="text-current opacity-70">{icon}</span>}
      <span className="opacity-70">{label}</span>
      {value !== undefined && (
        <span className={cn(
          "ml-1 font-bold",
          variant === 'emerald' ? "text-primary" : "text-foreground"
        )}>
          {value}
        </span>
      )}
    </div>
  );
};
