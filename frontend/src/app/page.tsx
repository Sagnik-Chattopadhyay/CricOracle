"use client";

import { useState, useEffect } from "react";
import {
  getPrediction,
  triggerSync,
  getVenueCountries,
  getVenuesByCountry,
  getLastMatchScoreboard,
  getH2HDetails,
  type PredictionData,
} from "@/lib/api";
import { cn } from "@/lib/utils";

// Modular Analytics Components
import { MatchSelector } from "@/components/analytics/MatchSelector";
import { MatchHero } from "@/components/analytics/MatchHero";
import { H2HCard } from "@/components/analytics/H2HCard";
import { SquadIntelligence } from "@/components/analytics/SquadIntelligence";
import { AnalyticsCard } from "@/components/analytics/AnalyticsCard";
import { InformaticsChip } from "@/components/ui/InformaticsChip";
import { getTeamTheme } from "@/lib/themes";

export default function Home() {
  const [teamA, setTeamA] = useState("");
  const [teamB, setTeamB] = useState("");
  const [country, setCountry] = useState("");
  const [venue, setVenue] = useState("");
  const [format, setFormat] = useState("T20I");
  const [countries, setCountries] = useState<string[]>([]);
  const [venues, setVenues] = useState<string[]>([]);
  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState("");

  const themeA = getTeamTheme(teamA);
  const themeB = getTeamTheme(teamB);

  // Scoreboard Modal State
  const [selectedScoreboard, setSelectedScoreboard] = useState<any>(null);
  const [loadingScoreboard, setLoadingScoreboard] = useState(false);
  const [previewH2H, setPreviewH2H] = useState<any[]>([]);

  // Team logo lookup - maps team names to local logo assets
  const TEAM_LOGOS: Record<string, string> = {
    // IPL Franchises
    "CHENNAI SUPER KINGS": "/assets/logos/ipl/csk.webp",
    "MUMBAI INDIANS": "/assets/logos/ipl/mi.webp",
    "ROYAL CHALLENGERS BENGALURU": "/assets/logos/ipl/rcb.webp",
    "ROYAL CHALLENGERS BANGALORE": "/assets/logos/ipl/rcb.webp",
    "KOLKATA KNIGHT RIDERS": "/assets/logos/ipl/kkr.webp",
    "RAJASTHAN ROYALS": "/assets/logos/ipl/rr.webp",
    "DELHI CAPITALS": "/assets/logos/ipl/dc.webp",
    "PUNJAB KINGS": "/assets/logos/ipl/pbks.webp",
    "SUNRISERS HYDERABAD": "/assets/logos/ipl/srh.webp",
    "GUJARAT TITANS": "/assets/logos/ipl/gt.webp",
    "LUCKNOW SUPER GIANTS": "/assets/logos/ipl/lsg.webp",
    // International Teams
    "INDIA": "/assets/logos/intl/ind.png",
    "AUSTRALIA": "/assets/logos/intl/aus.png",
    "ENGLAND": "/assets/logos/intl/eng.png",
    "NEW ZEALAND": "/assets/logos/intl/nz.png",
    "PAKISTAN": "/assets/logos/intl/pak.png",
    "SOUTH AFRICA": "/assets/logos/intl/sa.png",
    "SRI LANKA": "/assets/logos/intl/sl.png",
    "BANGLADESH": "/assets/logos/intl/ban.png",
    "AFGHANISTAN": "/assets/logos/intl/afg.png",
    "ZIMBABWE": "/assets/logos/intl/zim.png",
    "USA": "/assets/logos/intl/usa.png",
  };

  const getTeamFlag = (name: string, size: "sm" | "lg" = "sm") => {
    if (!name) return <span className={size === "lg" ? "text-4xl" : "text-sm"}>🏏</span>;

    const upperName = name.toUpperCase();
    const logoPath = TEAM_LOGOS[upperName];

    if (logoPath) {
      const sizeClasses = size === "lg"
        ? "w-20 h-20 p-1"
        : "w-8 h-8 p-0.5";
      return (
        <img
          src={logoPath}
          alt={name}
          className={`${sizeClasses} object-contain inline-block drop-shadow-[0_0_12px_rgba(16,185,129,0.3)]`}
        />
      );
    }

    // Fallback for countries not in our logo set
    const countryCodes: Record<string, string> = {
      "WEST INDIES": "wi", "IRELAND": "ie", "NETHERLANDS": "nl", "CANADA": "ca", "NEPAL": "np",
    };
    const code = countryCodes[upperName];
    if (code) {
      if (code === "wi") return <span className={size === "lg" ? "text-4xl" : "text-sm"}>🌴</span>;
      return (
        <img
          src={`https://flagcdn.com/${code}.svg`}
          alt={name}
          className={`${size === "lg" ? "w-12 h-8" : "w-5 h-3.5"} object-cover rounded-sm shadow-sm inline-block`}
        />
      );
    }
    return <span className={size === "lg" ? "text-4xl" : "text-sm"}>🏏</span>;
  };

  useEffect(() => {
    getVenueCountries().then(setCountries);
  }, []);

  useEffect(() => {
    if (country) {
      getVenuesByCountry(country).then((data) => {
        setVenues(data);
        if (data.length > 0 && !data.includes(venue)) {
          setVenue(data[0]);
        }
      });
    }
  }, [country]);

  const handlePredict = async () => {
    setLoading(true);
    setError("");
    setPrediction(null);
    try {
      const data = await getPrediction(teamA, teamB, venue, format);
      setPrediction(data);
      try {
        const h2hData = await getH2HDetails(teamA, teamB, format);
        setPreviewH2H(h2hData);
      } catch (e) {
        setPreviewH2H([]);
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await triggerSync();
    } catch (err) {
      console.error("Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  const fetchScoreboard = async (team: string) => {
    setLoadingScoreboard(true);
    setSelectedScoreboard(null);
    try {
      const data = await getLastMatchScoreboard(team, format);
      setSelectedScoreboard(data);
    } catch (err: any) {
      console.error("Scoreboard fetch failed");
    } finally {
      setLoadingScoreboard(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center bg-[#050505] text-[#e0e0e0] selection:bg-white/10 selection:text-white font-space-grotesk">
      {/* Background Kinetic Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute -top-[20%] -left-[10%] w-[800px] h-[800px] rounded-full blur-[200px] opacity-20 transition-all duration-1000"
          style={{ backgroundColor: teamA ? themeA.primary : '#10b981' }}
        />
        <div 
          className="absolute bottom-[0%] -right-[10%] w-[800px] h-[800px] rounded-full blur-[200px] opacity-20 transition-all duration-1000"
          style={{ backgroundColor: teamB ? themeB.primary : '#ffffff' }}
        />
      </div>

      {/* Premium Kinetic Header */}
      <header className="w-full max-w-7xl px-12 py-12 flex items-center justify-center z-10">
        <div className="flex flex-col gap-1 items-center">
          <h1 className="text-5xl font-black tracking-tighter text-white uppercase italic">
            CRIC<span className="text-primary ml-1">ORACLE</span>
          </h1>
        </div>
      </header>

      <div className="flex flex-col gap-16 w-full max-w-7xl px-8 py-12 z-10">
        
        {/* Match Selection Engine */}
        <MatchSelector
          format={format} setFormat={setFormat}
          teamA={teamA} setTeamA={setTeamA}
          teamB={teamB} setTeamB={setTeamB}
          country={country} setCountry={setCountry} countries={countries}
          venue={venue} setVenue={setVenue} venues={venues}
          loading={loading} handlePredict={handlePredict}
        />

        {/* Loading Perspective */}
        {loading && (
          <div className="py-32 flex flex-col items-center justify-center animate-in fade-in duration-700">
             <div className="relative w-32 h-32 mb-12">
               <div className="absolute inset-0 border-4 border-primary/20 rounded-full animate-ping" />
               <div className="absolute inset-0 border-t-4 border-primary rounded-full animate-spin shadow-[0_0_20px_rgba(16,185,129,0.5)]" />
               <div className="absolute inset-8 border border-white/5 rounded-full" />
             </div>
             <h2 className="font-space-grotesk text-2xl font-black tracking-[0.6em] uppercase text-primary text-glow">
              Processing Engrams
             </h2>
             <p className="font-inter text-[10px] text-white/40 uppercase tracking-[0.4em] mt-4 animator-pulse">
               Synchronizing tactical variables and historical vectors...
             </p>
          </div>
        )}

        {/* Prediction Intelligence Pipeline */}
        {!loading && prediction && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start animate-in fade-in slide-in-from-bottom-8 duration-1000">
            
            <MatchHero 
              prediction={prediction} 
              teamA={teamA} 
              teamB={teamB} 
              getTeamFlag={getTeamFlag} 
            />

            <H2HCard 
              h2h={prediction.h2h} 
              teamA={teamA} 
              teamB={teamB} 
              previewMatches={previewH2H} 
              getTeamFlag={getTeamFlag}
              format={format}
            />

            <SquadIntelligence 
              teamA={prediction.team_a} 
              teamB={prediction.team_b} 
              getTeamFlag={getTeamFlag}
              fetchScoreboard={fetchScoreboard}
            />

            {/* Weather Analysis */}
            <div className="lg:col-span-12 h-full">
              <AnalyticsCard title="Weather" subtitle="Real-time Conditions" className="h-full">
                <div className="flex flex-col items-center py-10 gap-10">
                  <div className="relative">
                    <div className="text-7xl drop-shadow-[0_0_30px_rgba(16,185,129,0.4)]">
                      {prediction.weather.condition.includes('Cloud') ? '☁️' : prediction.weather.condition.includes('Rain') ? '🌧️' : '☀️'}
                    </div>
                    <div className="absolute -top-4 -right-4">
                       <InformaticsChip label="LIVE SENSOR" active={true} variant="emerald" className="h-5 px-2 border-none" />
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="font-space-grotesk text-7xl font-black text-white tracking-widest">{prediction.weather.temp}</div>
                    <div className="font-space-grotesk text-[11px] text-primary uppercase tracking-[0.4em] font-bold mt-2">CITY: {prediction.venue.city.toUpperCase()}</div>
                  </div>
                  
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 w-full px-4">
                    {[
                      { label: 'HUMIDITY', val: '42%' },
                      { label: 'WIND VELOCITY', val: '14 KM/H' },
                      { label: 'DEW INDEX', val: 'MODERATE' },
                      { label: 'PRECIPITATION', val: '5%' }
                    ].map(stat => (
                      <div key={stat.label} className="p-4 rounded-xl glass-carbon border-white/5 flex flex-col gap-1 items-center hover:border-white/20 transition-colors">
                        <span className="font-inter text-[9px] font-black text-white/30 uppercase tracking-widest">{stat.label}</span>
                        <span className="font-space-grotesk text-lg font-bold text-white">{stat.val}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </AnalyticsCard>
            </div>

          </div>
        )}

        {/* Empty State Projection */}
        {!prediction && !error && !loading && (
          <div className="py-40 flex flex-col items-center justify-center text-center animate-in fade-in duration-1000">
            <div className="relative mb-12">
               <div className="absolute inset-0 bg-primary/5 rounded-full blur-[80px]" />
               <div className="relative text-9xl opacity-20 filter drop-shadow-[0_0_20px_rgba(16,185,129,0.3)]">🏏</div>
            </div>
          </div>
        )}

        {error && (
          <div className="p-12 rounded-[2rem] glass-carbon border-destructive/30 flex flex-col items-center gap-6 animate-shake">
            <div className="w-16 h-16 rounded-full bg-destructive/10 border border-destructive/30 flex items-center justify-center text-3xl">⚠️</div>
            <div className="text-center">
              <h4 className="font-space-grotesk text-2xl font-black text-destructive uppercase tracking-widest mb-2">Neural Vector Lost</h4>
              <p className="font-inter text-white/40 text-xs uppercase tracking-widest max-w-sm mx-auto">{error}</p>
            </div>
          </div>
        )}
      </div>

      {/* High-Fidelity Footer */}
      <footer className="w-full max-w-7xl px-8 py-16 mt-12 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-12 z-10">
        <div className="flex flex-col gap-2">
        </div>
        
        <div className="flex items-center gap-8">
           <button
            onClick={handleSync}
            disabled={syncing}
            className="group px-8 py-4 rounded-xl border border-white/10 glass-carbon font-space-grotesk text-[10px] font-bold tracking-[0.5em] uppercase text-white/40 hover:text-primary hover:border-primary/40 transition-all flex items-center gap-4 active:scale-95 disabled:opacity-30"
          >
            {syncing ? (
              <span className="flex items-center gap-3">
                <span className="w-3 h-3 border-2 border-primary/20 border-t-primary animate-spin rounded-full" />
                SYNCING ENGRAMS
              </span>
            ) : "REFRESH REAL-TIME ENGRAMS"}
          </button>
        </div>
      </footer>

      {/* Asset Archive Modal */}
      {selectedScoreboard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-2xl animate-in fade-in duration-500">
           <div className="w-full max-w-2xl glass-carbon rounded-[2.5rem] border-white/10 overflow-hidden shadow-[0_64px_128px_rgba(0,0,0,0.8)] border flex flex-col">
              <div className="p-8 border-b border-white/5 flex justify-between items-center">
                <div className="flex flex-col gap-1">
                  <span className="font-space-grotesk text-[10px] font-black text-white/40 uppercase tracking-[0.5em]">
                    {selectedScoreboard.date} // {selectedScoreboard.venue}
                  </span>
                </div>
                <button 
                  onClick={() => setSelectedScoreboard(null)} 
                  className="w-10 h-10 flex items-center justify-center rounded-full border border-white/5 hover:border-primary/40 hover:text-primary transition-all text-2xl font-light"
                >
                  &times;
                </button>
              </div>
              <div className="p-10 overflow-y-auto max-h-[70vh]">
                 <div className="flex flex-col gap-10">
                     <div className="text-center flex flex-col gap-8">
                        <div className="flex items-center justify-center gap-12">
                           <div className="filter drop-shadow-[0_0_20px_rgba(255,255,255,0.1)]">
                             {getTeamFlag(selectedScoreboard.scoreboard[0].team, "lg")}
                           </div>
                           <div className="font-space-grotesk text-2xl font-black text-white/10 italic">VS</div>
                           <div className="filter drop-shadow-[0_0_20px_rgba(255,255,255,0.1)]">
                             {getTeamFlag(selectedScoreboard.scoreboard[1].team, "lg")}
                           </div>
                        </div>
                        <div className="flex flex-wrap justify-center gap-3">
                          <InformaticsChip 
                            label={selectedScoreboard.result
                              .replace(new RegExp(selectedScoreboard.scoreboard[0].team, 'gi'), "")
                              .replace(new RegExp(selectedScoreboard.scoreboard[1].team, 'gi'), "")
                              .replace(/won by/gi, "win by")
                              .trim()
                              .toUpperCase()
                            } 
                            variant="emerald" 
                            className="h-6 px-4 border-none bg-primary text-black font-black" 
                          />
                        </div>
                     </div>
                    
                    <div className="grid grid-cols-2 gap-6">
                       {selectedScoreboard.scoreboard.map((sb: any) => (
                          <div key={sb.team} className="p-8 rounded-3xl glass-carbon bg-white/[0.02] border-white/5 hover:border-white/20 transition-all flex flex-col gap-4 items-center">
                             <div className="w-full h-1 bg-gradient-to-r from-transparent via-white/5 to-transparent mb-4" />
                             <div className="flex flex-col items-center">
                                <div className="font-space-grotesk text-5xl font-black text-white text-glow">{sb.runs}/{sb.wickets}</div>
                                <div className="font-space-grotesk text-[10px] text-primary mt-2 font-black uppercase tracking-[0.4em]">{sb.overs} ARCHIVE OV</div>
                             </div>
                          </div>
                       ))}
                    </div>
                 </div>
              </div>
           </div>
        </div>
      )}
    </main>
  );
}
