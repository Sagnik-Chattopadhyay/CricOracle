"use client";

import { useState, useEffect, useRef } from "react";

interface AutocompleteProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
    onSearch: (query: string) => Promise<string[]>;
    placeholder?: string;
}

export default function Autocomplete({ label, value, onChange, onSearch, placeholder }: AutocompleteProps) {
    const [suggestions, setSuggestions] = useState<string[]>([]);
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

    const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        onChange(val);
        if (val.length > 1) {
            const results = await onSearch(val);
            setSuggestions(results);
            setIsOpen(true);
        } else {
            setSuggestions([]);
            setIsOpen(false);
        }
    };

    const handleSelect = (suggestion: string) => {
        onChange(suggestion);
        setSuggestions([]);
        setIsOpen(false);
    };

    return (
        <div className="relative w-full" ref={containerRef}>
            <label className="block text-[10px] font-bold text-muted uppercase tracking-[0.2em] mb-3">{label}</label>
            <div className="relative">
                <input
                    type="text"
                    value={value}
                    onChange={handleInputChange}
                    placeholder={placeholder}
                    onFocus={() => value.length > 1 && setIsOpen(true)}
                    className="w-full bg-surface-elevated border border-border-subtle rounded-xl p-3 outline-none focus:border-gold/50 transition-colors text-sm"
                />
            </div>

            {isOpen && suggestions.length > 0 && (
                <ul className="absolute z-[100] w-full mt-2 bg-surface-elevated border border-border-subtle rounded-xl shadow-2xl overflow-hidden max-h-60 overflow-y-auto custom-scrollbar">
                    {suggestions.map((suggestion, index) => (
                        <li
                            key={index}
                            onClick={() => handleSelect(suggestion)}
                            className="p-3 hover:bg-white/5 cursor-pointer transition-colors border-b border-border-subtle/50 last:border-0 text-sm"
                        >
                            {suggestion}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
