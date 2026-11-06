// Composition registry. Copy examples/demo/ to films/<slug>/ and register the new component below.
import React from 'react';
import {Composition, type CalculateMetadataFunction} from 'remotion';
import {Demo} from '../examples/demo/Demo';
import demoProps from '../examples/demo/props.json';
import {PoseSheet} from './hero/PoseSheet';
import type {FilmProps} from './types';

// Duration follows props.json, including overrides supplied with --props=other.json.
const fromProps: CalculateMetadataFunction<FilmProps> = ({props}) => ({durationInFrames: props.durationInFrames, fps: props.fps ?? 30});

export const Root = () => (
  <>
    <Composition id="Demo" component={Demo} width={1080} height={1920} fps={30} durationInFrames={demoProps.durationInFrames} defaultProps={demoProps as FilmProps} calculateMetadata={fromProps} />
    <Composition id="Poses" component={PoseSheet} width={1620} height={1080} fps={30} durationInFrames={120} />
  </>
);
