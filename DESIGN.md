# Design System: CricOracle AI Predictor
**Project ID:** 17263216602954997851

## 1. Visual Theme & Atmosphere
**The Analytical Kineticist.** 
This interface is a high-performance sports analytics cockpit. It rejects the cluttered chaos of traditional betting apps in favor of a clinical, architectural "Data Lab" atmosphere. The density is high but organized—like a Swiss chronograph or a luxury flight instrument. The mood is dark, focused, and urgent, utilizing intentional asymmetry to guide the eye through complex match simulations and squad performance metrics.

## 2. Color Palette & Roles
*   **Foundational Slate-Ink** (#0F172A) — Primary background surface. A deep, architectural charcoal that provides maximum contrast for data layers. (Never use #000000).
*   **Kinetic Emerald** (#10B981) — Strategic Accent. Used for winning probabilities, active form indicators, and primary CTAs. It represents growth, success, and positive momentum.
*   **Precision Gold** (#F59E0B) — Tertiary data highlights. Reserved for "Player of the Match" stats, critical weather warnings (Turning points), and "Impact Player" tags.
*   **Shadow Steel** (#535B71) — Secondary UI elements. Used for structural dividers, secondary text, and inactive states.
*   **Whisper Border** (rgba(100, 116, 139, 0.2)) — 1px structural lines only where essential for data grid alignment.

## 3. Typography Rules
*   **Display:** **Cabinet Grotesk** — Track-tight (-0.02em). Used for match titles, headline scores, and massive percentages. It provides a unique, authoritative character that moves beyond generic geometric sans.
*   **Body:** **Satoshi** — Relaxed leading (1.6). Used for descriptive analysis and squad lists. Max line width of 65ch to maintain readability during live match shifts.
*   **Numbers/Mono:** **JetBrains Mono** — Required for all densities exceeding 7. Used for Strike Rates, Over-by-Over breakdowns, and Win Probabilities to ensure perfect columnar alignment.
*   **Banned:** **Inter** (too generic), **Lexend** (too round/friendly for high-stakes analytics).

## 4. Component Stylings
*   **Buttons:** AERODYNAMIC PILL-SHAPED. Tactile -1px downward translate on active state. No outer neon glows.
*   **Cards:** DENSE & LAYERED. Corner roundness at 1rem. Boundaries are defined by tonal shifts (Surface-on-Surface) rather than 1px borders or heavy shadows.
*   **Data Tracks:** DUAL-TRACK PROGRESS BARS. Win probability uses Kinetic Emerald vs. Shadow Steel. Tracks are recessed using a slightly darker fill than the background.
*   **Heatmaps:** 3-tier system using Kinetic Emerald (Hot), Precision Gold (Warm), and Muted Slate (Cold).

## 5. Layout Principles
*   **Intentional Asymmetry:** Hero sections (Match Overview) must avoid center alignment. Use split-screen layouts where the venue atmosphere (Image/Visual) occupies the right 40% and raw stats occupy the left 60%.
*   **Data Density:** Cockpit Density (8/10). Group related metrics (Humidity, Dew, Temp) using generous vertical whitespace (2rem) instead of horizontal lines.
*   **Hardware Acceleration:** All transitions (score updates, form reveals) must use `transform` and `opacity` only.

## 6. Motion & Interaction
*   **Spring Physics:** Weighty and dampened (stiffness: 100, damping: 20). Every card reveal should feel like a physical drawer opening.
*   **Perpetual Micro-Interactions:** Live match indicators pulse subtly. The "Predicting..." state uses a typewriter effect or a shimmering data skeleton.

## 7. Anti-Patterns (Banned)
*   **No Emojis:** Use custom icons or text labels exclusively.
*   **No Pure Black:** (#000000 is banned; use Slate-Ink).
*   **No Generic 3-Column Grids:** Use staggered masonry or asymmetric split layouts.
*   **No AI Copywriting:** Avoid "Unleash," "Seamless," or "Next-Gen." Use "Simulate," "Analyze," and "Engineer."
*   **No Metric Fabrication:** Use real match historicals or `[pending]` labels; never make up performance percentages.
