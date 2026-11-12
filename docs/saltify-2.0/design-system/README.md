# Saltify 2.0 design system foundation

Issue: [#361](https://github.com/oss-slu/SpeechTranscription/issues/361) · Parent: [#350](https://github.com/oss-slu/SpeechTranscription/issues/350) · Consumers: [#358](https://github.com/oss-slu/SpeechTranscription/issues/358), [#351](https://github.com/oss-slu/SpeechTranscription/issues/351), [#352](https://github.com/oss-slu/SpeechTranscription/issues/352)

This folder defines the visual foundation for Saltify 2.0: semantic tokens, typography, the application shell, component states, and accessibility rules. It does not build pages or replace the current CustomTkinter app.

| File | Purpose |
| --- | --- |
| `design-tokens.json` | Single source of truth for every token, plus the contrast pairs that must pass. |
| `design-tokens.css` | Generated CSS custom properties. **Do not edit by hand.** |
| `preview.html` | Visual review page: shell, components and states in light and dark. Open it in a browser. |
| `../../../scripts/build_design_tokens.py` | Generates the CSS (`--check` to verify, `--report` to print contrast ratios). |
| `../../../tests/test_design_tokens.py` | Enforces theme parity, valid values, WCAG contrast and an up-to-date CSS file. |

### Why CSS custom properties before #348 is decided

All three runtimes under evaluation in [#365](https://github.com/oss-slu/SpeechTranscription/issues/365) (Electron + React/TypeScript, Tauri, a webview-based Python host) render HTML and CSS. CSS custom properties work in all of them with no build tooling. If #348 picks a stack that needs another format (TypeScript constants, Tailwind config), add an output to `build_design_tokens.py` that reads the same JSON. Don't fork the values.

### Workflow

```bash
# edit docs/saltify-2.0/design-system/design-tokens.json, then:
python scripts/build_design_tokens.py            # regenerate the CSS
python scripts/build_design_tokens.py --report   # see every contrast ratio
python -m pytest tests/test_design_tokens.py     # parity, contrast and staleness checks
```

---

## 1. Semantic tokens

Components use **semantic** names only (`--color-text-secondary`), never raw hex values or palette names (`blue-600`). Light and dark define exactly the same keys, and the tests fail if they drift.

### Theme selection

- `<html data-theme="light">` or `data-theme="dark"` is the user's explicit choice and always wins.
- With no attribute, the OS setting (`prefers-color-scheme`) decides.
- `<html data-motion="reduce">` is the in-app reduced-motion override (see §5).

### Colour groups

| Group | Tokens | Use |
| --- | --- | --- |
| Surfaces | `bg-app`, `bg-sidebar`, `bg-surface`, `bg-surface-raised`, `bg-surface-sunken`, `bg-hover`, `bg-pressed`, `bg-selected`, `bg-scrim` | Window background, sidebar, cards and panels, popovers, inputs and search fields, interaction fills, selected nav item or row, dialog backdrop |
| Text | `text-primary`, `text-secondary`, `text-muted`, `text-disabled`, `text-inverse`, `text-link`, `text-selected` | Body and titles, supporting text, timestamps and metadata, disabled labels, text on dark fills, links, selected nav item label |
| Borders | `border-subtle`, `border-default`, `border-strong` | Card dividers, panel outlines, **input and control boundaries** (`strong` passes 3:1) |
| Accents | `accent-primary(-hover/-pressed/-subtle)`, `accent-record(-hover)`, `accent-import(-hover)`, `on-accent` | Primary actions, play button, toggles; New Recording; Import Audio; text and icons on accent fills |
| Focus | `focus-ring` | 2px ring at 2px offset on every focusable element |
| Disabled | `disabled-bg`, `disabled-border`, `disabled-text` | All disabled controls |
| Status | `status-{success,info,review,warning,danger,neutral}-{bg,fg}` | Badges and inline status (see mapping below) |
| Errors | `error-border`, `error-text` | Invalid inputs and inline validation messages |
| Speakers | `speaker-{1..6}-{solid,bg,fg}` | Speaker dot (`solid`) and speaker chip (`bg`, `fg`) |
| Waveform | `waveform-played`, `waveform-unplayed`, `waveform-playhead` | Audio waveform |

### Session status → status token

| Session state | Token | Notes |
| --- | --- | --- |
| Transcribed | `success` | |
| Recorded, In Review | `info` | |
| Reviewed, Exported | `review` | |
| Draft, Recovered | `warning` | Recovered sessions also show an explanatory banner |
| Failed, Processing error | `danger` | Always paired with a message and a retry action |
| Not Transcribed, SALT, SUGAR, format tags | `neutral` | |

### Changes from the reference images (and why)

The references are a baseline, not a pixel spec. These deliberate changes keep text readable:

- **New Recording teal** is darkened from the reference's bright teal to `#0F766E`. White text on the original was about 2.5:1, which fails WCAG AA.
- **Import Audio purple** uses `#7C3AED` instead of a lighter violet, which gives 5.7:1 with white text.
- **Primary blue in dark mode** keeps `#2563EB` rather than a lighter blue, because white icons on the play button need 4.5:1.
- **Muted text** (timestamps, dates) is darker than a typical "slate-400", so it passes 4.5:1 on every surface it sits on, including selected rows.

### Speaker colours

Six speaker slots cover examiner, child, parent and three extras. Slot 1 is Examiner (blue), slot 2 is Child (teal) and slot 3 is Parent (orange), matching the references. **Colour is never the only signal:** speaker chips always show the speaker's label text, and the dot always appears next to a name. This matters for colour-blind users and for printed exports.

---

## 2. Typography and transcript readability

**Family:** Inter, bundled with the app (SIL Open Font License) because Saltify runs offline. Never load fonts from a CDN.
**Fallback:** `Segoe UI Variable Text` / `Segoe UI` on Windows, `-apple-system` / `SF Pro Text` on macOS, then `system-ui`. The layout must not break if Inter fails to load. All sizes have enough line height to absorb the metric differences.

| Role | Size / line height | Weight | Example |
| --- | --- | --- | --- |
| `display` | 28 / 36 | 700 | "Good morning!" |
| `heading` | 24 / 32 | 600 | Session title in the workspace header |
| `title` | 20 / 28 | 600 | Section titles ("Recent Sessions") |
| `title-sm` | 16 / 24 | 600 | Card titles, panel headings |
| `transcript` | 16 / 26 | 400 | Utterance text |
| `body` | 14 / 20 | 400 | Default UI text |
| `label` | 13 / 18 | 500 | Buttons, tabs, badges, form labels |
| `caption` | 12 / 16 | 400 | Metadata, helper text. **Minimum size anywhere in the UI.** |

### Transcript rules

1. Utterance text uses `transcript` (16/26), one step larger than UI body text, because transcription is the core reading task.
2. Utterances wrap and never truncate. Line length is capped at `--transcript-max-width` (72ch).
3. Timestamps use `font-variant-numeric: tabular-nums` so the columns line up, in `text-muted`.
4. Users can set transcript size from 14px to 22px in Settings, and line height scales with it (ratio about 1.6). UI chrome does not scale with this setting.
5. Coding marks such as SALT codes `[EW]` and `/ed` render inline in the same font. Highlight them with a `bg` tint, never by colour alone.
6. Clinical speech is shown exactly as transcribed. No auto-capitalisation, no smart quotes, and disfluencies ("um", "uh") are kept.

---

## 3. Shell

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Title bar / drag region (40px; 80px left inset on macOS for window controls) │
├────────────┬──────────────┬─────────────────────────────────┬────────────────┤
│ Sidebar    │ List pane    │ Main content                    │ Inspector      │
│ 232px      │ 248px        │ min 480px, fluid                │ 320px          │
│ (rail 64)  │ (workspace   │                                 │ (Speakers /    │
│            │  only)       │                                 │ Annotations /  │
│ Home       │              │                                 │ Notes)         │
│ Sessions   │              │                                 │                │
│ Record     │              │                                 │                │
│ Import     │              │                                 │                │
│ Analysis ▾ │              │                                 │                │
│ Exports    │              │                                 │                │
│ ...        │              │                                 │                │
│ Settings   │              │                                 │                │
│ Help       │              │                                 │                │
│ Storage    │              │                                 │                │
└────────────┴──────────────┴─────────────────────────────────┴────────────────┘
```

**Primary navigation:** Home, Sessions, Record, Import, Analysis (expands to SALT and SUGAR), Exports. **Footer:** Settings, Help, storage meter. The current location is marked with `bg-selected`, `text-selected` and `aria-current="page"`.

### Supported sizes (in CSS px, after OS scaling)

| Window width | Sidebar | List pane | Inspector |
| --- | --- | --- | --- |
| ≥ 1440 | 232 expanded | 248 docked | 320 docked |
| 1280–1439 | 232 expanded | 248 docked | 288 docked |
| 1100–1279 | 232 expanded | Collapses; opens as overlay | 288 docked |
| 1024–1099 | 64 icon rail (labels in tooltips) | Overlay | Drawer from right |
| < 1024 × 640 | Not supported for layout | The main region scrolls. Content is **never clipped** (see #327). | |

The window minimum is **1024 × 640 CSS px**. Users can collapse the sidebar and inspector at any size, and that choice is remembered per user.

### Display scaling

- Every dimension is in CSS px, which the runtime scales. Icons are SVG. No raster UI assets.
- The layout must be verified at **Windows 100 / 125 / 150 / 200 %** and **macOS 1× / 2×**. At 150% on a 1920×1080 display, the effective window is 1280×720, which must use the 1280 layout without clipping. At 200% on 1080p (960×540 effective), the window is below the minimum, so the content scrolls.
- Text must survive 200% browser or OS text zoom without overlapping (WCAG 1.4.4). Containers grow, they don't clip.

---

## 4. Component states

Every interactive component supports the states below. Components get state colours from tokens, never from ad-hoc opacity tricks.

| State | Visual treatment | Tokens |
| --- | --- | --- |
| Default | Resting appearance | Component-specific |
| Hover | Fill shifts one step | `bg-hover`, or `accent-*-hover` on filled buttons |
| Focus-visible | 2px ring, 2px offset. Keyboard focus only, so no ring on mouse click | `focus-ring`, `focus-ring-width`, `focus-ring-offset` |
| Pressed | Fill shifts two steps | `bg-pressed`, `accent-*-pressed` |
| Selected / current | Tinted fill + strong label | `bg-selected`, `text-selected` |
| Disabled | Flat fill, muted label, `cursor: not-allowed`, **still announced** by screen readers. Not focusable unless it explains why it's disabled (tooltip) | `disabled-*` |
| Loading | Label stays visible next to a spinner, width does not jump, `aria-busy="true"`, repeat clicks ignored | Current fill |
| Error | 1px `error-border` + inline message in `error-text` linked with `aria-describedby`. Never colour alone: an icon and text are always present | `error-*` |

### Component inventory

| Component | Variants | Required states | Min target |
| --- | --- | --- | --- |
| Button | primary, secondary, ghost, danger, icon | all | 32px (40px primary, 44px transport) |
| Action card | record, import, neutral | default, hover, focus, pressed, disabled | whole card |
| Nav item | expanded, rail | default, hover, focus, pressed, current | 36px tall |
| Text input / search | default, with icon | default, hover, focus, disabled, error | 32px tall |
| Select | | default, hover, focus, open, disabled, error | 32px |
| Tabs / segmented | | default, hover, focus, selected, disabled | 32px |
| Toggle | | off, on, hover, focus, disabled | 24px tall, 40px wide |
| List row (session, utterance) | | default, hover, focus, selected, playing (utterance) | 40px |
| Badge | status tokens | static (not interactive) | n/a |
| Menu / overflow (`⋯`) | | item: default, hover, focus, disabled, destructive | 32px |
| Dialog / confirmation | default, destructive | open with focus trapped; Esc closes unless it's a destructive confirm in progress | n/a |
| Tooltip | | appears after 500ms hover or on focus, dismissable with Esc | n/a |
| Toast | success, info, warning, danger | auto-dismiss ≥ 6s, pause on hover/focus, never the only place an error is reported | n/a |
| Empty / loading / error states | per region | have a title, one sentence of help, and one action | n/a |

**Destructive actions** (delete session, discard transcript edits) always use a confirmation dialog with a `danger` button whose label names the action ("Delete session", not "OK"). Focus starts on the safe action.

---

## 5. Accessibility rules

| Rule | Target | Enforced by |
| --- | --- | --- |
| Text contrast | ≥ 4.5:1 (WCAG 1.4.3 AA) | `contrastPairs.text` in tests |
| Non-text contrast: focus ring, input borders, toggles, speaker dots | ≥ 3:1 (WCAG 1.4.11) | `contrastPairs.nonText` in tests |
| Target size | ≥ 24×24 (WCAG 2.5.8); 32 default; 40 primary | `target-*` tokens, review |
| Focus visible | Every focusable element shows `focus-ring` | Review on `preview.html` |
| No colour-only meaning | Status, speakers and errors always have text or an icon | Review |
| Reduced motion | OS `prefers-reduced-motion` **or** in-app `data-motion="reduce"` sets all durations to 0ms. The waveform stops auto-scrolling and the playhead moves in steps. Progress bars still update | Generated CSS |
| Motion budget | Hover/press 120ms, panels 180ms, dialogs 260ms. Nothing over 300ms, nothing that flashes | Tokens |

### Keyboard model

| Keys | Action |
| --- | --- |
| `Tab` / `Shift+Tab` | Move between controls in reading order: sidebar → list pane → main → inspector |
| `F6` / `Shift+F6` | Jump between shell regions |
| `↑` `↓` | Move within lists (nav, sessions, utterances), with roving `tabindex` so each list is a single Tab stop |
| `Enter` | Open the selected item. `Space` toggles checkboxes and toggles |
| `Ctrl/⌘ + K` | Focus session search |
| `Ctrl/⌘ + 1…6` | Go to Home, Sessions, Record, Import, Analysis, Exports |
| `Space` (outside text fields) | Play / pause |
| `←` / `→` (outside text fields) | Seek −10s / +15s, matching the transport buttons |
| `Esc` | Close menu, tooltip, drawer or dialog, then return focus to the element that opened it |

Shortcuts that conflict with text editing (`Space`, arrows) are disabled whenever focus is in an input or editable utterance.

---

## 6. Visual review baseline

`preview.html` renders the shell and every component state from the generated CSS, with light and dark side by side and a reduced-motion switch. Use it to review this issue and as the reference for #358, #351 and #352.

Review checklist, compared with the four reference images attached to [#350](https://github.com/oss-slu/SpeechTranscription/issues/350) (also in `docs/saltify-2.0/images/` on the Saltify 2.0 plan branch):

- [ ] Dashboard hierarchy (greeting → action cards → recent sessions) reads the same in both themes
- [ ] Workspace regions (sessions list, header and tabs, player, transcript, inspector) map to the shell in §3
- [ ] Every status badge and speaker chip is legible in both themes
- [ ] Focus ring is visible on every control in both themes (tab through the page)
- [ ] Layout at 1024, 1280 and 1440 px wide; text zoom at 200%
- [ ] Windows at 100%, 150% and 200% scaling; macOS at 1× and 2×
- [ ] Reduced motion switch removes transitions

Attach screenshots of `preview.html` at 1280×800 in both themes to the PR.
