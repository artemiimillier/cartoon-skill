// Film shell: backgrounds, scenes, captions, character, wipes, flashes, and audio.
// Scenes are Film children; access time and cues with useFilm().
import React, {useEffect, useMemo, useState} from 'react';
import {AbsoluteFill, Html5Audio, cancelRender, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Badge, Caption, ChalkDefs, Chalkboard, GridPaper, Halftone} from './lib/frame';
import {lin, mix, pop} from './lib/motion';
import {HeroSticker, type HeroRender, type Track} from './hero/HeroSticker';
import {HERO} from './hero/current';
import {T, fontsReady} from './theme';
import {FilmContext, strictCues, type FilmProps} from './types';

/** Wait for fonts before frame zero. Fail clearly on a network error instead of rendering fallback fonts. */
export const useFontsReady = () => {
  const [h] = useState(() => delayRender('Loading theme fonts (theme.ts)'));
  useEffect(() => {
    fontsReady()
      .then(() => continueRender(h))
      .catch((e) => cancelRender(new Error('Fonts failed to load: allow access to fonts.gstatic.com. ' + String(e))));
  }, [h]);
};

/** Halftone chapter wipe; badge is the next step number shown in darkness. */
export type Shutter = {at: number; dur?: number; hold?: number; dir?: 'left' | 'right' | 'center' | 'corners'; badge?: number; total?: number};

export const Film = ({p, track, boardUntil = 0, shutters = [], flashes = [], glow, hero, children}: {
  p: FilmProps;
  /** Character pose track using cue times in seconds. */
  track: (c: Record<string, number>) => Track;
  /** Keep the hook chalkboard and light captions until this time. */
  boardUntil?: number | ((c: Record<string, number>) => number);
  shutters?: Shutter[] | ((c: Record<string, number>) => Shutter[]);
  /** Two-frame dark flash before the payoff. */
  flashes?: number[] | ((c: Record<string, number>) => number[]);
  /** Character glow from zero to one for discovery and the finale. */
  glow?: (t: number, c: Record<string, number>) => number;
  /** Optional per-film character; otherwise use src/hero/current.ts. */
  hero?: HeroRender;
  children: React.ReactNode;
}) => {
  useFontsReady();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const c = useMemo(() => strictCues(p.cues), [p.cues]);
  const board = typeof boardUntil === 'function' ? boardUntil(c) : boardUntil;
  const onBoard = t < board;
  const tr = useMemo(() => [...track(c)].sort((a, b) => a[0] - b[0]), [track, c]);
  const sh = useMemo(() => (Array.isArray(shutters) ? shutters : shutters(c)), [shutters, c]);
  const fl = useMemo(() => (Array.isArray(flashes) ? flashes : flashes(c)), [flashes, c]);
  return (
    <FilmContext.Provider value={{t, frame, c, p}}>
      <AbsoluteFill style={{background: T.paper, overflow: 'hidden'}}>
        {onBoard ? <Chalkboard /> : <GridPaper t={t} />}
        <ChalkDefs />
        {children}
        <Caption p={p} t={t} light={onBoard} />
        <HeroSticker t={t} fps={fps} track={tr} words={p.words} amp={p.amplitude} glow={glow ? glow(t, c) : 0} render={hero ?? HERO} />
        {sh.map((h, i) => {
          const dur = h.dur ?? 0.32;
          const hold = h.hold ?? 0.12;
          const show = h.badge !== undefined && t >= h.at + dur * 0.7 && t < h.at + dur + hold + dur * 0.4;
          return (
            <React.Fragment key={i}>
              <Halftone t={t} at={h.at} dur={dur} hold={hold} dir={h.dir ?? 'right'} />
              {show && (
                <div style={{position: 'absolute', left: 540 - 50, top: 900 - 53, zIndex: 95, transform: `scale(${mix(1.6, 2.6, pop(t, h.at + dur * 0.7, 14, 10))}) rotate(-4deg)`, transformOrigin: '50% 50%', opacity: 1 - lin(t, h.at + dur + hold, h.at + dur + hold + dur * 0.4)}}>
                  <Badge n={h.badge!} total={h.total ?? 6} size={100} />
                </div>
              )}
            </React.Fragment>
          );
        })}
        {fl.map((at, i) => (t >= at && t < at + 2 / fps ? <div key={i} style={{position: 'absolute', inset: 0, background: T.shutter, zIndex: 96}} /> : null))}
        {p.audio ? <Html5Audio src={staticFile(p.audio)} /> : null}
        {p.sfx ? <Html5Audio src={staticFile(p.sfx)} volume={p.sfxVolume ?? 0.6} /> : null}
      </AbsoluteFill>
    </FilmContext.Provider>
  );
};
