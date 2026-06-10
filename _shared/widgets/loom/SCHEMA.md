# Loom — the trace schema

A **trace** is the only durable artifact Loom produces. It is a JSON patch
graph: nodes (boxes) and edges (wires). One engine (`engine.js`) renders a
trace; *where* it renders — live page background, baked asset, editor preview
— is the renderer's concern, not the trace's. Save the trace, and the
autocoder can place it anywhere.

```jsonc
{
  "version": 1,
  "size": { "w": 360, "h": 360 },     // internal render resolution (chunky-on-purpose; output upscales)
  "fps": 30,                          // animation cap; 0 = render one static frame
  "nodes": [
    { "id": "src",  "type": "lorenz",  "x": 40,  "y": 80,  "params": { "speed": 1, "hue": 200, "fade": 0.08 } },
    { "id": "dith", "type": "dither",  "x": 280, "y": 80,  "params": { "blockSize": 6, "levels": 4 } },
    { "id": "out",  "type": "output",  "x": 520, "y": 80,  "params": {} }
  ],
  "edges": [
    { "from": ["src", "out"],  "to": ["dith", "in"],        "kind": "buffer"  },
    { "from": ["dith", "out"], "to": ["out", "in"],         "kind": "buffer"  },
    { "from": ["lfo", "out"],  "to": ["dith", "blockSize"], "kind": "control", "range": [2, 14] }
  ]
}
```

## Two edge kinds — this is the whole idea

- **`buffer`** — carries a *texture* (a canvas) from a node's outlet into another
  node's **inlet**. This is the signal path: `source → effect → effect → output`.
  An inlet is a named port (`in`); an outlet is `out`.
- **`control`** — carries a *scalar* from a modulator's `out` into a target
  node's **parameter** (the `to` port is a param name, not an inlet). This is
  what makes Loom a synth and not a filter stack: an LFO patched into
  `dither.blockSize` makes the dither breathe. Modulators emit `0..1`; `range`
  on the edge maps that across the param (defaults to the param's own min/max).

## Node contract (see `engine.js` registry)

Every node `type` is registered with:

```js
Loom.register('dither', {
  kind: 'effect',                       // 'source' | 'effect' | 'modulator' | 'output'
  inlets: ['in'],                       // buffer inlets (sources have none)
  params: { blockSize: {def:6,min:2,max:14}, levels:{def:4,min:2,max:8} },
  render(node, inputs, p, t) { /* draw into node.cx (a 2d ctx) */ },   // buffer nodes
  sample(p, t) { /* return a number 0..1 */ },                          // modulators only
});
```

Adding a node = registering one of these. That registry is the extension
point — the reason Loom is the flagship "core engine" other things grow on.

### Param types

A numeric param (`{def,min,max}`) renders as a slider and is a modulation
target. Non-numeric params declare a `type`:

- `select` — `{def, type:'select', options:[…]}`
- `color`  — `{def:'#rrggbb', type:'color'}`
- `text`   — `{def:'…', type:'text'}`
- `asset`  — `{def:'', type:'asset', accept:'image'|'video'}` — holds a **portable
  asset path** (e.g. `images/foo.png`), not a URL. The renderer resolves it via
  `Loom.setAssetResolver(fn)` (editor → asset-thumb route, live → `/assets/`).
  Used by the `image` / `video` source nodes.

## Storage & placement

- **v0 (live-first):** the trace is saved into the artist's
  `config.json` under `features.loom` via `POST /api/adze/save-feature`
  (`{ feature: "loom", config: <trace> }`), exactly like `image_pipeline`.
  `compile.py` injects `engine.js` + `features/loom.js` + `window.__loom = <trace>`
  before `</body>`, and the runtime mounts a fixed full-bleed background canvas.
- **next bone — bake:** same engine, `fps:0` or frame-capture → PNG/WebM saved
  as an asset; the autocoder drops the static file where a live canvas would be
  too heavy (mobile, hero images).
- **next bone — named traces:** store multiple traces as
  `assets/looms/<name>.loom.json` so one site can have several, and the
  autocoder picks per placement.
