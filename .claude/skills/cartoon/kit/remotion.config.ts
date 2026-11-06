import {Config} from '@remotion/cli/config';

// Lossless PNG frames keep fine grid lines and halftone shadows sharp.
Config.setVideoImageFormat('png');
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer('angle');
Config.setEntryPoint('src/index.ts');
