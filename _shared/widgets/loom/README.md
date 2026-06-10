### loom (T2 platform · flagship)

Loom is a node-based **visual synth** for generative site backgrounds — think
TouchDesigner-in-the-dashboard. You wire **sources** (a Lorenz strange
attractor, gradients) through **effect** layers (dither, glitch) into an
**output**, and patch **modulators** (LFOs) into any parameter so the visuals
move on their own (e.g. a sine LFO breathing the dither block size).

**It saves a "trace"** — a JSON patch graph (see `SCHEMA.md`) — which is the
only durable artifact. One engine renders it; *where* it renders is the
placement layer's job:

- **Live (v0):** turn Loom On and Save in the widget → the trace is stored in
  `config.features.loom` and `compile.py` injects a fixed full-bleed background
  canvas on every page (`#loom-bg`, `z-index:-1`, paused when the tab is hidden).
- **Bake / named traces (next):** the same engine freezes the trace to a
  PNG/WebM asset, or stores `assets/looms/<name>.loom.json`, so the autocoder
  can place a specific trace behind a specific section.

**For the autocoder:** if an artist asks for a "living background", "generative
texture", or "animated backdrop", that's Loom. The trace already in
`config.features.loom` is live site-wide; to scope it to one section instead,
that's the bake/named-trace path (not built yet — say so).

Editor: a drag-to-wire node canvas — drag a node's outlet port onto another
node's inlet to make a **buffer** wire (blue), or onto a parameter's port to
make a **control** wire (green, dashed). Pan by dragging empty space, scroll to
zoom, `+ Add node` for the palette, `Fit` to frame the graph, live preview
bottom-right.

Node library (adding one = registering a def in `engine.js`):
- **sources:** `solid`, `gradient`, `lorenz` (strange attractor), `noise`,
  `plasma`, `cells` (Voronoi), `text`, `image` (an asset image), `video` (an
  asset video, muted/looping)
- **effects:** `dither`, `pixelate`, `blur`, `levels`, `colorize`, `grain`,
  `glitch`, `mirror`, `feedback` (frame trails), `vhs` (tape/CRT degradation),
  `scanlines` (CRT lines + vignette), `chromashift` (RGB split — patch an LFO
  into `amount` for that pulsing analog wobble)
- **composite:** `blend` (two inlets a/b · screen/multiply/overlay/…)
- **modulators:** `lfo`, `noisemod` (smooth random), `pulse`
- **sink:** `output`

**Image / video sources** pull from the artist's uploaded assets — pick a file
from the node's `src` dropdown. Great chained into `vhs` or `chromashift` for a
degraded-tape look over a photo or clip. The trace stores a portable asset path,
so the same trace renders in the editor preview and live on the site.
