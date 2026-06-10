# Loom — visual synth (flagship T2 widget)

A node-based visual synthesizer for generative backgrounds. Saves a JSON
**trace** (patch graph); one engine renders it live / baked / in the editor.
Genre: TouchDesigner / Max-MSP / cables.gl dataflow patching.

## Files
- `SCHEMA.md` — the trace contract (nodes + two edge kinds: `buffer` textures,
  `control` scalars). **Read this first** — the schema is the product.
- `engine.js` — the shared core, `window.Loom`. Node registry, topo-sort of the
  buffer graph, per-frame modulation resolution, `Runtime`/`mount`. Canvas2d,
  no deps, idempotent. This is the single source of truth for rendering.
- `widget.js` — the editor (dashboard). Fetches `engine.js` via
  `/api/adze/get-widget?filename=loom/engine.js&tier=platform`, runs a live
  preview, exposes param controls + LFO modulation badges, saves the trace.
- `widget.json` / `README.md` — manifest + artist/autocoder-facing notes.

## How the two halves share one engine
The widget route only serves `widget.js`/`engine.js` leaves (allow-listed in
`admin_api.py` `get_widget`). The editor fetches `engine.js` at runtime;
`compile.py` `_inject_loom` reads the *same* `engine.js` server-side and injects
it + `_shared/features/loom.js` + `window.__loom = <trace>` before `</body>`.
Zero duplication.

## Storage & lifecycle (mirrors image-pipeline exactly)
- Save: `POST /api/adze/save-feature` `{feature:'loom', config:<trace>|null}` →
  `config.features.loom`, then auto-recompile.
- Live render: `compile.py::_inject_loom` (called beside `_inject_image_pipeline`).
- After editing `_shared/**` here: `sudo docker restart adze-flask`.

## Node library (26 types, all in `engine.js`)
- sources: solid, gradient, lorenz, noise, plasma, cells, text, image, video
- effects: dither, pixelate, blur, levels, colorize, grain, glitch, mirror,
  feedback, vhs, scanlines, chromashift
- composite: blend (2 inlets a/b)
- modulators: lfo, noisemod, pulse · sink: output

## Asset sources (image / video)
`image` and `video` pull from the artist's `assets/`. They carry a `src` param of
`type:'asset'` (with `accept:'image'|'video'`) holding a **portable** asset path
(e.g. `images/foo.png`) — never a URL, so the trace stays portable. Each renderer
resolves that path at mount via `Loom.setAssetResolver(fn)`: the editor
(`widget.js`) points it at the authed `/api/adze/asset-thumb/<slug>/<rel>?t=…`
route; the live page (`features/loom.js`) at `/assets/<rel>` (nginx alias). Both
are same-origin so downstream `getImageData` effects (`vhs`, `chromashift`) don't
taint the canvas. Loaded media is cached by URL in `engine.js` so editor rebuilds
(remount on every param tweak) reuse one `<img>`/`<video>` and video doesn't
restart. The asset-picker control in `widget.js` filters `ctx.assetList` by
`accept`. Editor renders `type:'asset'` as a `<select>`; it's non-numeric so it's
excluded from modulation targets.
Each def carries `kind` (source|effect|modulator|output), `cat` (adds
`composite`), `inlets`, `params` (numeric params = `{min,max}` are
modulation targets; `type:'select'|'color'|'text'` render as such), and
`render(node,inputs,p,t)` (buffer nodes) or `sample(p,t)` (modulators).
`Loom.ports(type)` / `Loom.modTargets(type)` expose port metadata to the editor.

## Editor (`widget.js`)
Drag-to-wire node canvas: outlet→inlet = buffer wire, outlet→param-port =
control wire (kinds must match — buffer↔buffer, control↔control). Pan (drag bg),
zoom (wheel), palette (+ Add node), Fit, per-node param controls + delete (×),
click a wire to delete. Live preview bottom-right (debounced rebuild via rAF).
Port world-coords computed by inverting the pan/zoom transform on
`getBoundingClientRect` — robust to varying node heights.

## Next bones
bake-to-asset (same engine, `fps:0` / frame-capture → PNG/WebM), named
multi-traces (`assets/looms/<name>.loom.json`), audio/mouse modulators, WebGL
backend when canvas2d caps out. (image/video source nodes — done.)
