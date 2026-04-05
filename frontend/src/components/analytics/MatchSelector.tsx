import * as React from "react"
import { cn } from "@/lib/utils"
import Autocomplete from "@/components/Autocomplete"
import Select from "@/components/Select"
import { searchTeams } from "@/lib/api"

interface MatchSelectorProps {
  format: string;
  setFormat: (v: string) => void;
  teamA: string;
  setTeamA: (v: string) => void;
  teamB: string;
  setTeamB: (v: string) => void;
  country: string;
  setCountry: (v: string) => void;
  countries: string[];
  venue: string;
  setVenue: (v: string) => void;
  venues: string[];
  loading: boolean;
  handlePredict: () => void;
}

export function MatchSelector({
  format, setFormat,
  teamA, setTeamA,
  teamB, setTeamB,
  country, setCountry, countries,
  venue, setVenue, venues,
  loading, handlePredict
}: MatchSelectorProps) {
  return (
    <div className="w-full rounded-[2rem] border border-white/5 glass-carbon p-10 shadow-[0_32px_64px_rgba(0,0,0,0.5)] relative group">
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary to-transparent opacity-30 group-hover:opacity-100 transition-opacity duration-1000" />
      
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-end">
        {/* Format & Teams */}
        <div className="lg:col-span-2">
          <Select
            label="Match Format"
            value={format}
            onChange={(val) => {
              setFormat(val);
              if (val === "IPL") {
                setCountry("India");
              }
            }}
            options={[
              { value: "IPL", label: "IPL" },
              { value: "T20I", label: "T20 International" },
              { value: "ODI", label: "One Day International" },
              { value: "Tests", label: "Test Match" }
            ]}
          />
        </div>

        <div className="lg:col-span-3">
          <Autocomplete
            label="Home Team"
            value={teamA}
            onChange={setTeamA}
            onSearch={(q) => searchTeams(q, format)}
            placeholder="Search team..."
          />
        </div>

        <div className="lg:col-span-1 border-none flex flex-col items-center justify-center pb-4 h-full opacity-10">
          <span className="font-space-grotesk text-3xl font-black text-white italic">VS</span>
        </div>

        <div className="lg:col-span-3">
          <Autocomplete
            label="Away Team"
            value={teamB}
            onChange={setTeamB}
            onSearch={(q) => searchTeams(q, format)}
            placeholder="Search team..."
          />
        </div>

        <div className="lg:col-span-3">
          <button
            onClick={handlePredict}
            disabled={loading}
            className="w-full py-5 rounded-2xl font-inter text-base font-black tracking-[0.2em] uppercase text-white bg-primary hover:bg-primary/90 shadow-[0_0_40px_rgba(16,185,129,0.5)] border border-primary/20 active:scale-[0.98] transition-all disabled:opacity-50 relative group/btn"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white animate-spin rounded-full" />
                ANALYZING...
              </span>
            ) : "ANALYZE"}
          </button>
        </div>

        {/* Location & Stadium */}
        <div className="lg:col-span-3">
          <Select
            label="Country"
            value={country}
            onChange={setCountry}
            options={countries}
            placeholder="Select Country"
          />
        </div>

        <div className="lg:col-span-4">
          <Autocomplete
            label="Stadium"
            value={venue}
            onChange={setVenue}
            onSearch={async (q) => venues.filter(v => v.toLowerCase().includes(q.toLowerCase()))}
            placeholder="Search Stadium..."
          />
        </div>

        <div className="lg:col-span-5">
        </div>
      </div>
    </div>
  )
}
