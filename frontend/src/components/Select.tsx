"use client";

import { useState, useEffect, useRef } from "react";

interface SelectProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    options: { value: string; label: string }[] | string[];
    placeholder?: string;
    disabled?: boolean;
}

export default function Select({ label, value, onChange, options, placeholder, disabled }: SelectProps) {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSelect = (val: string) => {
        onChange(val);
        setIsOpen(false);
    };

    const displayOptions = options.map(opt =>
        typeof opt === 'string' ? { value: opt, label: opt } : opt
    );

    const selectedOption = displayOptions.find(opt => opt.value === value);

    return (
        <div className="relative w-full" ref={containerRef}>
            <label className="block text-[10px] font-bold text-muted uppercase tracking-[0.2em] mb-3">{label}</label>
            <div
                onClick={() => !disabled && setIsOpen(!isOpen)}
                className={`w-full bg-surface-elevated border border-border-subtle rounded-xl p-3 outline-none transition-all cursor-pointer flex justify-between items-center gap-2 group ${isOpen ? 'border-gold/50' : 'hover:border-white/20'} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
                <span className={`text-sm truncate ${!value ? 'text-muted' : 'text-white'}`}>
                    {selectedOption ? selectedOption.label : placeholder || 'Select option'}
                </span>
                <span className={`text-muted shrink-0 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}>
                    <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 1L5 5L9 1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </span>
            </div>

            {isOpen && (
                <ul className="absolute z-[100] w-full mt-2 bg-surface-elevated border border-border-subtle rounded-xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar animate-fade-in shadow-black/80">
                    {displayOptions.length === 0 ? (
                        <li className="p-3 text-xs text-muted italic">No options available</li>
                    ) : (
                        displayOptions.map((opt, index) => (
                            <li
                                key={index}
                                onClick={() => handleSelect(opt.value)}
                                className={`p-3 text-sm transition-colors border-b border-border-subtle/50 last:border-0 cursor-pointer truncate ${opt.value === value ? 'bg-gold/10 text-gold' : 'hover:bg-white/5 text-white'}`}
                                title={opt.label}
                            >
                                {opt.label}
                            </li>
                        ))
                    )}
                </ul>
            )}
        </div>
    );
}
