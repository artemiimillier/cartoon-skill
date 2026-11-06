// Central visual system: palette, fonts, and frame geometry.
// Change accent or background here; every scene inherits these values.
import {loadFont as loadOnest} from '@remotion/google-fonts/Onest';
import {loadFont as loadOswald} from '@remotion/google-fonts/Oswald';
import {loadFont as loadCaveat} from '@remotion/google-fonts/Caveat';
import {loadFont as loadMono} from '@remotion/google-fonts/JetBrainsMono';

// Fonts load before the first frame; see useFontsReady in Film.tsx.
const onest = loadOnest('normal', {weights: ['400', '500', '600', '700', '800'], subsets: ['latin']});
const oswald = loadOswald('normal', {weights: ['500', '700'], subsets: ['latin']});
const caveat = loadCaveat('normal', {weights: ['600', '700'], subsets: ['latin']});
const mono = loadMono('normal', {weights: ['400', '600'], subsets: ['latin']});

export const FONT = {
  caption: onest.fontFamily, // captions
  ui: onest.fontFamily, // labels inside schematic interfaces
  display: oswald.fontFamily, // headlines
  accent: caveat.fontFamily, // handwritten emphasis in accent color
  mono: mono.fontFamily, // headers, code, paths
};
export const fontsReady = () =>
  Promise.all([onest.waitUntilDone(), oswald.waitUntilDone(), caveat.waitUntilDone(), mono.waitUntilDone()]);

// One accent color for key words, rings, underlines, stamps, and active items.
export const T = {
  paper: '#F4EFE4', // cream graph paper
  gridMinor: 'rgba(35, 70, 255, .085)',
  gridMajor: 'rgba(35, 70, 255, .17)',
  ink: '#15171E',
  ink2: '#2A2D37',
  mute: '#85817A',
  ghost: '#C6C1B6',
  accent: '#2346FF', // cobalt
  accentDark: '#152FCC',
  accentSoft: '#DDE4FF',
  accentOnDark: '#93A9FF', // accent on chalkboard
  white: '#FFFFFF',
  card: '#FFFDF8',
  line: '#E0DACD',
  shadow: '#1A2560', // dark blue halftone shadow
  shutter: '#101634', // halftone chapter wipe
  board: '#26332F', // hook chalkboard
  boardDark: '#141B19',
  chalk: '#EEEBE1',
  boardText: '#F6F3EA',
  win: '#1B1D25',
  win2: '#262934',
  win3: '#353946',
  winText: '#E9E7E2',
  winMute: '#8E8C95',
  folder: '#F0C35A',
  folderDark: '#C9962A',
  tape: 'rgba(243, 231, 184, .88)',
  good: '#1FA35B',
  warm: '#FF7A45',
  pink: '#FF8FA8',
  hero: {
    shell: '#FFFDF5',
    shellShade: '#E7E0CF',
    visor: '#1A1E2C',
    glow: '#A6C4FF',
    cheek: '#FF8FA8',
    outline: '#15171E',
    antenna: '#2346FF',
  },
};

// 1080 by 1920: captions above, object center, state lower left, character lower right.
export const L = {
  W: 1080,
  H: 1920,
  fps: 30,
  eyebrow: {x: 133, y: 122},
  caption: {x: 133, y: 236, w: 840, size: 74},
  title: {x: 110, y: 500},
  stage: {top: 600, bottom: 1350},
  state: {x: 110, y: 1360, w: 440},
  hero: {x: 800, y: 1590, scale: 0.92}, // character eye anchor and scale
};
