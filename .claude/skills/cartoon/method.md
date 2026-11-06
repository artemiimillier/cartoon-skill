# Cartoon production method

Read this file before storyboarding or editing scenes. Setup and reference selection are in [SKILL.md](SKILL.md). Run commands from the working studio, `cartoon/`. Scenes inherit the visual system from `style/STYLE.md` and `src/theme.ts`, and the character from `src/hero/current.ts`.

## Choose material that can move

This format works for a chain of visible actions: a tutorial, a workflow, a tool explanation, or a list of mistakes and fixes. Use one narrator and a concrete object for every phrase. For abstract arguments, two-person dialogue, or live-action stories, explain the mismatch and propose an action-based script first.

- **Supplied script:** keep the user's words. Split into caption phrases without silently rewriting. If it runs beyond roughly a minute, propose specific cuts and get agreement.
- **Reference video:** use the analysis from `xray_video`. Map actions every half-second, the opening mechanism, objects, speech relationships, and transitions. Borrow the structure, never footage, handles, metrics, text, or someone else's results.
- **Topic only:** write an original twenty-to-forty-five-second script with a hook, steps, and payoff. Obtain script approval before narration.

Write numbers as spoken words, such as “seventy-two.” Use familiar English product names, such as “Claude Code.”

## 1. Create a film folder

Copy `examples/demo/` to `films/<slug>/`: captions, cues, storyboard, scenes, event sounds, and the film component. Rename `Demo.tsx` to `Movie.tsx` and its exported component to a unique name. The relative `../../src/...` imports still work. Once timing exists, register it in `src/Root.tsx`:

```tsx
import {MyFilm} from '../films/<slug>/Movie';
import myProps from '../films/<slug>/props.json';
<Composition id="MyFilm" component={MyFilm} width={1080} height={1920} fps={30}
  durationInFrames={myProps.durationInFrames} defaultProps={myProps as FilmProps} calculateMetadata={fromProps} />
```

## 2. Storyboard words before animation

For each spoken phrase, record these columns in `storyboard.md`:

- Section header, for example `// 04 · step 2 · folder`.
- Main object and the action on each meaningful word.
- A headline of one to three words, with one highlighted word.
- Lower-left state: checklist, hint, counter, or resulting object.
- Character pose.

Aim for two to four visible events per second: entrance, click, checkmark, ring, typing, stamp, or headline change. A paragraph replacing an action is a defect. Choose events for their meaning, using the catalog below.

## 3. Captions and timing cues

`chunks.txt` has one caption phrase per line, usually twenty-five to forty characters and one or two screen lines. Break at meaning boundaries. `*word*` highlights the key word; use one emphasis per phrase.

`cues.json` maps names to `["word", occurrence]`, with occurrences counted from one. Scenes refer to these cues rather than hard-coded seconds. New narration then moves all dependent events together.

## 4. Voice and timing

Use the recorded voice choice in setup.json. Place the user's recording under `public/<slug>/voice.wav`, or synthesize one complete take:

```bash
python3 scripts/voice.py say films/<slug>/voice.txt -o public/<slug>/voice.mp3
```

This first prints the plan. Add `--yes` only within approved spending scope. Keep provider bytes unchanged; a new take gets a new filename. Synthetic timing is for drafts and the bundled silent-narration demo only.

```bash
python3 scripts/prep.py films/<slug>/chunks.txt films/<slug>/cues.json -o films/<slug>/props.json --synthetic
python3 scripts/prep.py films/<slug>/chunks.txt films/<slug>/cues.json -o films/<slug>/props.json --audio public/<slug>/voice.mp3 --whisper small
python3 scripts/prep.py films/<slug>/chunks.txt films/<slug>/cues.json -o films/<slug>/props.json --audio public/<slug>/voice.mp3 --words asr.json
```

Use one timing mode. `--whisper` needs faster-whisper. Audio inside `public/` attaches automatically. Captions always come from the script; ASR supplies timing only. Below 0.95 `chars_matched`, investigate wording, language, and numeric spellings before continuing. Compare printed cue times with the storyboard.

## 5. Build scenes

Use `src/lib` to draw each object in `scenes.tsx`.

- Each scene controls its own visibility: `const {t,c}=useFilm(); if(t<c.p1 || t>=c.p2) return null;`.
- Time comes from `c.name` plus a small offset. Missing cue names must fail visibly.
- Objects pop in with `pop` or `enter` and leave in four or five frames. Prefer hard cuts over crossfades.
- Show causality: cursor movement → click → menu or selection → result. Objects should appear for a reason.
- Keep the main scene at y=600–1350, headline around y=500, and state at x=110–520, y=1360–1650. The lower-right area belongs to the character.
- Put marks inside the moving object's container so they stay attached.
- Confetti and other celebration props should clear in one or two seconds.

In the film component, change pose roughly once a second when meaning warrants it. Use halftone wipes between major steps, a two-frame dark flash before the payoff, and brief character glow at moments of discovery. `boardUntil` controls the hook's chalkboard background.

## 6. Inspect frames before rendering

```bash
npx tsc -p tsconfig.json
node scripts/stills.mjs MyFilm out/stills --cues --sheet
```

Open every sheet and inspect it visually. Fix defects and repeat. Use `--frames 120,121,122` for a specific event or `--every 0.25` to inspect motion at the opening and transitions. Type checking alone does not prove a good frame.

## 7. Add event sounds

`sfx.json` lists sounds attached to cues: clicks, letter ticks, stamp impacts, transition swishes, and typing. Its schema is documented in `scripts/sfx.py`.

```bash
python3 scripts/sfx.py films/<slug>/props.json films/<slug>/sfx.json -o public/<slug>/sfx.wav
```

The script attaches audio to props. Use sounds for visible actions, without background music.

## 8. Render and deliver

```bash
npx remotion render src/index.ts MyFilm out/<slug>.mp4
```

For limited memory, render frame ranges such as `--frames=0-329` and `--frames=330-659`, then concatenate with ffmpeg. Mix narration near −14 LUFS with peak no higher than −1 dBFS; keep the original voice file intact. Check the final mix, not just the input file.

If private Telegram delivery is configured and authorized:

```bash
python3 scripts/send_telegram.py send out/<slug>.mp4 --caption-file films/<slug>/description.txt
```

A smaller Telegram copy must not replace the master. The user publishes the video.

## 9. Review the finished file

Apply the checklist below to the MP4. `scripts/compare.py` produces reference/ours sheets at matching events. Frame sheets verify sampled visuals; they do not replace checking the full audio or playback.

## Frame layout: 1080×1920

| Layer | Position | Treatment |
|---|---|---|
| Background | Full frame | Graph paper; chalkboard during the hook |
| Header | x=133, y=122 | Muted monospace section label |
| Captions | x=133, y=236, width=840 | Words appear as spoken; settle over 0.12 s |
| Headline | x=110, y=500 | Condensed bold, 100–150 px; one accent word |
| Scene | y=600–1350 | Main object and step badge |
| State | x=110–520, y=1360–1650 | Checklist, hint, count, result |
| Character | Eyes near (800,1590) | Chest crop, white sticker outline, visible through the last frame |

## Visual language

A dark step badge carries a white number and progress dots. Introduce it large inside a thin accent ring, then move it into the object's corner. Use accent color only for meaning: the active item, a key word, hand-drawn ring, underline, frame, checkmark, or stamp. Halftone shadows offset by ten to eighteen pixels connect cards, windows, and character. Chapter wipes grow dots into a dark screen with the next step badge.

## Word-to-action catalog

| Spoken beat | Visible action |
|---|---|
| Everyone does it; nobody shows how | Chalk sketches, a taped card, then a sheet with a large HOW? |
| Here are the steps | Cards fan onto a winding route; a ring jumps between them |
| Tool or app name | Dotted outline resolves into an icon with an underlined label |
| Don't do this | The rejected object slides in, gets crossed out, then moves aside |
| Interface action | Window, curved cursor path, click ring, menu, selection, result |
| Name it; type this | Letters enter a field; a hint points to the lit Enter key |
| Put it here; store files | A file follows the cursor into an opening folder; the path updates |
| Tools to do several jobs | Dashed question marks turn into specific tool cards |
| Ask it; write this | A large input bar types along with speech; a word counter updates |
| It handles the work | Checklist progresses from zero to complete with the current task beneath |
| For example | Large quotation marks and a prompt typed word by word |
| Check the result | A magnifier crosses frames; checkmarks and an OK stamp follow |
| Something is wrong | Before view, spoken correction, visible edit, after view |
| A number | Counter animates to the actual value |
| The fun part | Brief wipe, confetti, rays, and character glow |
| That's the process | Route returns; checks run through the steps; finish flag and DONE stamp |
| Final call to action | Show the exact requested action: button, description, or command |

Use only the devices that support the current phrase.

## Character

`src/hero/current.ts` selects the studio character. Undefined uses Beep; an atlas uses `atlasHero(rig)`. Both share pose names. Beep's mouth uses `props.amplitude`, or word timing when no audio exists; it also blinks, breathes, and animates its equalizer. The `Poses` composition shows all poses.

| Meaning | Pose |
|---|---|
| First, announcement, main idea | up |
| Explanation or list | palm |
| Point to an object | point |
| Discovery or payoff | celebrate |
| Surprise or nobody | surprise |
| Check, doubt, something wrong | think |
| No need, uncertainty | shrug |
| Step complete | wink |
| Rest | neutral |

The atlas schema is documented in `src/hero/AtlasHero.tsx`. Install it with `scripts/atlas_rig.py --install`, or pass `hero={atlasHero(rig)}` to one Film. Mouth and blink overlays depend on accurately inspected anchors.

## Library

- Timing: `ease`, `smooth`, `lin`, `mix`, `pop`, `pulse`, `shake`, `typed`, `enter`, `slideIn`, `curPath`, `stepOf`.
- Frame: `GridPaper`, `Chalkboard`, `ChalkDefs`, `Eyebrow`, `Caption`, `Display`, `Badge`, `StepBadge`, `Halftone`, `HT`, `dots`, `Abs`.
- Marks: `Ring`, `Frame`, `Underline`, `Strike`, `ArrowUp`, `Mark`, `CheckBox`, `Stamp`, `Particles`, `Rays`, `Tip`, `Key`, `Pill`, `Counter`, `Caret`.
- Interfaces: `Cursor`, `AppWindow`, `AgentHello`, `FileWindow`, `Folder`, `FileCard`, `Phone`, `Browser`, `InputBar`, `Spinner`, `Checklist`.
- Props: `Tape`, `PaperSheet`, `Sticky`, `Magnifier`, `Flag`, `StepCard`, `Road`, `MiniScene`, `ChalkFrame`.

Draw missing objects with SVG/CSS. Reusable ones can move into `src/lib`. Schematic interfaces must not be presented as authentic screenshots or fabricated product evidence.

## Frequent defects

- Headlines overlap a step badge or edge: reduce size and keep the right edge within roughly 880 px.
- Windows touch headlines: start windows no higher than y≈650.
- Card labels wrap: use length-aware sizes and `whiteSpace:'nowrap'`.
- Important information sits behind the character: move it left.
- A mark detaches from its object: place it inside the same container.
- A later headline word appears too soon: give that segment its own `at`.
- Nothing changes for over half a second: add a meaningful cursor move, tick, ring, or typing event.
- Several accents compete: keep one focal accent.
- Celebration props linger: clear them after one or two seconds.
- Captions cover the headline: shorten caption chunks.

## Final checklist

- [ ] Visible action follows the meaning throughout; no unexplained static gaps.
- [ ] Captions, object, state, and character are present and readable.
- [ ] Accent, badges, and chapter transitions form a consistent visual system.
- [ ] Every frame sheet was inspected and defects fixed.
- [ ] Captions match the actual narration; the final voice and effects are audible and synchronized.
- [ ] Any reference supplied mechanics, not borrowed identity, footage, or results.
