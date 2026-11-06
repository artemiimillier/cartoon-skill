// Demo scene composition, pose track, and chapter wipes; all times come from cues.json.
import React from 'react';
import {Film, type Shutter} from '../../src/Film';
import type {Track} from '../../src/hero/HeroSticker';
import type {FilmProps} from '../../src/types';
import {Finale, Hook, Roadmap, Step1, Step2, Step3} from './scenes';

type C = Record<string, number>;

// Change pose roughly once per second according to meaning; see the method pose table.
const track = (c: C): Track => [
  [0, 'palm'],
  [c.explainers, 'point'],
  [c.nobody, 'surprise'],
  [c.how, 'shrug'],
  [c.here, 'palm'],
  [c.three, 'up'],
  [c.steps, 'wink'],
  [c.p1, 'up'],
  [c.put, 'palm'],
  [c.skill, 'point'],
  [c.folder, 'palm'],
  [c.project, 'wink'],
  [c.p2, 'up'],
  [c.give, 'palm'],
  [c.claude, 'point'],
  [c.one, 'up'],
  [c.make, 'point'],
  [c.script, 'wink'],
  [c.p3, 'up'],
  [c.maps, 'palm'],
  [c.words, 'point'],
  [c.draws, 'palm'],
  [c.scene, 'point'],
  [c.self, 'think'],
  [c.frames, 'wink'],
  [c.thats, 'celebrate'],
  [c.install, 'palm'],
  [c.try, 'celebrate'],
];

// Major steps get a halftone wipe and badge; the payoff gets a brief corner wipe.
const shutters = (c: C): Shutter[] => [
  {at: c.p1 - 0.42, badge: 1, total: 3, dir: 'right'},
  {at: c.p3 - 0.25, badge: 3, total: 3, dir: 'left'},
  {at: c.thats - 0.3, dir: 'corners', dur: 0.22, hold: 0.04},
];
const flashes = (c: C) => [c.thats - 0.12];
const glow = (t: number, c: C) => (t >= c.thats ? 0.8 : 0);
const board = (c: C) => c.here;

export const Demo: React.FC<FilmProps> = (p) => (
  <Film p={p} boardUntil={board} track={track} shutters={shutters} flashes={flashes} glow={glow}>
    <Hook />
    <Roadmap />
    <Step1 />
    <Step2 />
    <Step3 />
    <Finale />
  </Film>
);
