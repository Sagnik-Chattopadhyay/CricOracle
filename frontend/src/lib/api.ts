export const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type PlayerForm = {
    name: string;
    pfi: number;
    batting_pfi?: number;
    bowling_pfi?: number;
    role?: string;
    image_url?: string;
    batting_style?: string;
    bowling_style?: string;
};

export type TeamInfo = {
    name: string;
    squad: PlayerForm[];
    venue_adv: string;
    form_adv: string;
};

export type H2HStats = {
    total: number;
    team_a_wins: number;
    team_b_wins: number;
    draws: number;
};

export type WeatherInfo = {
    temp: string;
    condition: string;
    humidity: string;
    source: string;
};

export type PredictionData = {
    prediction: string;
    win_probability: string;
    confidence: string;
    team_a: TeamInfo;
    team_b: TeamInfo;
    h2h: H2HStats;
    venue: { name: string; city: string };
    weather: WeatherInfo;
};

export async function getPrediction(team_a: string, team_b: string, venue: string, match_format: string = "IPL") {
    const response = await fetch(`${BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ team_a, team_b, venue, match_format }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to fetch prediction");
    }
    return response.json();
}

export const getLastMatchScoreboard = async (team: string, format: string) => {
    try {
        const response = await fetch(`${BASE_URL}/team/last-match?team=${encodeURIComponent(team)}&format=${format}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch last match score: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching last match:", error);
        throw error;
    }
};

export const getH2HDetails = async (teamA: string, teamB: string, format: string) => {
    try {
        const response = await fetch(`${BASE_URL}/team/h2h-details?team_a=${encodeURIComponent(teamA)}&team_b=${encodeURIComponent(teamB)}&format=${format}&limit=5`);
        if (!response.ok) {
            throw new Error(`Failed to fetch H2H details: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Error fetching H2H details:", error);
        throw error;
    }
};

export async function searchTeams(q: string, format?: string): Promise<string[]> {
    const url = `${BASE_URL}/search/teams?q=${encodeURIComponent(q)}${format ? `&format=${format}` : ""}`;
    const response = await fetch(url);
    if (!response.ok) return [];
    return response.json();
}

export async function getVenueCountries(): Promise<string[]> {
    const response = await fetch(`${BASE_URL}/venues/countries`);
    if (!response.ok) return [];
    return response.json();
}

export async function getVenuesByCountry(country: string): Promise<string[]> {
    const response = await fetch(`${BASE_URL}/venues/by-country?country=${encodeURIComponent(country)}`);
    if (!response.ok) return [];
    return response.json();
}

export async function searchVenues(q: string): Promise<string[]> {
    const response = await fetch(`${BASE_URL}/search/venues?q=${encodeURIComponent(q)}`);
    if (!response.ok) return [];
    return response.json();
}

export async function triggerSync() {
    const response = await fetch(`${BASE_URL}/sync`, { method: "POST" });
    return response.json();
}
