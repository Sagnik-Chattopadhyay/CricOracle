export interface TeamTheme {
  primary: string;
  secondary: string;
  accent: string;
}

export const TEAM_THEMES: Record<string, TeamTheme> = {
  // IPL Teams
  "MUMBAI INDIANS": { primary: "#004B8D", secondary: "#FFD141", accent: "#E1261C" },
  "CHENNAI SUPER KINGS": { primary: "#F2C701", secondary: "#0000FF", accent: "#F2C701" },
  "ROYAL CHALLENGERS BENGALURU": { primary: "#EC1C24", secondary: "#C3A342", accent: "#000000" },
  "ROYAL CHALLENGERS BANGALORE": { primary: "#EC1C24", secondary: "#C3A342", accent: "#000000" },
  "KOLKATA KNIGHT RIDERS": { primary: "#3A225D", secondary: "#F7D54E", accent: "#3A225D" },
  "RAJASTHAN ROYALS": { primary: "#EA1B7E", secondary: "#004A99", accent: "#EA1B7E" },
  "SUNRISERS HYDERABAD": { primary: "#F26522", secondary: "#000000", accent: "#F26522" },
  "DELHI CAPITALS": { primary: "#00008B", secondary: "#EF1B23", accent: "#00008B" },
  "PUNJAB KINGS": { primary: "#ED1C24", secondary: "#C0C0C0", accent: "#ED1C24" },
  "GUJARAT TITANS": { primary: "#092645", secondary: "#00AEEF", accent: "#092645" },
  "LUCKNOW SUPER GIANTS": { primary: "#00AEEF", secondary: "#E3263B", accent: "#00AEEF" },

  // International Teams
  "INDIA": { primary: "#078BDC", secondary: "#F5895A", accent: "#078BDC" },
  "AUSTRALIA": { primary: "#FFD950", secondary: "#006432", accent: "#FFD950" },
  "PAKISTAN": { primary: "#006A4D", secondary: "#FFFFFF", accent: "#006A4D" },
  "ENGLAND": { primary: "#001844", secondary: "#CF081F", accent: "#001844" },
  "SOUTH AFRICA": { primary: "#006A4E", secondary: "#FFCD00", accent: "#006A4E" },
  "NEW ZEALAND": { primary: "#000000", secondary: "#C0C0C0", accent: "#000000" },
  "WEST INDIES": { primary: "#7B2C3B", secondary: "#F9D21C", accent: "#7B2C3B" },
  "SRI LANKA": { primary: "#0038A8", secondary: "#F7D417", accent: "#0038A8" },
  "BANGLADESH": { primary: "#006A4E", secondary: "#F42A41", accent: "#006A4E" },
};

export const getTeamTheme = (name: string): TeamTheme => {
  const upperName = name?.toUpperCase();
  return TEAM_THEMES[upperName] || { primary: "#10b981", secondary: "#34d399", accent: "#059669" }; // Fallback to Emerald
};
