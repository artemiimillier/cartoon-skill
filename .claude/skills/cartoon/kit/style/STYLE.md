# Studio style: Cobalt on Graph Paper

This document defines the studio's visual system, implemented in `src/theme.ts`. When adapting a reference, keep these sections and update both the document and code.

Source: built-in style. Mood: an engineering notebook, clean and bright, with one bold pen color.

## Palette

| Role | Value | Use |
|---|---|---|
| Paper | #F4EFE4 | Scenes after the hook |
| Grid | rgba(35,70,255,.085) / .17 | Small 24 px and large 120 px squares |
| Ink | #15171E | Text, outlines, badges |
| Muted | #85817A | Headers and secondary labels |
| Accent | #2346FF | One key word, ring, underline, stamp, active row |
| Accent on dark | #93A9FF | Chalkboard and dark windows |
| Shadow | #1A2560 | Halftone shadows |
| Wipe | #101634 | Chapter transitions |
| Hook board | #26332F → #141B19 | Slate, with #EEEBE1 chalk |
| Windows | #1B1D25 / #262934 | Agent and input panels |
| Folder | #F0C35A | Folders and cardboard props |
| Warm | #FF7A45 | Occasional confetti and stars |

## Background and texture

Cream graph paper with grain and a soft vignette. The hook uses a chalkboard with dust and erased strokes. Cards attach with tape; illustrations draw themselves in chalk.

## Typography

| Role | Google Font | Treatment |
|---|---|---|
| Captions | Onest | 600, 74 px |
| Emphasis | Caveat | 700, 1.32× caption size, accent, −2° tilt |
| Headlines | Oswald | 700, 100–150 px, uppercase |
| Headers, paths, code | JetBrains Mono | 400–600 |
| Interfaces | Onest | 500–800 |

## Layout: 1080×1920

Header (133,122); captions (133,236), width 840; headline (110,500); scene y=600–1350; lower-left state x=110–520, y=1360–1650. Character eyes stay near (800,1590), through the final frame.

## Motion

Objects scale from 0.6 to 1 with overshoot over six to eight frames and leave over four or five. Use hard cuts. Headline letters enter every 35 ms with scale and blur. Caption words appear as spoken, settling from light to dark over 0.12 s. Cursor movement follows smooth curves; clicks compress the pointer and send out an accent ring.

## Transitions

Halftone dots grow in a wave to #101634. The next step badge appears large in the dark. Before the payoff, use a corner wipe and a two-frame dark flash.

## Shadows and outlines

Halftone shadows shift ten to eighteen pixels down and right. The character has a six-pixel white sticker outline and the same dotted shadow. Accent marks feel hand-drawn: imperfect looping rings and curved underlines.

## Matching library components

Chalk frames, taped cards, a route with step cards, agent/file windows, an oversized prompt field, a checklist advancing to completion, miniature scenes and magnifier, OK/DONE stamps, brief confetti and character rays.

## New components

None required for the built-in style. For a custom style, describe each missing component, its position, and its motion here before implementing it.

## Character

Beep is a vector robot with a cream body, dark screen-face, glowing #A6C4FF eyes and mouth, and an accent-colored antenna.

Character style: flat 2D vector cartoon, thick clean dark outline, cream and cobalt-blue accents, soft cel shading, friendly big-eyed proportions
