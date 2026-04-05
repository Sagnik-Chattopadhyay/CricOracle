import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
});

export const metadata: Metadata = {
  title: "CricOracle | Premium Cricket Analytics",
  description: "Advanced AI-driven cricket match prediction and analytics dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans scroll-smooth", inter.variable, spaceGrotesk.variable)}>
      <body
        className="antialiased min-h-screen selection:bg-primary/30 selection:text-primary"
      >
        {children}
      </body>
    </html>
  );
}
