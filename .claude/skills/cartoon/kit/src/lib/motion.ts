// Scene time is seconds (frame/fps). Pure functions make every frame deterministic.
import type React from 'react';
import {Easing, interpolate} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Zero to one: quick launch and soft landing. */
export const ease = (t: number, a: number, b: number) =>
  interpolate(t, [a, b], [0, 1], {...clamp, easing: Easing.bezier(0.16, 1, 0.3, 1)});
/** Zero to one with easing at both ends, for cursors and movement. */
export const smooth = (t: number, a: number, b: number) =>
  interpolate(t, [a, b], [0, 1], {...clamp, easing: Easing.bezier(0.65, 0, 0.35, 1)});
/** Linear zero-to-one interpolation. */
export const lin = (t: number, a: number, b: number) => interpolate(t, [a, b], [0, 1], clamp);
export const mix = (a: number, b: number, k: number) => a + (b - a) * k;
/** Overshooting spring for object entrances. */
export const pop = (t: number, at: number, f = 15, d = 9) => {
  const x = t - at;
  return x < 0 ? 0 : 1 - Math.exp(-d * x) * Math.cos(f * x);
};
/** Zero-one-zero impulse of duration d. */
export const pulse = (t: number, at: number, d = 0.4) => Math.sin(lin(t, at, at + d) * Math.PI);
export const on = (t: number, a: number, b = 1e9) => t >= a && t < b;
/** Type characters between times a and b. */
export const typed = (s: string, t: number, a: number, b: number) =>
  [...s].slice(0, Math.round([...s].length * lin(t, a, b))).join('');
/** Damped shake after an impact. */
export const shake = (t: number, at: number, amp = 10, d = 0.25) => {
  const k = 1 - lin(t, at, at + d);
  return k <= 0 || t < at ? 0 : Math.sin(t * 90) * amp * k;
};

/** Pop from scale 0.6 to one with overshoot and slight blur; exit quickly at b. */
export const enter = (t: number, a: number, b = 1e9, from = 0.6): React.CSSProperties => {
  const k = pop(t, a, 16, 10);
  const out = lin(t, b, b + 0.16);
  return {
    opacity: Math.min(1, lin(t, a, a + 0.08)) * (1 - out),
    transform: `scale(${mix(from, 1, k) * (1 - 0.25 * out)})`,
    filter: `blur(${(1 - lin(t, a, a + 0.12)) * 8 + out * 6}px)`,
    display: t < a - 0.01 || t > b + 0.17 ? 'none' : undefined,
  };
};
/** Slide by (dx,dy), then exit at b. */
export const slideIn = (t: number, a: number, dx = 0, dy = 120, b = 1e9): React.CSSProperties => {
  const k = ease(t, a, a + 0.32);
  const out = lin(t, b, b + 0.16);
  return {
    opacity: lin(t, a, a + 0.1) * (1 - out),
    transform: `translate(${(1 - k) * dx}px,${(1 - k) * dy}px)`,
    display: t < a - 0.01 || t > b + 0.17 ? 'none' : undefined,
  };
};

/** Cursor keyframes [x,y,time], connected with smooth curves. */
export const curPath = (t: number, pts: [number, number, number][]): [number, number] => {
  let i = 0;
  while (i < pts.length - 1 && t >= pts[i + 1][2]) i++;
  if (i >= pts.length - 1) return [pts[pts.length - 1][0], pts[pts.length - 1][1]];
  const [x0, y0, t0] = pts[i];
  const [x1, y1, t1] = pts[i + 1];
  const k = smooth(t, t0, t1);
  return [mix(x0, x1, k), mix(y0, y1, k)];
};

/** Index of the most recent event, or minus one. */
export const stepOf = (t: number, times: number[]) => {
  let n = -1;
  times.forEach((x, i) => {
    if (t >= x) n = i;
  });
  return n;
};
