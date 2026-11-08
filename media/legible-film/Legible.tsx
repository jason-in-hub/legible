import React, { useMemo } from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { C, FONT } from './brand/tokens';
import { FontGate } from './lib/FontGate';
import { E, clamp, mix, prog } from './lib/anim';
import { measureTracked } from './lib/measure';

// legible - a README feature loop (cinetic format "Feature loop": reads muted, GIF out).
// One element is carried through the whole film: the reader's eye, an underline that steps word by word.
// It stalls (stall red) where a reader would stall, jumps back to reread, then glides through the plain
// version (accent) in one pass. On the end card it becomes the underline under the name.

export const LW = 1200;
export const LH = 600;
export const LFPS = 30;

// ---- timeline (absolute frames, 30 fps) --------------------------------------------------------------------------
const T = {
  l1In: 0, l1Out: 46, l2In: 54, l2Out: 104, // the statement and the promise
  aIn: 112, aRead: 124, aStep: 7, aBack: 172, aFix: 202, aGlide: 222, aOut: 280, // exhibit A: prediction
  bIn: 288, bRead: 300, bStep: 6, bBack: 372, bFix: 404, bGlide: 424, bOut: 500, // exhibit B: memory
  end: 508, total: 600,
};
export const LTOTAL = T.total;

type Tok = { t: string; x: number; y: number; w: number };
type Lay = { toks: Tok[]; size: number };

const W8 = 470; // the voice's weight for exhibits
const TRACK = -0.012;

/** Words centred in rows round cy; `rows` are given explicitly, or wrapped greedily to maxW. */
const layout = (words: string[] | string[][], size: number, cy: number, maxW = 1040, weight = W8): Lay => {
  const sp = measureTracked('x x', size, weight, TRACK) - measureTracked('xx', size, weight, TRACK);
  const wOf = (s: string) => measureTracked(s, size, weight, TRACK, FONT.text, { trailing: false });
  let rows: string[][];
  if (Array.isArray(words[0])) rows = words as string[][];
  else {
    rows = [[]];
    let cur = 0;
    for (const w of words as string[]) {
      const ww = wOf(w);
      if (rows[rows.length - 1].length && cur + sp + ww > maxW) {
        rows.push([]);
        cur = 0;
      }
      cur += (rows[rows.length - 1].length ? sp : 0) + ww;
      rows[rows.length - 1].push(w);
    }
  }
  const lead = size * 1.45;
  const top = cy - ((rows.length - 1) * lead) / 2;
  const toks: Tok[] = [];
  rows.forEach((r, ri) => {
    const widths = r.map(wOf);
    const total = widths.reduce((a, b) => a + b, 0) + sp * (r.length - 1);
    let x = (LW - total) / 2;
    r.forEach((t, i) => {
      toks.push({ t, x, y: top + ri * lead, w: widths[i] });
      x += widths[i] + sp;
    });
  });
  return { toks, size };
};

/** A word or line arriving: rise + blur-in on the house arrival curve; leaving: up and out on the house exit. */
const inOut = (f: number, a: number, z: number, rise = 18, dur = 14) => {
  const i = prog(f, a, a + dur, E.glideOut);
  const o = prog(f, z, z + 8, E.buildIn);
  return { opacity: i * (1 - o), ty: (1 - i) * rise - o * 26, blur: (1 - i) * 8 + o * 6 };
};

const Word: React.FC<{ k: Tok; size: number; color: string; dx?: number; dy?: number; opacity?: number; blur?: number; weight?: number }> = ({ k, size, color, dx = 0, dy = 0, opacity = 1, blur = 0, weight = W8 }) => (
  <div
    style={{
      position: 'absolute',
      left: k.x + dx,
      top: k.y - size / 2 + dy,
      fontFamily: FONT.text,
      fontSize: size,
      fontWeight: weight,
      letterSpacing: `${TRACK}em`,
      lineHeight: 1,
      whiteSpace: 'pre',
      color,
      opacity,
      filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
    }}
  >
    {k.t}
  </div>
);

/** A centred one-line sentence; *word* marks the key word, set in `key` colour. */
const Line: React.FC<{ text: string; size: number; cy: number; color?: string; keyColor?: string; f: number; a: number; z: number; weight?: number }> = ({ text, size, cy, color = C.ink, keyColor = C.accent, f, a, z, weight = 500 }) => {
  const s = inOut(f, a, z);
  const parts = text.split(/(\*[^*]+\*)/).filter(Boolean);
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        top: cy - size * 0.6,
        textAlign: 'center',
        fontFamily: FONT.text,
        fontSize: size,
        fontWeight: weight,
        letterSpacing: '-0.02em',
        lineHeight: 1.2,
        whiteSpace: 'pre',
        color,
        opacity: s.opacity,
        transform: `translateY(${s.ty}px)`,
        filter: s.blur > 0.05 ? `blur(${s.blur}px)` : undefined,
      }}
    >
      {parts.map((p, i) => (p.startsWith('*') ? <span key={i} style={{ color: keyColor }}>{p.slice(1, -1)}</span> : <span key={i}>{p}</span>))}
    </div>
  );
};

/** The eye: a rounded bar under a span of the line. */
const Eye: React.FC<{ x: number; y: number; w: number; color: string; opacity?: number }> = ({ x, y, w, color, opacity = 1 }) => (
  <div style={{ position: 'absolute', left: x, top: y, width: Math.max(0, w), height: 5, borderRadius: 3, background: color, opacity }} />
);

const under = (k: Tok, size: number) => k.y + size * 0.52;

/** The eye's rectangle while it steps along `path` (token indices), one step every `step` frames from `a`. */
const stepEye = (f: number, a: number, step: number, path: number[], toks: Tok[]) => {
  const t = (f - a) / step;
  const i = clamp(Math.floor(t), 0, path.length - 1);
  const j = Math.min(i + 1, path.length - 1);
  const p = E.jump(clamp((t - i) * 1.6, 0, 1)); // a quick saccade, then a dwell
  const A = toks[path[i]];
  const B = toks[path[j]];
  const q = t >= path.length - 1 ? 0 : p;
  return { x: mix(A.x, B.x, q), w: mix(A.w, B.w, q), y: mix(A.y, B.y, q), idx: q > 0.5 ? path[j] : path[i] };
};

const Film: React.FC = () => {
  const f = useCurrentFrame();
  const L = useMemo(() => {
    const aOld = layout(['The', 'whole', 'conversation', 'is', 'eating', 'its', 'own', 'tail.'], 50, 300, 1120);
    const aNew = layout(['The', 'whole', 'conversation', 'keeps', 'going', 'in', 'circles.'], 50, 300, 1120);
    const bOld = layout(['The', 'guitar', 'sitting', 'in', 'the', 'corner', 'because', "you're", 'still', '“deciding”', 'teaches', 'you', 'zero', 'chords.'], 46, 296, 900);
    const bNew = layout(
      [
        ['While', "you're", 'still', '“deciding”,', 'the', 'guitar', 'sits', 'in', 'the', 'corner.'],
        ['It', 'teaches', 'you', 'zero', 'chords.'],
      ],
      40,
      296,
    );
    const name = layout(['legible'], 132, 268, 1100, 520);
    return { aOld, aNew, bOld, bNew, name };
  }, []);

  const els: React.ReactNode[] = [];
  const cap = 470; // the caption's centre, under the exhibit
  const exh = 150; // the exhibit's label, above it

  // ---- 1 · what it is, what it does ---------------------------------------------------------------------------------
  if (f < T.aIn) {
    els.push(<Line key="l1" text="legible is a writing skill for *Claude*." size={56} cy={300} f={f} a={T.l1In - 6} z={T.l1Out} />);
    els.push(<Line key="l2" text="It fixes sentences readers must *reread*." size={56} cy={300} f={f} a={T.l2In} z={T.l2Out} keyColor={C.stall} />);
  }

  // ---- 2 · exhibit A: prediction fails --------------------------------------------------------------------------------
  if (f >= T.aIn - 2 && f < T.bIn) {
    const { aOld, aNew } = L;
    const s = inOut(f, T.aIn, T.aOut);
    const fix = prog(f, T.aFix, T.aFix + 16, E.jump); // the kept words re-centre
    const going = prog(f, T.aFix, T.aFix + 8, E.buildIn); // the stalled words leave
    els.push(<Line key="la" text="An AI model wrote:" size={30} cy={exh} color={C.mute} f={f} a={T.aIn} z={T.aFix} weight={450} />);
    els.push(<Line key="la2" text="legible rewrote:" size={30} cy={exh} color={C.mute} f={f} a={T.aFix + 8} z={T.aOut} weight={450} />);
    const path = [0, 1, 2, 3, 4, 4, 4, 4, 4, 4, 2, 3, 4, 4, 4];
    const eye = stepEye(f, T.aRead, T.aStep, path, aOld.toks);
    const stalled = f >= T.aRead + 4 * T.aStep;
    aOld.toks.forEach((k, i) => {
      if (i <= 2) {
        const n = aNew.toks[i];
        els.push(<Word key={`ao${i}`} k={k} size={aOld.size} color={C.ink} dx={(n.x - k.x) * fix} dy={s.ty} opacity={s.opacity} blur={s.blur} />);
      } else {
        const red = i === 4 && stalled;
        els.push(<Word key={`ao${i}`} k={k} size={aOld.size} color={red ? C.stall : C.ink} dy={s.ty + going * 22} opacity={s.opacity * (1 - going)} blur={s.blur + going * 6} />);
      }
    });
    aNew.toks.slice(3).forEach((k, i) => {
      const w = inOut(f, T.aFix + 6 + i * 2, T.aOut);
      els.push(<Word key={`an${i}`} k={k} size={aNew.size} color={C.accent} dy={w.ty} opacity={w.opacity} blur={w.blur} />);
    });
    // the eye
    if (f < T.aFix) {
      const k = aOld.toks[0];
      const enterEye = prog(f, T.aRead - 8, T.aRead + 2, E.glideOut);
      els.push(<Eye key="eyeA" x={eye.x} y={under(k, aOld.size)} w={eye.w * enterEye} color={stalled && eye.idx === 4 ? C.stall : C.ink} opacity={s.opacity} />);
    } else {
      const g = prog(f, T.aGlide, T.aGlide + 26, E.stdInOut);
      const first = aNew.toks[0];
      const last = aNew.toks[aNew.toks.length - 1];
      const shrink = prog(f, T.aFix, T.aFix + 10, E.glideOut);
      const ex = f < T.aGlide ? mix(aOld.toks[4].x, first.x, shrink) : mix(first.x, last.x, g);
      const ew = f < T.aGlide ? mix(aOld.toks[4].w, first.w, shrink) : mix(first.w, last.w, g);
      // the trail it leaves: everything it has read in one pass, in accent
      const trail = f < T.aGlide ? 0 : ex - first.x;
      els.push(<Eye key="trailA" x={first.x} y={under(first, aNew.size)} w={trail} color={C.accent} opacity={0.28 * s.opacity} />);
      els.push(<Eye key="eyeA" x={ex} y={under(first, aNew.size)} w={ew} color={f < T.aGlide ? C.ink : C.accent} opacity={s.opacity} />);
    }
    els.push(<Line key="ca1" text="Conversations do not *eat*." size={38} cy={cap} color={C.ink} keyColor={C.stall} f={f} a={T.aRead + 4 * T.aStep + 8} z={T.aGlide - 4} weight={460} />);
    els.push(<Line key="ca2" text="The plain version reads *once*." size={38} cy={cap} color={C.ink} f={f} a={T.aGlide + 2} z={T.aOut} weight={460} />);
  }

  // ---- 3 · exhibit B: memory overflows --------------------------------------------------------------------------------
  if (f >= T.bIn - 2 && f < T.end) {
    const { bOld, bNew } = L;
    const s = inOut(f, T.bIn, T.bFix);
    els.push(<Line key="lb" text="An AI model wrote:" size={30} cy={exh} color={C.mute} f={f} a={T.bIn} z={T.bFix} weight={450} />);
    els.push(<Line key="lb2" text="legible rewrote:" size={30} cy={exh} color={C.mute} f={f} a={T.bFix + 10} z={T.bOut} weight={450} />);
    const path = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10, 1, 4, 7, 10, 10];
    const eye = stepEye(f, T.bRead, T.bStep, path, bOld.toks);
    const verbAt = T.bRead + 10 * T.bStep;
    const held = Math.floor((f - T.bRead) / T.bStep); // how far the first pass has got
    bOld.toks.forEach((k, i) => {
      const isVerb = i === 10 && f >= verbAt;
      const isSubj = i === 1 && f >= T.bRead + T.bStep;
      els.push(<Word key={`bo${i}`} k={k} size={bOld.size} color={isVerb ? C.stall : isSubj ? C.stall : C.ink} dy={s.ty} opacity={s.opacity} blur={s.blur} />);
      // the words held in memory between subject and verb: a faint stall-red mark under each, as it is passed
      if (i >= 2 && i <= 9 && held >= i && f < T.bFix) {
        const a = prog(f, T.bRead + i * T.bStep, T.bRead + i * T.bStep + 6, E.glideOut);
        els.push(<Eye key={`bh${i}`} x={k.x} y={under(k, bOld.size) + 8} w={k.w} color={C.stall} opacity={0.35 * a * s.opacity} />);
      }
    });
    if (f < T.bFix) {
      const k = bOld.toks[eye.idx];
      els.push(<Eye key="eyeB" x={eye.x} y={under(k, bOld.size)} w={eye.w} color={eye.idx === 10 || f >= verbAt ? C.stall : C.ink} opacity={s.opacity} />);
    }
    // the plain version: two short sentences, rising in place
    const rows = [bNew.toks.slice(0, 10), bNew.toks.slice(10)];
    rows.forEach((r, ri) =>
      r.forEach((k, i) => {
        const w = inOut(f, T.bFix + 10 + ri * 8 + i, T.bOut);
        els.push(<Word key={`bn${ri}-${i}`} k={k} size={bNew.size} color={C.ink} dy={w.ty} opacity={w.opacity} blur={w.blur} />);
      }),
    );
    if (f >= T.bFix + 10) {
      const o = inOut(f, T.bFix + 10, T.bOut).opacity;
      // one smooth pass: row 1, then row 2
      const r1 = prog(f, T.bGlide, T.bGlide + 22, E.stdInOut);
      const r2 = prog(f, T.bGlide + 24, T.bGlide + 38, E.stdInOut);
      const row = f < T.bGlide + 24 ? 0 : 1;
      const R = rows[row];
      const p = row === 0 ? r1 : r2;
      const first = R[0];
      const last = R[R.length - 1];
      const ex = mix(first.x, last.x, p);
      const ew = mix(first.w, last.w, p);
      const y = under(first, bNew.size);
      if (row === 1) {
        const a = rows[0];
        els.push(<Eye key="trailB0" x={a[0].x} y={under(a[0], bNew.size)} w={a[a.length - 1].x + a[a.length - 1].w - a[0].x} color={C.accent} opacity={0.28 * o} />);
      }
      els.push(<Eye key="trailB" x={first.x} y={y} w={ex - first.x} color={C.accent} opacity={0.28 * o} />);
      els.push(<Eye key="eyeB2" x={ex} y={y} w={ew} color={f < T.bGlide ? C.ink : C.accent} opacity={o} />);
    }
    els.push(<Line key="cb1" text="The *verb* waits eight words." size={38} cy={cap} color={C.ink} keyColor={C.stall} f={f} a={verbAt + 6} z={T.bFix} weight={460} />);
    els.push(<Line key="cb2" text="Two short sentences read *once*." size={38} cy={cap} color={C.ink} f={f} a={T.bGlide + 2} z={T.bOut} weight={460} />);
  }

  // ---- 4 · the end card: the eye becomes the name's underline ---------------------------------------------------------
  if (f >= T.end - 2) {
    const n = L.name.toks[0];
    const creep = mix(1, 1.035, clamp((f - T.end) / (T.total - T.end))); // the hold keeps creeping about its centre // lint-ok: end-card creep
    const s = inOut(f, T.end, T.total + 99, 22, 16);
    const line = prog(f, T.end + 6, T.end + 26, E.glideOut);
    els.push(
      <div key="end" style={{ position: 'absolute', inset: 0, transform: `scale(${creep})`, transformOrigin: '50% 45%' }}>
        <Word k={n} size={L.name.size} color={C.ink} dy={s.ty} opacity={s.opacity} blur={s.blur} weight={520} />
        <Eye x={n.x} y={n.y + L.name.size * 0.5} w={n.w * line} color={C.accent} />
        <Line text="A writing skill for Claude." size={40} cy={392} color={C.ink} f={f} a={T.end + 14} z={T.total + 99} weight={460} />
        <Line text="github.com/jason-in-hub/UnderstandingMaxxing" size={26} cy={452} color={C.mute} f={f} a={T.end + 22} z={T.total + 99} weight={440} />
      </div>,
    );
  }

  return <AbsoluteFill style={{ background: C.paper }}>{els}</AbsoluteFill>;
};

export const Legible: React.FC = () => (
  <FontGate>
    <Film />
  </FontGate>
);
