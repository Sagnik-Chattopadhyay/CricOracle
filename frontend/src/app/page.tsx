"use client";

import { useState, useEffect } from "react";
import {
  getPrediction,
  triggerSync,
  searchTeams,
  getVenueCountries,
  getVenuesByCountry,
  getLastMatchScoreboard,
  getH2HDetails,
  type PredictionData,
  type PlayerForm
} from "@/lib/api";
import Autocomplete from "@/components/Autocomplete";
import Select from "@/components/Select";
import Image from "next/image";

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

  // Scoreboard Modal State
  const [selectedScoreboard, setSelectedScoreboard] = useState<any>(null);
  const [loadingScoreboard, setLoadingScoreboard] = useState(false);
  const [scoreboardError, setScoreboardError] = useState("");

  // H2H Detail Modal State
  const [selectedH2H, setSelectedH2H] = useState<any[] | null>(null);
  const [loadingH2H, setLoadingH2H] = useState(false);
  const [h2hError, setH2HError] = useState("");
  const [previewH2H, setPreviewH2H] = useState<any[]>([]);

  const formats = ["IPL", "T20I", "ODI", "Tests"];

  const getTeamFlag = (name: string, size: "sm" | "lg" = "sm") => {
    if (!name) return <span className={size === "lg" ? "text-4xl" : "text-sm"}>🏏</span>;

    // Country codes for FlagCDN
    const countryCodes: Record<string, string> = {
      "INDIA": "in", "IND": "in",
      "AUSTRALIA": "au", "AUS": "au",
      "NEW ZEALAND": "nz", "NZ": "nz",
      "ENGLAND": "gb", "ENG": "gb",
      "SOUTH AFRICA": "za", "SA": "za",
      "PAKISTAN": "pk", "PAK": "pk",
      "SRI LANKA": "lk", "SL": "lk",
      "WEST INDIES": "wi", "WI": "wi",
      "BANGLADESH": "bd", "BAN": "bd",
      "AFGHANISTAN": "af", "AFG": "af",
      "IRELAND": "ie", "IRE": "ie",
      "ZIMBABWE": "zw", "ZIM": "zw",
      "NETHERLANDS": "nl", "NED": "nl",
      "USA": "us", "CANADA": "ca", "NEPAL": "np"
    };

    const iplIcons: Record<string, string> = {
      "ROYAL CHALLENGERS BANGALORE": "🔴",
      "CHENNAI SUPER KINGS": "🟡",
      "MUMBAI INDIANS": "🔵",
      "KOLKATA KNIGHT RIDERS": "🟣",
      "GUJARAT TITANS": "⚪",
      "LUCKNOW SUPER GIANTS": "🧊",
      "RAJASTHAN ROYALS": "💗",
      "DELHI CAPITALS": "🏙️",
      "PUNJAB KINGS": "🦁",
      "SUNRISERS HYDERABAD": "🟠"
    };

    const upperName = name.toUpperCase();

    if (countryCodes[upperName]) {
      const code = countryCodes[upperName];
      // Special handling for West Indies (WI isn't a standard ISO country code in most CDNs)
      if (code === "wi") return <span className={size === "lg" ? "text-4xl" : "text-sm"}>🌴</span>;

      return (
        <img
          src={`https://flagcdn.com/${code}.svg`}
          alt={name}
          className={`${size === "lg" ? "w-12 h-8" : "w-5 h-3.5"} object-cover rounded-sm shadow-sm inline-block`}
        />
      );
    }

    return <span className={size === "lg" ? "text-4xl" : "text-sm"}>{iplIcons[upperName] || "🏏"}</span>;
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

      // Fetch H2H preview as well
      try {
        const h2hData = await getH2HDetails(teamA, teamB, format);
        setPreviewH2H(h2hData.slice(0, 2));
      } catch (e) {
        console.error("Failed to fetch H2H preview", e);
        setPreviewH2H([]);
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await triggerSync();
      alert("Live data sync completed successfully!");
    } catch (err) {
      alert("Sync failed. Ensure backend is running.");
    } finally {
      setSyncing(false);
    }
  };

  const fetchScoreboard = async (team: string) => {
    setLoadingScoreboard(true);
    setScoreboardError("");
    setSelectedScoreboard(null);
    try {
      const data = await getLastMatchScoreboard(team, format);
      setSelectedScoreboard(data);
    } catch (err: any) {
      if (err.message === "Failed to fetch") {
        setScoreboardError("Connection to analysis engine lost. Please ensure the backend is running and try again.");
      } else {
        setScoreboardError(err.message || "Archive data lost in time.");
      }
    } finally {
      setLoadingScoreboard(false);
    }
  };

  const handleFetchH2HDetails = async () => {
    setLoadingH2H(true);
    setH2HError("");
    setSelectedH2H(null);
    try {
      // Map format string back to API format code
      let formattedFormat = format;
      if (format === "T20 International") formattedFormat = "T20I";

      const data = await getH2HDetails(teamA, teamB, formattedFormat);
      setSelectedH2H(data);
    } catch (err: any) {
      setH2HError(err.message || "Historical rivalry data currently unavailable.");
    } finally {
      setLoadingH2H(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center bg-dark-bg text-white overflow-x-hidden">
      {/* Header */}
      <header className="w-full max-w-7xl px-4 py-6 flex items-center justify-between relative">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <h1 className="text-4xl font-bebas tracking-tight">
              Cric<span className="text-gold [text-shadow:0_0_10px_rgba(245,200,66,0.5)]">Oracle</span>
            </h1>
            <div className="w-2.5 h-2.5 rounded-full bg-gold animate-heartbeat shadow-[0_0_8px_#f5c842]"></div>
          </div>

          <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-success/10 border border-success/20 rounded-full">
            <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse"></div>
            <span className="text-[10px] font-bold text-success uppercase tracking-widest">Live Data</span>
          </div>
        </div>

        <nav className="hidden lg:flex items-center gap-8">
          {["Predict", "H2H", "Players", "IPL Hub", "Venues"].map((item) => (
            <button
              key={item}
              className={`text-sm font-bold tracking-wide transition-colors ${item === "Predict" ? "text-gold" : "text-muted hover:text-white"
                }`}
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="text-[10px] font-mono text-muted uppercase tracking-[0.2em]">
          4M+ Ball Records
        </div>

        <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-gold to-cyan opacity-20"></div>
      </header>

      <div className="flex flex-col gap-8 w-full max-w-7xl px-4 py-8">
        {/* Match Selector Panel */}
        <div className="surface-base rounded-2xl p-8 relative group animate-fade-up">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-gold to-cyan opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end">
            <div className="lg:col-span-2">
              <Select
                label="Format"
                value={format}
                onChange={setFormat}
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
                label="Team A"
                value={teamA}
                onChange={setTeamA}
                onSearch={(q) => searchTeams(q, format)}
                placeholder="Search team..."
              />
            </div>

            <div className="lg:col-span-1 flex flex-col items-center justify-center h-full pb-3">
              <div className="h-4 w-[1px] bg-border-subtle"></div>
              <span className="font-bebas text-muted text-xl py-2">VS</span>
              <div className="h-4 w-[1px] bg-border-subtle"></div>
            </div>

            <div className="lg:col-span-3">
              <Autocomplete
                label="Team B"
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
                className="w-full py-4 rounded-xl font-bebas text-xl tracking-widest text-[#060b14] bg-gradient-to-br from-gold to-[#ff6b2b] shadow-[0_4px_20px_rgba(245,200,66,0.3)] hover:shadow-[0_4px_30px_rgba(245,200,66,0.5)] active:scale-[0.98] transition-all disabled:opacity-50 shimmer-sweep overflow-hidden relative"
              >
                {loading ? "Analyzing..." : "Analyse Match"}
              </button>
            </div>

            <div className="lg:col-span-4">
              <Select
                label="Location"
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

            <div className="lg:col-span-4">
              <label className="block text-[10px] font-bold text-muted uppercase tracking-[0.2em] mb-3">Match Date</label>
              <input
                type="date"
                className="w-full bg-surface-elevated border border-border-subtle rounded-xl p-3 outline-none focus:border-gold/50 transition-colors cursor-pointer text-sm font-mono"
              />
            </div>
          </div>
        </div>

        {/* Prediction Loading State */}
        {loading && (
          <div className="surface-base rounded-2xl p-12 flex flex-col items-center justify-center animate-fade-up hud-scanline">
            <div className="w-32 h-32 relative mb-8">
              <div className="absolute inset-0 border-2 border-cyan/20 rounded-full animate-ping"></div>
              <div className="absolute inset-0 border-t-2 border-gold rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-4xl animate-pulse">📡</span>
              </div>
            </div>
            <h2 className="font-bebas text-3xl tracking-[0.3em] mb-4 text-white">Initialising Neural Core</h2>
            <div className="font-mono text-[10px] text-cyan/60 flex flex-col items-center gap-1">
              <span className="animate-pulse">{" >> "} STREAMING MATCH DATA [4.2M SAMPLES]</span>
              <span className="animate-pulse flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-success"></span>
                SYNCING LIVE WEATHER SENSORS...
              </span>
            </div>
          </div>
        )}

        {/* Prediction Display */}
        {!loading && prediction && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start animate-fade-up">

            {/* Left: Win Probability & H2H */}
            <div className="lg:col-span-4 flex flex-col gap-8 animate-fade-up [animation-delay:200ms]">
              {/* Win Probability Card */}
              <div className="surface-base rounded-2xl p-8 relative overflow-hidden">
                <div className="flex justify-between items-center mb-10">
                  <div className="flex items-center gap-2 px-2 py-1 bg-gold/5 border border-gold/20 rounded">
                    <span className="text-gold text-[10px]">✦</span>
                    <span className="font-bebas text-[10px] text-gold tracking-widest uppercase">AI Analysis</span>
                  </div>
                  <div className="font-bebas text-muted text-[10px] tracking-widest uppercase">Win Probability</div>
                </div>

                <div className="relative flex flex-col items-center justify-center pb-8 border-b border-border-subtle mb-8">
                  <div className="relative w-64 h-32 overflow-hidden">
                    <svg className="w-full h-full" viewBox="0 0 100 50">
                      <path
                        d="M 10 45 A 35 35 0 0 1 90 45"
                        fill="none"
                        stroke="#111d2e"
                        strokeWidth="8"
                        strokeLinecap="round"
                      />
                      <path
                        d="M 10 45 A 35 35 0 0 1 90 45"
                        fill="none"
                        stroke="url(#arcGradient)"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray="125.66"
                        strokeDashoffset={125.66 - (125.66 * (parseFloat(prediction.win_probability) / 100))}
                        className="transition-all duration-1000 ease-out"
                        style={{ filter: "drop-shadow(0 0 5px rgba(245,200,66,0.3))" }}
                      />
                      <defs>
                        <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#f5c842" />
                          <stop offset="100%" stopColor="#ff6b2b" />
                        </linearGradient>
                      </defs>
                    </svg>

                    <div className="absolute inset-0 flex flex-col items-center justify-end pb-1">
                      <span className="font-bebas text-4xl text-transparent bg-clip-text bg-gradient-to-br from-gold to-orange leading-none mb-1">
                        {prediction.win_probability}
                      </span>
                      <span className="font-bebas text-gold text-[10px] tracking-[0.2em] uppercase flex items-center gap-1.5 justify-center">
                        <span className="opacity-80">{getTeamFlag(prediction.prediction, "sm")}</span>
                        <span>{prediction.prediction}</span>
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 mb-8 bg-surface-elevated/50 p-3 rounded-xl border border-border-subtle">
                  <div className="w-2 h-2 rounded-full bg-success animate-pulse shadow-[0_0_8px_#00e5a0]"></div>
                  <span className="font-mono text-[10px] tracking-widest text-white uppercase">Confidence: <span className="text-success">{prediction.confidence.split(' ')[0].toUpperCase()}</span></span>
                </div>

                <div className="space-y-4">
                  {[
                    { name: 'Head-to-Head', val: '+8.2', status: 'pos' },
                    { name: 'Recent Form', val: '+6.5', status: 'pos' },
                    { name: 'Player Form Index', val: '+4.1', status: 'pos' },
                    { name: 'Venue Advantage', val: '+7.8', status: 'pos' },
                    { name: 'Pitch Conditions', val: '+3.2', status: 'pos' },
                    { name: 'Toss Factor', val: '-1.4', status: 'neg' }
                  ].map((factor, i) => (
                    <div
                      key={factor.name}
                      className="flex justify-between items-center group cursor-default"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-[1px] h-6 bg-border-subtle group-hover:bg-gold transition-colors group-hover:shadow-[0_0_10px_#f5c842]"></div>
                        <span className="text-[10px] font-bold text-muted uppercase tracking-widest group-hover:text-white transition-colors">{factor.name}</span>
                      </div>
                      <span className={`font-mono text-xs ${factor.status === 'pos' ? 'text-success' : 'text-danger'}`}>
                        {factor.val}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right: H2H & Squad Intelligence */}
            <div className="lg:col-span-8 flex flex-col gap-8 animate-fade-up [animation-delay:400ms]">
              {/* Head-to-Head Card */}
              <div className="surface-base rounded-2xl p-8 relative">
                <div className="flex justify-between items-center mb-10 border-b border-border-subtle pb-6">
                  <div className="font-bebas text-muted text-[10px] tracking-[0.3em] uppercase">Historical Command</div>
                  <div className="font-bebas text-muted text-[10px] tracking-[0.3em] uppercase">Clash of Titans</div>
                </div>

                <div className="flex justify-between items-center mb-8 px-4">
                  <div className="flex flex-col items-center gap-3 text-center">
                    <div className="mb-1">{getTeamFlag(teamA, "lg")}</div>
                    <span className="font-bebas text-muted text-sm tracking-widest uppercase truncate max-w-[120px]">{teamA || 'Team A'}</span>
                    <span className="font-bebas text-gold text-5xl leading-none">{prediction.h2h.team_a_wins}</span>
                    <span className="font-bebas text-muted text-[10px] tracking-widest uppercase mt-1">Wins</span>
                  </div>

                  <div className="flex flex-col items-center">
                    <div className="h-8 w-[1px] bg-border-subtle mb-2"></div>
                    <span className="font-bebas text-muted text-xl">VS</span>
                    <span className="font-mono text-[10px] text-muted tracking-widest mt-2 uppercase">{prediction.h2h.total} Matches</span>
                    <span className="font-mono text-[10px] text-muted tracking-widest uppercase">{prediction.h2h.draws} Draws</span>
                    <div className="h-8 w-[1px] bg-border-subtle mt-2"></div>
                  </div>

                  <div className="flex flex-col items-center gap-3 text-center">
                    <div className="mb-1">{getTeamFlag(teamB, "lg")}</div>
                    <span className="font-bebas text-muted text-sm tracking-widest uppercase truncate max-w-[120px]">{teamB || 'Team B'}</span>
                    <span className="font-bebas text-orange text-5xl leading-none">{prediction.h2h.team_b_wins}</span>
                    <span className="font-bebas text-muted text-[10px] tracking-widest uppercase mt-1">Wins</span>
                  </div>
                </div>

                <div className="w-full h-1.5 bg-surface-elevated rounded-full overflow-hidden flex shadow-inner mb-12">
                  <div
                    className="h-full bg-gold shadow-[0_0_15px_rgba(245,200,66,0.5)] transition-all duration-1000"
                    style={{ width: `${(prediction.h2h.team_a_wins / prediction.h2h.total) * 100}%` }}
                  ></div>
                  <div
                    className="h-full bg-muted opacity-20"
                    style={{ width: `${(prediction.h2h.draws / prediction.h2h.total) * 100}%` }}
                  ></div>
                  <div
                    className="h-full bg-orange shadow-[0_0_15px_rgba(255,107,43,0.5)] transition-all duration-1000"
                    style={{ width: `${(prediction.h2h.team_b_wins / prediction.h2h.total) * 100}%` }}
                  ></div>
                </div>

                <div className="space-y-3">
                  <div className="font-bebas text-muted text-[10px] tracking-widest uppercase mb-4">Recent Rivalry Preview</div>
                  {previewH2H.length > 0 ? (
                    previewH2H.map((match, i) => (
                      <div key={i} className="surface-elevated rounded-xl p-4 flex items-center justify-between border border-border-subtle hover:bg-[#1a2c46] transition-all group">
                        <div className="flex items-center gap-4">
                          <span className="font-mono text-[10px] text-muted group-hover:text-gold">{match.date}</span>
                          <div className="flex flex-col">
                            <span className="text-[10px] font-bold text-white uppercase tracking-wide">
                              {match.scoreboard[0].team} vs {match.scoreboard[1].team} • {format}
                            </span>
                            <span className="font-mono text-[11px] text-muted mt-0.5">
                              {match.scoreboard[0].runs}/{match.scoreboard[0].wickets} vs {match.scoreboard[1].runs}/{match.scoreboard[1].wickets}
                            </span>
                          </div>
                        </div>
                        <div className={`px-3 py-1 rounded-full border ${match.result.toUpperCase().includes(teamA.toUpperCase()) || match.result.toUpperCase().includes('WON') && match.result.toUpperCase().includes(teamA.toUpperCase().split(' ')[0]) ? 'border-success/30 bg-success/10 text-success' :
                          match.result.toUpperCase().includes(teamB.toUpperCase()) || match.result.toUpperCase().includes('WON') && match.result.toUpperCase().includes(teamB.toUpperCase().split(' ')[0]) ? 'border-danger/30 bg-danger/10 text-danger' :
                            'border-muted/30 bg-muted/10 text-muted'
                          } text-[9px] font-bold tracking-widest uppercase flex items-center gap-1.5`}>
                          <span className="text-xs leading-none">{getTeamFlag(match.result.split(' ')[0])}</span>
                          <span>{match.result.split(' ').slice(1).join(' ') || match.result}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-[10px] text-muted uppercase tracking-widest py-8 text-center border border-dashed border-border-subtle rounded-xl">
                      {loading ? "Analyzing battles..." : "No recent H2H preview available"}
                    </div>
                  )}
                  <button onClick={handleFetchH2HDetails} className="w-full py-3 font-bebas text-muted text-[10px] tracking-[0.4em] uppercase hover:text-white transition-colors">Expand Full Archive</button>
                </div>
              </div>
            </div>

            {/* Squad Intelligence Card */}
            <div className="lg:col-span-12 surface-base rounded-2xl p-8 relative overflow-hidden group animate-fade-up [animation-delay:600ms]">
              <div className="flex justify-between items-center mb-8 border-b border-border-subtle pb-6">
                <div className="flex items-center gap-4">
                  <div className="font-bebas text-muted text-[10px] tracking-[0.3em] uppercase">Tactical Asset Overview</div>
                  <div className="h-[1px] w-12 bg-border-subtle"></div>
                  <div className="font-bebas text-white text-[10px] tracking-[0.3em] uppercase">Squad Intelligence</div>
                </div>
                <div className="font-mono text-[10px] text-muted uppercase tracking-widest">Update: Real-time Form</div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                {/* Team A */}
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{getTeamFlag(prediction.team_a.name, "lg")}</div>
                      <h4 className="font-bebas text-gold text-2xl tracking-widest uppercase [text-shadow:0_0_10px_rgba(245,200,66,0.2)]">{prediction.team_a.name}</h4>
                    </div>
                    <div className="text-right">
                      <div className="font-bebas text-muted text-[10px] tracking-widest uppercase">Team Avg PFI</div>
                      <div className="font-mono text-xl text-white">{prediction.team_a.form_adv}</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {prediction.team_a.squad.map((player) => (
                      <PlayerRow key={player.name} player={player} />
                    ))}
                  </div>
                  <button onClick={() => fetchScoreboard(prediction.team_a.name)} className="w-full mt-6 py-3 border border-border-subtle rounded-xl font-bebas text-[10px] tracking-[0.4em] text-muted hover:text-gold hover:border-gold/30 transition-all uppercase">Analyse Last Performance</button>
                </div>

                {/* Team B */}
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{getTeamFlag(prediction.team_b.name, "lg")}</div>
                      <h4 className="font-bebas text-cyan text-2xl tracking-widest uppercase [text-shadow:0_0_10px_rgba(0,212,255,0.2)]">{prediction.team_b.name}</h4>
                    </div>
                    <div className="text-right">
                      <div className="font-bebas text-muted text-[10px] tracking-widest uppercase">Team Avg PFI</div>
                      <div className="font-mono text-xl text-white">{prediction.team_b.form_adv}</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {prediction.team_b.squad.map((player) => (
                      <PlayerRow key={player.name} player={player} />
                    ))}
                  </div>
                  <button onClick={() => fetchScoreboard(prediction.team_b.name)} className="w-full mt-6 py-3 border border-border-subtle rounded-xl font-bebas text-[10px] tracking-[0.4em] text-muted hover:text-cyan hover:border-cyan/30 transition-all uppercase">Analyse Last Performance</button>
                </div>
              </div>
            </div>

            {/* Bottom Row: Weather, Toss */}
            <div className="lg:col-span-12 grid grid-cols-1 md:grid-cols-2 gap-8 pb-12 animate-fade-up [animation-delay:800ms]">
              {/* Weather Card */}
              <div className="surface-base rounded-2xl p-8 flex flex-col items-center group">
                <div className="font-bebas text-muted text-[10px] tracking-[0.3em] uppercase mb-8 w-full border-b border-border-subtle pb-4">Atmospheric Data</div>
                <div className="text-7xl mb-6 relative">
                  <span className="drop-shadow-[0_0_15px_rgba(245,200,66,0.4)]">
                    {prediction.weather.condition.includes('Cloud') ? '☁️' : prediction.weather.condition.includes('Rain') ? '🌧️' : '☀️'}
                  </span>
                </div>
                <div className="font-bebas text-6xl mb-1 tracking-tighter">{prediction.weather.temp}</div>
                <div className="font-bebas text-muted text-sm tracking-[0.2em] uppercase mb-8">{prediction.venue.city}</div>
                <div className="grid grid-cols-2 gap-4 w-full">
                  {[
                    { label: 'Humidity', val: '42%', color: 'text-white' },
                    { label: 'Wind', val: '14 km/h', color: 'text-white' },
                    { label: 'Dew Risk', val: 'Med', color: 'text-orange' },
                    { label: 'Rain Prob', val: '5%', color: 'text-success' }
                  ].map(stat => (
                    <div key={stat.label} className="surface-elevated rounded-xl p-3 border border-border-subtle">
                      <div className="text-[9px] font-bold text-muted uppercase tracking-widest mb-1">{stat.label}</div>
                      <div className={`font-mono text-sm font-bold ${stat.color}`}>{stat.val}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Toss Intelligence */}
              <div className="surface-base rounded-2xl p-8 flex flex-col items-center group">
                <div className="font-bebas text-muted text-[10px] tracking-[0.3em] uppercase mb-8 w-full border-b border-border-subtle pb-4">Toss Intelligence</div>
                <div className="w-24 h-24 rounded-full bg-surface-elevated border border-border-subtle flex items-center justify-center mb-10 overflow-hidden relative">
                  <div className="text-4xl animate-spin-coin">🪙</div>
                  <div className="absolute inset-0 bg-gold/5 pointer-events-none"></div>
                </div>
                <div className="w-full space-y-3">
                  {[
                    { label: 'India wins toss here', val: '68%', color: 'text-gold' },
                    { label: 'Bat first wins at venue', val: '61%', color: 'text-gold' },
                    { label: 'Dew favours chasing', val: 'Yes', color: 'text-cyan' },
                    { label: 'Toss impact weight', val: '5%', color: 'text-muted' }
                  ].map(row => (
                    <div key={row.label} className="flex justify-between items-center py-2 border-b border-border-subtle/50">
                      <span className="text-[10px] font-bold text-muted uppercase tracking-wide">{row.label}</span>
                      <span className={`font-mono text-sm font-bold ${row.color}`}>{row.val}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>
        )}

        {/* Empty State */}
        {!prediction && !error && !loading && (
          <div className="glass p-16 rounded-3xl flex flex-col items-center justify-center text-center">
            <div className="text-8xl mb-8 animate-bounce opacity-20">🏏</div>
            <h3 className="text-3xl font-black mb-4">Awaiting Match Insight</h3>
            <p className="text-slate max-w-md">Configure your teams and venue above, then click predict for a deep-dive AI analysis of squads, H2H, and form.</p>
          </div>
        )}

        {error && (
          <div className="text-center text-red-400 p-8 rounded-3xl glass border-red-400/20 bg-red-400/5">
            <div className="text-4xl mb-4">⚠️</div>
            <p className="font-bold text-xl mb-2">Analysis Failed</p>
            <p>{error}</p>
          </div>
        )}
      </div>

      <div className="mt-12 flex gap-4">
        <button
          onClick={handleSync}
          disabled={syncing}
          className="text-slate text-sm hover:text-gold transition-colors flex items-center gap-2 bg-white/5 px-4 py-2 rounded-full"
        >
          {syncing ? "Syncing..." : "🔄 Refresh Real-time Stats"}
        </button>
      </div>

      {/* Scoreboard Modal */}
      {(selectedScoreboard || loadingScoreboard || scoreboardError) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in zoom-in-95 duration-200">
          <div className="glass max-w-2xl w-full max-h-[90vh] overflow-y-auto rounded-3xl p-8 relative flex flex-col border border-white/10 shadow-2xl">
            <button
              onClick={() => { setSelectedScoreboard(null); setScoreboardError(""); setLoadingScoreboard(false); }}
              className="absolute top-4 right-6 text-slate hover:text-white text-3xl"
            >
              &times;
            </button>

            {loadingScoreboard && <div className="text-center py-16"><div className="text-4xl animate-spin mb-4 text-gold">🏏</div><p className="text-slate font-bold">Searching Archives...</p></div>}
            {scoreboardError && <div className="text-center py-16 text-red-400 font-bold">{scoreboardError}</div>}

            {selectedScoreboard && (
              <div className="flex flex-col gap-6">
                <div className="text-center border-b border-white/10 pb-4">
                  <h2 className="text-2xl font-black mb-1">{selectedScoreboard.match_title}</h2>
                  <p className="text-slate text-sm">{selectedScoreboard.date} • {selectedScoreboard.venue}</p>
                  <p className="text-gold font-bold mt-2 uppercase tracking-widest text-xs bg-gold/10 inline-block px-3 py-1 rounded-full">{selectedScoreboard.result}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {selectedScoreboard.scoreboard.map((sb: any) => (
                    <div key={sb.team} className="bg-white/5 border border-white/5 rounded-2xl p-4 text-center">
                      <h3 className="font-bold text-slate text-xs uppercase mb-2 truncate">{sb.team}</h3>
                      <p className="text-3xl font-black">{sb.runs}<span className="text-lg text-slate font-normal">/{sb.wickets}</span></p>
                      <p className="text-xs text-slate mt-1">({sb.overs} Ov)</p>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-2 gap-6 mt-4">
                  {/* Top Batsmen */}
                  <div>
                    <h4 className="text-[10px] font-black uppercase text-slate tracking-widest mb-3 border-b border-white/5 pb-1">Top Performers (Bat)</h4>
                    <div className="space-y-2">
                      {selectedScoreboard.top_batsmen.map((b: any) => (
                        <div key={b.name} className="flex justify-between items-center text-sm bg-white/5 px-3 py-2 rounded-lg border border-white/[0.02]">
                          <span className="font-medium truncate max-w-[120px]">{b.name}</span>
                          <div className="text-right flex flex-col items-end">
                            <span className="font-black text-gold leading-none">{b.runs}</span>
                            <span className="text-[10px] text-slate mt-1">{b.balls} balls</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Top Bowlers */}
                  <div>
                    <h4 className="text-[10px] font-black uppercase text-slate tracking-widest mb-3 border-b border-white/5 pb-1">Top Performers (Bowl)</h4>
                    <div className="space-y-2">
                      {selectedScoreboard.top_bowlers.map((b: any) => (
                        <div key={b.name} className="flex justify-between items-center text-sm bg-white/5 px-3 py-2 rounded-lg border border-white/[0.02]">
                          <span className="font-medium truncate max-w-[120px]">{b.name}</span>
                          <div className="text-right flex flex-col items-end">
                            <span className="font-black text-orange-500 leading-none">{b.wickets}</span>
                            <span className="text-[10px] text-slate mt-1">{b.runs} runs</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* H2H Detail Modal */}
      {(selectedH2H || loadingH2H || h2hError) && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md animate-in fade-in zoom-in-95 duration-200">
          <div className="glass max-w-4xl w-full max-h-[90vh] overflow-y-auto rounded-3xl p-8 relative flex flex-col border border-white/10 shadow-2xl">
            <button
              onClick={() => { setSelectedH2H(null); setH2HError(""); setLoadingH2H(false); }}
              className="absolute top-4 right-6 text-slate hover:text-white text-3xl z-10"
            >
              &times;
            </button>

            <div className="mb-8 text-center border-b border-white/5 pb-6">
              <h2 className="text-3xl font-black mb-2 text-white"><span className="text-gold">Historic</span> Rivalry</h2>
              <p className="text-slate text-sm">Last 5 Encounters • {teamA} vs {teamB}</p>
            </div>

            {loadingH2H && <div className="text-center py-16"><div className="text-4xl animate-spin mb-4 text-gold">⚔️</div><p className="text-slate font-bold">Unearthing historical battles...</p></div>}
            {h2hError && <div className="text-center py-16 text-red-500 font-bold">{h2hError}</div>}

            {selectedH2H && (
              <div className="grid grid-cols-1 gap-6">
                {selectedH2H.length === 0 ? (
                  <div className="text-center text-slate font-bold py-10 opacity-60">No recent matches found between these teams in this format.</div>
                ) : (
                  selectedH2H.map((match: any, idx: number) => (
                    <div key={idx} className="bg-white/[0.02] border border-white/[0.05] rounded-2xl p-6 hover:bg-white/[0.04] transition-colors relative overflow-hidden">

                      {/* Match Header */}
                      <div className="flex justify-between items-start mb-6 border-b border-white/5 pb-4">
                        <div>
                          <p className="text-xs text-gold uppercase tracking-widest font-black mb-1">{match.date}</p>
                          <p className="text-slate/70 text-sm flex items-center gap-2"><span>📍</span> {match.venue}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] text-slate uppercase font-bold mb-1">Toss</p>
                          <p className="text-sm font-medium"><span className="text-white flex items-center gap-1.5 justify-end"><span>{getTeamFlag(match.toss_winner)}</span><span>{match.toss_winner}</span></span> elected to <span className="text-white">{match.toss_decision}</span></p>
                        </div>
                      </div>

                      {/* Match Result Banner */}
                      <div className="absolute top-0 left-0 w-1 h-full bg-gold opacity-50"></div>

                      {/* Scoreboard Split */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
                        {match.scoreboard.map((sb: any, sIdx: number) => (
                          <div key={sIdx} className="bg-black/20 rounded-xl p-5 border border-white/[0.02]">
                            <div className="flex justify-between items-end mb-3">
                              <h4 className="font-bold text-white text-lg flex items-center gap-2"><span>{getTeamFlag(sb.team)}</span>{sb.team}</h4>
                              <div className="text-right">
                                <span className="text-2xl font-black">{sb.runs}<span className="text-slate text-sm font-normal">/{sb.wickets}</span></span>
                                <span className="block text-[10px] text-slate tracking-widest opacity-60">({sb.overs} OV)</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Result string */}
                      <p className="text-center text-sm font-black text-white bg-gold/10 py-2 rounded-lg border border-gold/20 inline-block px-6 w-full flex items-center justify-center gap-2">
                        <span className="text-lg leading-none">{getTeamFlag(match.result.split(' ')[0])}</span>
                        <span>{match.result.split(' ').slice(1).join(' ') || match.result}</span>
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}

      <footer className="mt-20 text-muted font-mono text-[9px] opacity-50 text-center pb-12 border-t border-border-subtle pt-12 w-full max-w-7xl">
        &copy; 2026 CricOracle AI Engine • Proprietary Neural Clusters (PFI, H2H, Venue, Form) • Mission Control V4.
      </footer>
    </main>
  );
}

function PlayerRow({ player }: { player: PlayerForm }) {
  const pfi = player.pfi;
  const isHot = pfi >= 80;
  const isWarm = pfi >= 50 && pfi < 80;
  const isCold = pfi < 50;

  const barColor = isHot ? 'bg-gradient-to-r from-gold to-orange shadow-[0_0_10px_rgba(245,200,66,0.3)]' :
    isWarm ? 'bg-gradient-to-r from-[#00d4ff] to-cyan' :
      'bg-muted opacity-40';

  return (
    <div className={`flex flex-col p-4 rounded-xl border border-border-subtle bg-surface-elevated/30 group hover:translate-x-1 hover:bg-surface-elevated/60 transition-all duration-300 ${isCold ? 'opacity-60' : ''}`}>
      <div className="flex justify-between items-center mb-3">
        <div className="flex flex-col">
          <span className="text-xs font-bold text-white group-hover:text-gold transition-colors">{player.name}</span>
          <span className="text-[9px] text-muted uppercase tracking-tight">{player.role || 'Professional'}</span>
        </div>
        <div className="font-mono text-xs font-bold text-white">
          {pfi}
        </div>
      </div>
      <div className="w-full h-1 bg-dark-bg rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-1000 ${barColor}`}
          style={{ width: `${Math.min(100, (pfi / 150) * 100)}%` }}
        />
      </div>
    </div>
  );
}
