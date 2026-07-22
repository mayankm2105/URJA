---
name: Luminous Intelligence
colors:
  surface: '#10141a'
  surface-dim: '#10141a'
  surface-bright: '#353940'
  surface-container-lowest: '#0a0e14'
  surface-container-low: '#181c22'
  surface-container: '#1c2026'
  surface-container-high: '#262a31'
  surface-container-highest: '#31353c'
  on-surface: '#dfe2eb'
  on-surface-variant: '#b9cbb9'
  inverse-surface: '#dfe2eb'
  inverse-on-surface: '#2d3137'
  outline: '#849585'
  outline-variant: '#3b4b3d'
  surface-tint: '#00e478'
  primary: '#f1ffef'
  on-primary: '#003919'
  primary-container: '#00ff87'
  on-primary-container: '#007138'
  inverse-primary: '#006d36'
  secondary: '#c2c7d0'
  on-secondary: '#2c3138'
  secondary-container: '#42474f'
  on-secondary-container: '#b1b5bf'
  tertiary: '#f9faff'
  on-tertiary: '#29313a'
  tertiary-container: '#d6dfea'
  on-tertiary-container: '#5a636c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#60ff98'
  primary-fixed-dim: '#00e478'
  on-primary-fixed: '#00210c'
  on-primary-fixed-variant: '#005227'
  secondary-fixed: '#dee2ec'
  secondary-fixed-dim: '#c2c7d0'
  on-secondary-fixed: '#171c23'
  on-secondary-fixed-variant: '#42474f'
  tertiary-fixed: '#dae3ee'
  tertiary-fixed-dim: '#bec7d2'
  on-tertiary-fixed: '#141c24'
  on-tertiary-fixed-variant: '#3f4850'
  background: '#10141a'
  on-background: '#dfe2eb'
  surface-variant: '#31353c'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
  mono-data:
    fontFamily: monospace
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  sidebar-width: 280px
  gutter: 24px
  margin-page: 40px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The design system is engineered for high-stakes industrial monitoring, focusing on environmental accountability and operational efficiency for EV fleets. The brand personality is authoritative yet optimistic—blending the precision of data science with the vibrancy of a sustainable future. 

The aesthetic is **Dark Glassmorphism**, characterized by deep obsidian surfaces, ultra-refined borders, and high-frequency neon accents. It aims to evoke a sense of a "mission control center," where carbon intelligence is visualized through luminous layers and a "glowing" information architecture. This style ensures that critical data points—like emissions spikes or charging efficiencies—stand out against a silent, professional backdrop.

## Colors
The palette is rooted in a deep navy foundation to reduce eye strain during long-term monitoring. 

- **Foundation:** The `#0D1117` background provides the ultimate depth, allowing glass elements to layer effectively.
- **Sustainability Neon:** The primary `#00FF87` green is used sparingly for progress indicators, success states, and "Net Zero" milestones.
- **Alert Tiers:** High-contrast `#FF4D4D` (Danger) and `#FFB347` (Warning) are reserved strictly for actionable emission anomalies or hardware failures.
- **Overlays:** Card surfaces use `#161B22` with varying degrees of transparency to create a sense of physical stacks.

## Typography
This design system utilizes **Inter** for its exceptional legibility in data-heavy environments. 

- **Data Emphasis:** Large numeric values in KPI cards should use `display-lg` with a tight letter spacing to appear technical and impactful.
- **Hierarchy:** Use `label-md` in uppercase for section headers and metadata categories to create clear visual anchors.
- **Mobile Adaptation:** On mobile devices, headline sizes scale down significantly to ensure data tables and charts remain the primary focus.

## Layout & Spacing
The layout follows a **Fixed Sidebar + Fluid Content** model. 

- **Sidebar:** A constant 280px navigation rail on the left provides quick access to Fleet, Infrastructure, and Carbon Reports.
- **Grid:** Content is organized in a 12-column grid. KPI cards typically span 3 columns on desktop, while complex charts span 6 or 12.
- **Margins:** Generous 40px outer margins on desktop create a premium, "breathable" feel that prevents the data-dense UI from feeling overwhelming.
- **Mobile:** The sidebar collapses into a bottom navigation bar or a hamburger menu, and the page margins shrink to 16px.

## Elevation & Depth
Depth is achieved through **Glassmorphism** rather than traditional drop shadows.

- **Surface 0:** The base `#0D1117` background.
- **Surface 1 (Cards):** Background color `#161B22` at 60% opacity with a `20px` backdrop blur. A `1px` solid border using `#F0F6FC` at 10% opacity provides a "razor-thin" edge.
- **Surface 2 (Modals/Popovers):** Background color `#161B22` at 80% opacity with a `40px` backdrop blur. Use a subtle glow effect (box-shadow) using the primary neon green at 5% opacity for positive-context modals.

## Shapes
A "Rounded" strategy (8px base) is employed to soften the industrial nature of the data. 

- **Standard Elements:** Buttons, input fields, and small cards use `0.5rem` (8px).
- **Large Containers:** Dashboard widgets and main content areas use `rounded-xl` (1.5rem / 24px) to emphasize the "glass pane" aesthetic.
- **Data Points:** Pulse markers on maps and status indicators are perfectly circular (pill-shaped).

## Components
- **KPI Cards:** Glass containers featuring a large `display-lg` value. If the value is "Net Zero" or "Positive," the value text should have a subtle outer glow of the primary color.
- **Progress Rings:** High-contrast rings using a thick stroke. The background of the ring should be a dark `#30363D`, with the active progress in `#00FF87`.
- **Buttons:** 
    - *Primary:* Solid `#00FF87` with black text for high visibility.
    - *Secondary:* Ghost style with a `1px` border of the primary color and a subtle hover fill.
- **City Markers:** For the Indian fleet map, use a double-ring pulsing animation. The inner circle is solid, while the outer ring pulses outward with decreasing opacity to indicate real-time telemetry.
- **Data Tables:** Row separators should be 1px lines at 5% opacity. High-emission rows should have a very faint red-orange left border (4px) to draw the eye.
- **Charts:** Use thin, vector-based line charts. Area charts should use a vertical gradient from the primary/danger color (top) to transparent (bottom).