# AgriVision AI — Design Language

> Derived from the AgriVision AI Stitch mockups (Style Guide, Login, Dashboard, Scan Tomato Leaves, Detection Results). This document is the single source of truth for visual and interaction design across the product. It is written to map directly onto the project's stack: **React + TypeScript + Tailwind CSS + Framer Motion**.

---

## 1. Design Principles

- **Dark-first, field-ready.** The core app runs on a near-black canvas so imagery (drone/leaf photos) and status colors pop, and screens stay legible in bright outdoor sunlight and low-light barns alike.
- **Green as trust, not decoration.** Deep forest green is the brand anchor (primary actions, active states); brighter greens are reserved for "good news" (healthy status, high confidence, success).
- **Calm authority.** Generous spacing, soft rounded corners, and restrained color usage keep a technical AI product feeling approachable to non-technical farmers.
- **One primary action per screen.** Every screen has exactly one high-emphasis filled button (Sign In, Scan Now, Analyze Plant Health, View Treatment Plan) — everything else is secondary/outlined or tertiary/text.

---

## 2. Color Palette

### 2.1 Brand Colors

| Token | Hex | Usage |
|---|---|---|
| `primary` | `#0B2B1E` | Deepest brand green — primary buttons, active nav, high-emphasis fills |
| `primary-600` | `#1B4332` | Primary hover/pressed, card headers on dark bg |
| `primary-500` | `#297B5C` | Mid-tone brand green — secondary CTAs ("Scan Now"), icon accents |
| `primary-400` | `#34A65F` | Success/confidence rings, active progress states |
| `primary-100` | `#A2F4C8` | Healthy-status pill background |
| `secondary-gradient` | `#002114 → #CFFBE2` | Decorative gradient for hero/illustration accents, chart fills |

### 2.2 Accent (Tertiary)

| Token | Hex | Usage |
|---|---|---|
| `accent` | `#DDA15E` | Weather/tips icon backgrounds, informational highlights, priority flags |
| `accent-600` | `#8A5A2A` | Accent text on light chips |

### 2.3 Neutrals

| Token | Hex | Usage |
|---|---|---|
| `bg-canvas` | `#1E1F22` | App shell / outer background |
| `bg-base` | `#202124` | Screen background (Dashboard, Scan, Results) |
| `bg-surface` | `#F8F9FA` | Light surfaces (Login card, form screens) |
| `bg-card` | `#2A2E2B` | Card / panel background on dark screens |
| `border-subtle` | `#3A3F3C` | Card borders, dividers on dark bg |
| `border-light` | `#E1E3E1` | Card borders, dividers on light bg |
| `text-primary` | `#F5F7F6` | Headings/body on dark bg |
| `text-secondary` | `#9AA39D` | Muted/meta text on dark bg |
| `text-inverse` | `#14171A` | Body text on light bg |
| `disabled` | `#767D79` | Disabled buttons/inputs |

### 2.4 Status / Semantic Colors

| Token | Hex | Usage |
|---|---|---|
| `status-success-bg` | `#A2F4C8` | "Healthy" badge background |
| `status-success-text` | `#0B3D24` | "Healthy" badge text |
| `status-danger-bg` | `#FFDAD6` | "Blight" / disease badge background |
| `status-danger-text` | `#7A1F17` | "Blight" / disease badge text |
| `status-warning-bg` | `#FBD2CE` | "High Priority" badge background |
| `status-warning-text` | `#7A3A17` | "High Priority" badge text |
| `status-info-ring` | `#34A65F` | Confidence-score circular gauge |

### 2.5 Tailwind Config Tokens

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0B2B1E",
          600: "#1B4332",
          500: "#297B5C",
          400: "#34A65F",
          100: "#A2F4C8",
        },
        accent: { DEFAULT: "#DDA15E", 600: "#8A5A2A" },
        surface: {
          canvas: "#1E1F22",
          base: "#202124",
          card: "#2A2E2B",
          light: "#F8F9FA",
        },
        border: { subtle: "#3A3F3C", light: "#E1E3E1" },
        text: {
          primary: "#F5F7F6",
          secondary: "#9AA39D",
          inverse: "#14171A",
        },
        status: {
          successBg: "#A2F4C8", successText: "#0B3D24",
          dangerBg: "#FFDAD6", dangerText: "#7A1F17",
          warningBg: "#FBD2CE", warningText: "#7A3A17",
        },
      },
      borderRadius: { xl: "16px", "2xl": "20px", pill: "999px" },
    },
  },
};
```

---

## 3. Typography

A modern, rounded geometric sans-serif is used throughout (target: **Manrope** or **Plus Jakarta Sans** for headings, **Inter** for body/UI text — both free, high-legibility, agri-tech-appropriate).

```css
--font-heading: 'Manrope', 'Plus Jakarta Sans', sans-serif;
--font-body: 'Inter', sans-serif;
```

| Style | Font / Weight | Size | Line-height | Usage |
|---|---|---|---|---|
| Display | Heading / Bold (700) | 28px | 34px | Screen hero text ("Welcome back, Farmer!") |
| H1 | Heading / Bold (700) | 22px | 28px | Section titles ("Plant Health Scan") |
| H2 | Heading / Semibold (600) | 18px | 24px | Card titles, disease names |
| Body | Body / Regular (400) | 15px | 22px | Paragraph copy, descriptions |
| Body Small | Body / Regular (400) | 13px | 18px | Meta text, timestamps, helper text |
| Label | Body / Medium (500) | 12px | 16px | Badges, tags, form labels, nav labels |
| Button | Body / Semibold (600) | 15px | 20px | Button text, uppercase tracking optional for secondary CTAs |

**Rules:**
- Headings are always `text-primary` (near-white) on dark screens, `text-inverse` on light screens — never mid-gray.
- Only one Display/H1 per screen.
- Numbers that matter (confidence %, temperature) are set in a bold, slightly larger weight than surrounding text to draw the eye.

---

## 4. Layout & Grid

- **Mobile-first, single-column.** All primary screens (Login, Dashboard, Scan, Results) are designed at a ~390px mobile viewport with a persistent bottom tab bar.
- **Safe content width:** 16–20px horizontal margin on all screens.
- **Vertical rhythm:** content stacks in cards/sections separated by 24px; related elements within a card separated by 8–12px.
- **Screen anatomy (top to bottom):**
  1. Status bar (system)
  2. Top App Bar (logo + 1–2 icon actions)
  3. Hero / context block (greeting, weather, or subject image)
  4. Primary action (one filled button, full-width or prominent)
  5. Secondary content (lists, cards, tips)
  6. Bottom Tab Bar (fixed)

### Breakpoints (for the responsive web build)

| Breakpoint | Width | Layout change |
|---|---|---|
| `mobile` | < 640px | Single column, bottom tab nav, full-width buttons (as designed) |
| `tablet` | 640–1024px | Two-column content (e.g., image + details side-by-side), bottom nav becomes optional side rail |
| `desktop` | > 1024px | Top app bar becomes full nav bar with inline links; bottom tab bar is replaced by a persistent left sidebar; content max-width 1120px, centered |

---

## 5. Spacing System

8px base grid:

| Token | Value | Usage |
|---|---|---|
| `space-1` | 4px | Icon-to-label gap, tight badge padding |
| `space-2` | 8px | Default gap between related inline elements |
| `space-3` | 12px | Input internal padding, small card padding |
| `space-4` | 16px | Standard card padding, screen horizontal margin |
| `space-6` | 24px | Gap between major page sections |
| `space-8` | 32px | Section-to-section on larger screens / desktop |
| `space-12` | 48px | Hero/top spacing, empty-state padding |

---

## 6. Buttons

| Variant | Background | Text | Border | Radius | Usage |
|---|---|---|---|---|---|
| **Primary** | `primary` `#0B2B1E` | `#FFFFFF` | none | `pill` (999px) or 14px | Main CTA: "Sign In", "Scan Now", "View Treatment Plan" |
| **Secondary (Outlined)** | transparent / `surface.light` | `primary-600` | 1.5px `primary-600` | 14px | "Upload from Gallery", "Download AI Report (PDF)" |
| **Tertiary (Text/Social)** | `#FFFFFF` or `surface.card` | `text-inverse` / `text-primary` | 1px `border-light` | 12px | Social login (Google/Apple) |
| **Disabled** | `disabled` `#767D79` | `#D8D8D8` | none | 14px | Inactive until precondition met ("Analyze Plant Health" before upload) |
| **Icon Button** | transparent, circular | icon color | none | `pill` | Top-bar actions (search, notifications, avatar) |

**Anatomy:** icon (optional, 18–20px) + label, 12–16px horizontal padding beyond text, 48px minimum touch target height.

**States:**
- Default → Hover: darken fill 8% / lighten border.
- Pressed: scale to 97%, 100ms ease-out (Framer Motion `whileTap={{ scale: 0.97 }}`).
- Disabled: 60% opacity on label, no pointer events, no shadow.
- Loading: label replaced by spinner, button width preserved (no layout shift).

```tsx
// Example Tailwind classes
<button className="w-full h-12 rounded-full bg-primary text-white font-semibold
  active:scale-97 transition-transform disabled:bg-disabled disabled:opacity-60">
  Sign In
</button>
```

---

## 7. Cards

- **Radius:** 16–20px (`rounded-2xl`).
- **Background:** `surface.card` (`#2A2E2B`) on dark screens, `#FFFFFF` on light screens.
- **Border:** 1px `border-subtle`, used instead of heavy shadow to keep the dark theme flat and calm.
- **Padding:** 16px standard, 20px for hero/feature cards.
- **Elevation:** avoid drop shadows on dark backgrounds (they don't read); use a subtle 1px lighter border or 2–4% white overlay instead. Light-theme cards may use a soft `0 2px 8px rgba(0,0,0,0.06)` shadow.
- **Card types observed:**
  - **Info card** — icon + title + description (Tips for Accuracy, About [Disease]).
  - **Stat card** — large number/ring + label (Confidence Score, Humidity/Temp).
  - **List-item card** — thumbnail + title + status badge + chevron (Recent Activity, Prediction History).
  - **Upload card** — dashed 2px border, centered icon + copy, drag-and-drop target state (border color shifts to `primary-400` on drag-over).

```tsx
<div className="rounded-2xl bg-surface-card border border-border-subtle p-4">
  <div className="flex items-center gap-3">
    <IconCircle />
    <div>
      <h3 className="text-text-primary font-semibold">Optimal Lighting</h3>
      <p className="text-text-secondary text-sm">Avoid harsh shadows or backlight during capture.</p>
    </div>
  </div>
</div>
```

---

## 8. Badges & Status Pills

Rounded-pill, compact, always icon-or-dot + label:

| Type | Background | Text | Example |
|---|---|---|---|
| Success | `status-success-bg` | `status-success-text` | "Healthy · 96% Confidence" |
| Danger | `status-danger-bg` | `status-danger-text` | "Blight" |
| Warning | `status-warning-bg` | `status-warning-text` | "High Priority" |

Padding: 4px vertical, 10px horizontal. Font: Label style, 12px, medium weight. Radius: `pill`.

---

## 9. Navigation

### 9.1 Top App Bar

- Height: 56px.
- Left: logo mark (leaf icon) + wordmark "AgriVision AI", Heading/Semibold, 16px.
- Right: 1–2 circular icon buttons (search, notification bell) or avatar, 40×40px tap target.
- Background matches screen background (no separate bar color) with a 1px `border-subtle` bottom hairline on scroll.

### 9.2 Bottom Tab Bar

- Fixed, height 64–72px, background `surface.card` with top hairline border.
- 5 items: **Home · Scan · History · Tips · Profile**.
- Active item: icon + label in `primary-400`; inactive: icon + label in `text-secondary`.
- Center "Scan" item may be visually emphasized (filled circle background in `primary`) as the app's core action, camera-app style.
- Icon size 22–24px, label 11px below, 4px gap.

### 9.3 Web Navigation (Desktop Adaptation)

For the responsive web build, promote the bottom tab bar to a **left sidebar** (≥1024px): same 5 items stacked vertically, logo pinned at top, user/profile pinned at bottom. Top app bar becomes a slim breadcrumb/search/notification strip.

---

## 10. Footer (Web / Marketing Pages)

The mobile app itself has no footer (bottom nav owns that space), but marketing/landing and admin-panel web pages should use a consistent footer:

- Background: `surface.base` (`#202124`), 1px top border `border-subtle`.
- Layout: 4-column grid on desktop (Product, Company, Resources, Legal) collapsing to an accordion on mobile.
- Includes: logo + one-line mission statement, social icons (in `text-secondary`, hover → `primary-400`), copyright line in Body Small / `text-secondary`.

---

## 11. Iconography

- Style: outline icons, 1.5–2px stroke, rounded joins (Phosphor / Lucide-style) — matches the rounded typography and pill buttons.
- Sizes: 16px (inline/badges), 20px (buttons), 24px (nav/top bar).
- Color inherits from context: `text-primary`/`text-secondary` on neutral use, `primary-400` on active/success, `accent` on informational/tips.

---

## 12. Motion & Animation

The mockups are static, so the following are **interaction guidelines inferred from the UI's affordances** (progress rings, drag targets, state changes) — implement with Framer Motion.

| Interaction | Motion |
|---|---|
| Screen transitions | 220ms ease-in-out slide/fade between tab-bar destinations; modal/detail screens push in from the right, 280ms |
| Button press | Scale to 0.97, 100ms ease-out, spring back on release |
| Card entrance (lists) | Staggered fade+slide-up, 20px offset, 40ms stagger per item |
| Drag-and-drop upload zone | Border color + background tint animate to `primary-400` over 150ms on drag-over; scale 1.02 pulse on drop |
| Confidence score ring | Animate stroke-dashoffset from 0 → target % over 900ms ease-out on results reveal |
| Disabled → enabled button | Background color + opacity cross-fade 200ms once precondition is met (e.g., image selected) |
| Badge/status reveal | Pop-in: scale 0.8 → 1 with slight overshoot (spring, stiffness 300, damping 20) |
| Toast/alert (weather, errors) | Slide down from top, auto-dismiss fade after 4s |

```tsx
// Example: confidence ring animation
<motion.circle
  initial={{ strokeDashoffset: circumference }}
  animate={{ strokeDashoffset: circumference * (1 - confidence) }}
  transition={{ duration: 0.9, ease: "easeOut" }}
/>
```

Keep motion **purposeful and quick** (150–300ms for most UI, up to 900ms only for data-reveal moments like the confidence gauge) — this is a field tool, not a showcase; nothing should slow down a farmer trying to get an answer.

---

## 13. Mobile Responsiveness

The product is **mobile-first by design intent** (all core screens are phone-sized in the source mockups). Responsive rules for the companion web app:

- **< 640px (mobile):** exact mockup fidelity — single column, full-width primary buttons, bottom tab bar, 16px screen margins.
- **640–1024px (tablet):** cards may adopt a 2-column masonry (e.g., Recent Activity grid); Scan screen splits into upload zone (left) + tips panel (right); bottom nav remains but items gain more horizontal padding.
- **> 1024px (desktop):** left sidebar navigation replaces bottom tab bar; max content width 1120px centered with 32–48px gutters; Detection Results screen becomes a 2-pane layout (image + map on left, diagnosis + recommendations on right); hover states become meaningful (buttons, cards get hover elevation/border-brighten since mouse input is available).
- **Touch targets:** minimum 44×44px on all breakpoints, even desktop, since the primary field-use case is touch (tablet-in-hand at the farm).
- **Images:** drone/leaf photos use `object-fit: cover` with a fixed aspect ratio (4:3) at all breakpoints to keep card grids aligned.

---

## 14. Accessibility Notes

- Maintain WCAG AA contrast: verify `text-secondary` (`#9AA39D`) on `bg-base` (`#202124`) — passes for body text (≥4.5:1); do not drop further.
- Status must never be conveyed by color alone — pair every badge with an icon or label text (already true of "Healthy · 96%" pattern; keep it that way for "Blight"/"High Priority" too).
- Disabled buttons should carry `aria-disabled` and a visible reason (helper text) rather than silent inactivity.
- Focus states: 2px `primary-400` outline offset 2px, visible on all interactive elements for keyboard/tablet-with-stylus use.

---

## 15. Quick-Reference Token Sheet

```css
:root {
  /* Brand */
  --color-primary: #0B2B1E;
  --color-primary-600: #1B4332;
  --color-primary-500: #297B5C;
  --color-primary-400: #34A65F;
  --color-primary-100: #A2F4C8;
  --color-accent: #DDA15E;

  /* Neutrals */
  --color-bg-canvas: #1E1F22;
  --color-bg-base: #202124;
  --color-bg-surface: #F8F9FA;
  --color-bg-card: #2A2E2B;
  --color-border-subtle: #3A3F3C;
  --color-border-light: #E1E3E1;
  --color-text-primary: #F5F7F6;
  --color-text-secondary: #9AA39D;
  --color-text-inverse: #14171A;
  --color-disabled: #767D79;

  /* Status */
  --color-success-bg: #A2F4C8;
  --color-success-text: #0B3D24;
  --color-danger-bg: #FFDAD6;
  --color-danger-text: #7A1F17;
  --color-warning-bg: #FBD2CE;
  --color-warning-text: #7A3A17;

  /* Type */
  --font-heading: 'Manrope', 'Plus Jakarta Sans', sans-serif;
  --font-body: 'Inter', sans-serif;

  /* Radius */
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 20px;
  --radius-pill: 999px;

  /* Spacing */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px;
}
```

---

*Source: AgriVision AI Stitch project mockups (Style Guide, Login, Dashboard, Scan Tomato Leaves, Detection Results screens). Colors sampled directly from mockup pixels; typography and motion values are best-practice recommendations consistent with the observed visual style.*
