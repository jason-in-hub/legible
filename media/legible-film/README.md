# legible README film

A 20 s, 1200×600, 30 fps silent loop, made once with [cinetic](https://github.com/Leonxlnx/cinetic) v1.5.1.

- `script.txt` holds the on-screen lines, checked with cinetic's `copy-check.py` (verdict: clear).
- `Legible.tsx` is the single composition. It imports the cinetic Remotion starter's `brand/tokens`, `lib/anim`, `lib/measure` and `lib/FontGate`, so it builds only inside a cinetic scaffold.

To rebuild it:

```bash
npx skills add Leonxlnx/cinetic
```

```bash
bash ~/.claude/skills/cinetic/scripts/new-film.sh films/legible --name legible --template none --fps 30 --size 1200x600
```

Copy `Legible.tsx` into `films/legible/src/`. Add `stall: '#C4343F'` to `C` in `src/brand/tokens.ts`, then register the composition in `src/Root.tsx`:

```tsx
<Composition id="Legible" component={Legible} durationInFrames={LTOTAL} fps={LFPS} width={LW} height={LH} />
```

Render the MP4, then turn it into a GIF:

```bash
npx remotion render Legible out/legible.mp4
```

```bash
ffmpeg -i out/legible.mp4 -vf "fps=20,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=48:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" out/legible.gif
```

Cinetic steps that were skipped, and why: music, sound kit and the audio gates (`forensics.py` audio, `check-sync.py`), because a README GIF is silent. The direction deck and scene bank were also skipped, because the film is a single type-led exhibit.
