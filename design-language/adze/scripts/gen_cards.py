#!/usr/bin/env python3
"""Generate the Adze design-system preview cards.

Every card is standalone HTML (the Design System pane renders each in its own
frame), so the token block has to be inlined into each one. Generating them
from a single TOKENS string here is what stops the eight cards drifting apart
the way the four chrome files did.
"""

import pathlib

ROOT = pathlib.Path('/home/gabriel/adze/design-language/adze')

TOKENS = """
:root {
    --adze-bg: #fbfbfd; --adze-surface: #ffffff; --adze-text: #1d1d1f;
    --adze-accent: #1c4f82; --adze-accent-text: #ffffff; --adze-border: #e3e3e8;
    --adze-bg-sunken: color-mix(in srgb, var(--adze-bg) 94%, var(--adze-text));
    --adze-surface-hover: color-mix(in srgb, var(--adze-surface) 96%, var(--adze-text));
    --adze-border-strong: color-mix(in srgb, var(--adze-border) 55%, var(--adze-text));
    --adze-text-muted: color-mix(in srgb, var(--adze-text) 62%, var(--adze-bg));
    --adze-text-faint: color-mix(in srgb, var(--adze-text) 40%, var(--adze-bg));
    --adze-accent-hover: color-mix(in srgb, var(--adze-accent) 86%, var(--adze-text));
    --adze-accent-soft: color-mix(in srgb, var(--adze-accent) 10%, var(--adze-surface));
    --adze-accent-line: color-mix(in srgb, var(--adze-accent) 32%, var(--adze-border));
    --adze-success: #1a8a52; --adze-warn: #a86b00; --adze-danger: #c8362a;
    --adze-success-soft: color-mix(in srgb, #1a8a52 12%, var(--adze-surface));
    --adze-warn-soft: color-mix(in srgb, #a86b00 12%, var(--adze-surface));
    --adze-danger-soft: color-mix(in srgb, #c8362a 12%, var(--adze-surface));
    --adze-focus-ring: 0 0 0 3px color-mix(in srgb, var(--adze-accent) 30%, transparent);
    --adze-font-ui: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --adze-font-mono: 'JetBrains Mono', ui-monospace, Menlo, monospace;
    --adze-text-2xs: 11px; --adze-text-xs: 12px; --adze-text-sm: 13px;
    --adze-text-md: 15px; --adze-text-lg: 18px; --adze-text-xl: 22px;
    --adze-text-2xl: 28px; --adze-text-3xl: 36px; --adze-text-display: 48px;
    --adze-weight-normal: 400; --adze-weight-medium: 500;
    --adze-weight-semibold: 600; --adze-weight-bold: 700;
    --adze-leading-tight: 1.2; --adze-leading-snug: 1.35;
    --adze-leading-normal: 1.55; --adze-leading-relaxed: 1.7;
    --adze-tracking-display: -0.02em; --adze-tracking-tight: -0.01em;
    --adze-tracking-label: 0.08em;
    --adze-space-1: 4px; --adze-space-2: 8px; --adze-space-3: 12px;
    --adze-space-4: 16px; --adze-space-5: 20px; --adze-space-6: 24px;
    --adze-space-8: 32px; --adze-space-10: 40px; --adze-space-12: 48px; --adze-space-16: 64px;
    --adze-control-sm: 28px; --adze-control-md: 36px; --adze-control-lg: 44px;
    --adze-radius-sm: 4px; --adze-radius-md: 8px; --adze-radius-lg: 12px; --adze-radius-pill: 999px;
    --adze-width-form: 560px; --adze-width-content: 720px; --adze-col-min: 200px;
    --adze-shadow-sm: 0 1px 2px rgba(0,0,0,.04), 0 1px 3px rgba(0,0,0,.06);
    --adze-shadow-md: 0 2px 4px rgba(0,0,0,.04), 0 8px 20px rgba(0,0,0,.08);
    --adze-shadow-lg: 0 4px 8px rgba(0,0,0,.04), 0 16px 40px rgba(0,0,0,.10);
    --adze-dur-instant: 80ms; --adze-dur-fast: 140ms; --adze-dur: 220ms;
    --adze-dur-slow: 320ms; --adze-dur-slower: 480ms;
    --adze-ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --adze-ease-in: cubic-bezier(0.4, 0, 1, 1);
    --adze-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
    --adze-ease-spring: cubic-bezier(0.34, 1.4, 0.64, 1);
}
@media (prefers-color-scheme: dark) {
    :root {
        --adze-bg: #131316; --adze-surface: #1c1c20; --adze-text: #f0f0f2;
        --adze-accent: #99cdff; --adze-accent-text: #131316; --adze-border: #2e2e34;
        --adze-success: #4fc084; --adze-warn: #e0b055; --adze-danger: #f0685c;
        --adze-shadow-sm: 0 1px 2px rgba(0,0,0,.4);
        --adze-shadow-md: 0 2px 6px rgba(0,0,0,.45), 0 8px 24px rgba(0,0,0,.35);
        --adze-shadow-lg: 0 4px 12px rgba(0,0,0,.5), 0 16px 48px rgba(0,0,0,.4);
    }
}
@keyframes adze-spin { to { transform: rotate(360deg); } }
@keyframes adze-rise-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes adze-pulse { 50% { opacity: 0.55; } }

* { box-sizing: border-box; }
body {
    margin: 0; padding: var(--adze-space-8);
    background: var(--adze-bg); color: var(--adze-text);
    font-family: var(--adze-font-ui); font-size: var(--adze-text-sm);
    line-height: var(--adze-leading-normal); -webkit-font-smoothing: antialiased;
    font-feature-settings: 'cv05' 1, 'ss01' 1;
}
h1,h2,h3,h4 { margin: 0; font-weight: var(--adze-weight-semibold); line-height: var(--adze-leading-tight); letter-spacing: var(--adze-tracking-tight); }
.wrap { max-width: 1100px; margin: 0 auto; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--adze-space-6); }
.panel { background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md); padding: var(--adze-space-6); box-shadow: var(--adze-shadow-sm); }
.panel > h3 { font-size: var(--adze-text-md); margin-bottom: var(--adze-space-4); }
.stack { display: flex; flex-direction: column; gap: var(--adze-space-4); }
.row { display: flex; align-items: center; gap: var(--adze-space-3); flex-wrap: wrap; }
.adze-label { font-family: var(--adze-font-mono); font-size: var(--adze-text-2xs); font-weight: var(--adze-weight-medium); letter-spacing: var(--adze-tracking-label); text-transform: uppercase; color: var(--adze-text-muted); line-height: var(--adze-leading-snug); }
.adze-numeric { font-family: var(--adze-font-mono); font-variant-numeric: tabular-nums; letter-spacing: 0; }
.note { font-size: var(--adze-text-xs); color: var(--adze-text-muted); max-width: 62ch; }

.adze-theme {
    --adze-bg: var(--adze-artist-bg, #fbfbfd);
    --adze-surface: var(--adze-artist-surface, #ffffff);
    --adze-text: var(--adze-artist-text, #1d1d1f);
    --adze-accent: var(--adze-artist-accent, #1c4f82);
    --adze-accent-text: var(--adze-artist-accent-text, #ffffff);
    --adze-border: var(--adze-artist-border, #e3e3e8);
    --adze-bg-sunken: color-mix(in srgb, var(--adze-bg) 94%, var(--adze-text));
    --adze-surface-hover: color-mix(in srgb, var(--adze-surface) 96%, var(--adze-text));
    --adze-border-strong: color-mix(in srgb, var(--adze-border) 55%, var(--adze-text));
    --adze-text-muted: color-mix(in srgb, var(--adze-text) 62%, var(--adze-bg));
    --adze-text-faint: color-mix(in srgb, var(--adze-text) 40%, var(--adze-bg));
    --adze-accent-hover: color-mix(in srgb, var(--adze-accent) 86%, var(--adze-text));
    --adze-accent-soft: color-mix(in srgb, var(--adze-accent) 10%, var(--adze-surface));
    --adze-accent-line: color-mix(in srgb, var(--adze-accent) 32%, var(--adze-border));
    --adze-success-soft: color-mix(in srgb, var(--adze-success) 12%, var(--adze-surface));
    --adze-warn-soft: color-mix(in srgb, var(--adze-warn) 12%, var(--adze-surface));
    --adze-danger-soft: color-mix(in srgb, var(--adze-danger) 12%, var(--adze-surface));
    --adze-focus-ring: 0 0 0 3px color-mix(in srgb, var(--adze-accent) 30%, transparent);
    background: var(--adze-bg); color: var(--adze-text);
}
.mono { font-family: var(--adze-font-mono); font-size: var(--adze-text-2xs); color: var(--adze-text-faint); }
"""

# Component CSS reused across the cards.
BTN = """
.adze-btn { display: inline-flex; align-items: center; justify-content: center; gap: var(--adze-space-2); height: var(--adze-control-md); padding: 0 var(--adze-space-4); border: 1px solid transparent; border-radius: var(--adze-radius-md); font-family: var(--adze-font-ui); font-size: var(--adze-text-sm); font-weight: var(--adze-weight-medium); line-height: 1; white-space: nowrap; cursor: pointer; transition: background-color var(--adze-dur-instant) var(--adze-ease-out), border-color var(--adze-dur-instant) var(--adze-ease-out), color var(--adze-dur-instant) var(--adze-ease-out), box-shadow var(--adze-dur-fast) var(--adze-ease-out), transform var(--adze-dur-fast) var(--adze-ease-out); }
.adze-btn i { font-size: 1.15em; }
.adze-btn--sm { height: var(--adze-control-sm); padding: 0 var(--adze-space-3); font-size: var(--adze-text-xs); }
.adze-btn--lg { height: var(--adze-control-lg); padding: 0 var(--adze-space-6); font-size: var(--adze-text-md); }
.adze-btn:active:not(:disabled) { transform: scale(0.98); }
.adze-btn:focus-visible { outline: none; box-shadow: var(--adze-focus-ring); }
.adze-btn--primary { background: var(--adze-accent); color: var(--adze-accent-text); }
.adze-btn--primary:hover:not(:disabled) { background: var(--adze-accent-hover); }
.adze-btn--secondary { background: var(--adze-surface); color: var(--adze-text); border-color: var(--adze-border-strong); }
.adze-btn--secondary:hover:not(:disabled) { background: var(--adze-surface-hover); border-color: var(--adze-text-faint); }
.adze-btn--ghost { background: transparent; color: var(--adze-text-muted); }
.adze-btn--ghost:hover:not(:disabled) { background: var(--adze-bg-sunken); color: var(--adze-text); }
.adze-btn--danger { background: var(--adze-danger); color: #fff; }
.adze-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.adze-spinner { display: inline-block; flex: 0 0 auto; border-radius: var(--adze-radius-pill); border: 2px solid color-mix(in srgb, currentColor 20%, transparent); border-top-color: currentColor; animation: adze-spin 0.7s linear infinite; vertical-align: -0.125em; width: 16px; height: 16px; }
.adze-spinner--sm { width: 12px; height: 12px; border-width: 1.5px; }
"""

TAG = """
.adze-tag { display: inline-flex; align-items: center; gap: var(--adze-space-1); padding: 3px var(--adze-space-2); border-radius: var(--adze-radius-sm); font-family: var(--adze-font-mono); font-size: var(--adze-text-2xs); font-weight: var(--adze-weight-medium); line-height: 1.4; letter-spacing: var(--adze-tracking-label); text-transform: uppercase; white-space: nowrap; }
.adze-tag__dot { width: 5px; height: 5px; border-radius: var(--adze-radius-pill); background: currentColor; flex: 0 0 auto; }
.adze-tag--neutral { background: var(--adze-bg-sunken); color: var(--adze-text-muted); }
.adze-tag--accent { background: var(--adze-accent-soft); color: var(--adze-accent); }
.adze-tag--success { background: var(--adze-success-soft); color: var(--adze-success); }
.adze-tag--warn { background: var(--adze-warn-soft); color: var(--adze-warn); }
.adze-tag--danger { background: var(--adze-danger-soft); color: var(--adze-danger); }
"""

FORMS = """
.adze-field { display: flex; flex-direction: column; gap: var(--adze-space-2); margin-bottom: var(--adze-space-4); }
.adze-field__head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--adze-space-3); }
.adze-field__req { color: var(--adze-danger); margin-left: 2px; }
.adze-field__hint { font-size: var(--adze-text-2xs); color: var(--adze-text-faint); }
.adze-field__help { margin: 0; font-size: var(--adze-text-xs); color: var(--adze-text-muted); }
.adze-field__error { display: flex; align-items: center; gap: var(--adze-space-1); margin: 0; font-size: var(--adze-text-xs); color: var(--adze-danger); }
.adze-input { width: 100%; height: var(--adze-control-md); padding: 0 var(--adze-space-3); background: var(--adze-surface); color: var(--adze-text); border: 1px solid var(--adze-border-strong); border-radius: var(--adze-radius-md); font-family: var(--adze-font-ui); font-size: var(--adze-text-sm); transition: border-color var(--adze-dur-instant) var(--adze-ease-out), box-shadow var(--adze-dur-fast) var(--adze-ease-out); }
.adze-input--textarea { height: auto; min-height: 96px; padding: var(--adze-space-3); line-height: var(--adze-leading-normal); resize: vertical; }
.adze-input::placeholder { color: var(--adze-text-faint); }
.adze-input:hover:not(:disabled) { border-color: var(--adze-text-faint); }
.adze-input:focus { outline: none; border-color: var(--adze-accent); box-shadow: var(--adze-focus-ring); }
.adze-input:disabled { opacity: 0.55; cursor: not-allowed; background: var(--adze-bg-sunken); }
.adze-field--error .adze-input { border-color: var(--adze-danger); }
.adze-input-group { display: flex; align-items: center; gap: var(--adze-space-2); height: var(--adze-control-md); padding: 0 var(--adze-space-3); background: var(--adze-surface); border: 1px solid var(--adze-border-strong); border-radius: var(--adze-radius-md); transition: border-color var(--adze-dur-instant) var(--adze-ease-out), box-shadow var(--adze-dur-fast) var(--adze-ease-out); }
.adze-input-group:focus-within { border-color: var(--adze-accent); box-shadow: var(--adze-focus-ring); }
.adze-input-group i { color: var(--adze-text-faint); font-size: 1.15em; }
.adze-input-group__prefix { font-family: var(--adze-font-mono); font-size: var(--adze-text-xs); color: var(--adze-text-faint); white-space: nowrap; }
.adze-input--bare { border: 0; background: transparent; padding: 0; height: 100%; flex: 1; min-width: 0; }
.adze-input--bare:focus { box-shadow: none; }
.adze-select-wrap { position: relative; display: block; }
.adze-select { appearance: none; padding-right: var(--adze-space-8); cursor: pointer; }
.adze-select__caret { position: absolute; right: var(--adze-space-3); top: 50%; transform: translateY(-50%); pointer-events: none; color: var(--adze-text-faint); font-size: 0.9em; }
.adze-check { display: flex; align-items: flex-start; gap: var(--adze-space-3); cursor: pointer; padding: var(--adze-space-1) 0; position: relative; }
.adze-check__input { position: absolute; opacity: 0; width: 18px; height: 18px; margin: 0; cursor: pointer; }
.adze-check__box { flex: 0 0 auto; display: grid; place-items: center; width: 18px; height: 18px; margin-top: 1px; background: var(--adze-surface); border: 1.5px solid var(--adze-border-strong); border-radius: var(--adze-radius-sm); color: transparent; font-size: 12px; transition: background-color var(--adze-dur-fast) var(--adze-ease-out), border-color var(--adze-dur-fast) var(--adze-ease-out), color var(--adze-dur-fast) var(--adze-ease-out), transform var(--adze-dur-fast) var(--adze-ease-spring); }
.adze-check:hover .adze-check__box { border-color: var(--adze-text-faint); }
.adze-check__input:checked + .adze-check__box { background: var(--adze-accent); border-color: var(--adze-accent); color: var(--adze-accent-text); transform: scale(1.06); }
.adze-check__input:focus-visible + .adze-check__box { box-shadow: var(--adze-focus-ring); }
.adze-check__text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.adze-check__label { font-size: var(--adze-text-sm); }
.adze-check__desc { font-size: var(--adze-text-xs); color: var(--adze-text-muted); }
.adze-switch { display: flex; align-items: center; justify-content: space-between; gap: var(--adze-space-4); cursor: pointer; padding: var(--adze-space-2) 0; position: relative; }
.adze-switch__text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.adze-switch__label { font-size: var(--adze-text-sm); }
.adze-switch__desc { font-size: var(--adze-text-xs); color: var(--adze-text-muted); }
.adze-switch__input { position: absolute; opacity: 0; right: 0; width: 44px; height: 26px; margin: 0; cursor: pointer; }
.adze-switch__track { position: relative; flex: 0 0 auto; width: 44px; height: 26px; background: var(--adze-border-strong); border-radius: var(--adze-radius-pill); transition: background-color var(--adze-dur) var(--adze-ease-out); }
.adze-switch__thumb { position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; background: #fff; border-radius: var(--adze-radius-pill); box-shadow: var(--adze-shadow-sm); transition: transform var(--adze-dur) var(--adze-ease-spring); }
.adze-switch__input:checked ~ .adze-switch__track { background: var(--adze-accent); }
.adze-switch__input:checked ~ .adze-switch__track .adze-switch__thumb { transform: translateX(18px); }
.adze-switch__input:focus-visible ~ .adze-switch__track { box-shadow: var(--adze-focus-ring); }
.adze-switch.is-pending .adze-switch__track { animation: adze-pulse 1s var(--adze-ease-in-out) infinite; }
.adze-switch.is-pending .adze-switch__text { opacity: 0.6; }
.adze-card { background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md); box-shadow: var(--adze-shadow-sm); padding: var(--adze-space-6); transition: border-color var(--adze-dur-fast) var(--adze-ease-out), box-shadow var(--adze-dur-fast) var(--adze-ease-out), transform var(--adze-dur-fast) var(--adze-ease-out); }
.adze-card__head { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--adze-space-4); margin-bottom: var(--adze-space-4); }
.adze-card__title { font-size: var(--adze-text-md); font-weight: var(--adze-weight-semibold); line-height: var(--adze-leading-snug); }
.adze-card__subtitle { margin: var(--adze-space-1) 0 0; font-size: var(--adze-text-xs); color: var(--adze-text-muted); }
.adze-card--interactive { cursor: pointer; }
.adze-card--interactive:hover { border-color: var(--adze-accent-line); box-shadow: var(--adze-shadow-md); transform: translateY(-1px); }
.adze-link { color: var(--adze-accent); text-decoration: none; text-underline-offset: 2px; text-decoration-thickness: 1px; }
.adze-link--inline { text-decoration: underline; }
.adze-link--standalone { display: inline-flex; align-items: center; gap: var(--adze-space-1); font-weight: var(--adze-weight-medium); }
.adze-link--standalone:hover { text-decoration: underline; }
.adze-link--quiet { color: var(--adze-text-muted); }
.adze-link--quiet:hover { color: var(--adze-text); text-decoration: underline; }
"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Adze — {title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2/src/regular/style.css">
<style>{css}</style>
</head>
<body><div class="wrap">
{body}
</div></body>
</html>
"""


def card(path, group, name, subtitle, title, extra_css, body):
    html = ('<!-- @dsCard group="%s" name="%s" subtitle="%s" -->\n' % (group, name, subtitle)
            + HEAD.format(title=title, css=TOKENS + extra_css, body=body))
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding='utf-8')
    print('wrote', path, len(html), 'bytes')


# ── Core components ────────────────────────────────────────────────────────
card('components/core/core.card.html', 'Components', 'Core',
     'Button, Card, Tag, TextLink', 'Core', BTN + TAG + FORMS, """
<div class="grid">
  <div class="panel stack">
    <h3>Button — variants</h3>
    <div class="row">
      <button class="adze-btn adze-btn--primary">Publish</button>
      <button class="adze-btn adze-btn--secondary">Preview</button>
      <button class="adze-btn adze-btn--ghost"><i class="ph ph-dots-three"></i></button>
      <button class="adze-btn adze-btn--danger">Delete</button>
    </div>
    <p class="note">Variant encodes importance, not colour. Max one primary per view.</p>
    <div class="row">
      <button class="adze-btn adze-btn--primary adze-btn--sm">Small</button>
      <button class="adze-btn adze-btn--primary">Medium</button>
      <button class="adze-btn adze-btn--primary adze-btn--lg">Large</button>
    </div>
    <div class="row">
      <button class="adze-btn adze-btn--primary" disabled><span class="adze-spinner adze-spinner--sm"></span> Publishing</button>
      <button class="adze-btn adze-btn--secondary" disabled>Disabled</button>
    </div>
    <div class="row">
      <button class="adze-btn adze-btn--primary"><i class="ph ph-plus"></i> Add a work</button>
      <button class="adze-btn adze-btn--secondary">Open site <i class="ph ph-arrow-up-right"></i></button>
    </div>
  </div>

  <div class="panel stack">
    <h3>Tag</h3>
    <div class="row">
      <span class="adze-tag adze-tag--success"><span class="adze-tag__dot"></span>Live</span>
      <span class="adze-tag adze-tag--warn"><span class="adze-tag__dot"></span>Unpublished</span>
      <span class="adze-tag adze-tag--danger"><span class="adze-tag__dot"></span>Error</span>
      <span class="adze-tag adze-tag--neutral">Draft</span>
      <span class="adze-tag adze-tag--accent">Featured</span>
    </div>
    <p class="note">Mono at 11px with open tracking — the strongest carry-over from the
    old Adze identity, and why this system still reads as Adze. Status tones are not
    artist-overridable.</p>
    <h3 style="margin-top:var(--adze-space-4)">TextLink</h3>
    <p style="margin:0">Read the <a class="adze-link adze-link--inline" href="#">setup guide</a> first —
    inline links are always underlined.</p>
    <div class="row">
      <a class="adze-link adze-link--standalone" href="#"><i class="ph ph-arrow-left"></i> Back to sites</a>
      <a class="adze-link adze-link--quiet" href="#">lydialott.co.uk <i class="ph ph-arrow-up-right" style="font-size:.85em;opacity:.7"></i></a>
    </div>
  </div>

  <div class="panel stack">
    <h3>Card</h3>
    <div class="adze-card adze-card--interactive">
      <div class="adze-card__head">
        <div>
          <h4 class="adze-card__title">Lydia Lott</h4>
          <p class="adze-card__subtitle">lydialott.co.uk</p>
        </div>
        <span class="adze-tag adze-tag--success"><span class="adze-tag__dot"></span>Live</span>
      </div>
      <div class="row" style="gap:var(--adze-space-6)">
        <div><div class="adze-label">Views</div><div class="adze-numeric" style="font-size:var(--adze-text-lg)">1,284</div></div>
        <div><div class="adze-label">This week</div><div class="adze-numeric" style="font-size:var(--adze-text-lg)">312</div></div>
      </div>
    </div>
    <p class="note">Hover lifts 1px. One card, one subject — if you need a divider
    through the middle, it's two cards. `interactive` only when the whole card navigates.</p>
  </div>
</div>
""")

# ── Form components ────────────────────────────────────────────────────────
card('components/forms/forms.card.html', 'Components', 'Forms',
     'Field, Input, Select, Checkbox, Switch', 'Forms', BTN + TAG + FORMS, """
<div class="grid">
  <div class="panel">
    <h3>Field + Input</h3>
    <div class="adze-field">
      <div class="adze-field__head"><label class="adze-label" for="f1">Title<span class="adze-field__req">*</span></label></div>
      <input class="adze-input" id="f1" value="Study in Ochre">
    </div>
    <div class="adze-field">
      <div class="adze-field__head"><label class="adze-label" for="f2">Website</label></div>
      <div class="adze-input-group"><span class="adze-input-group__prefix">https://</span><input class="adze-input adze-input--bare" id="f2" placeholder="yoursite.com"></div>
      <p class="adze-field__help">Where your work lives online.</p>
    </div>
    <div class="adze-field adze-field--error">
      <div class="adze-field__head"><label class="adze-label" for="f3">Slug<span class="adze-field__req">*</span></label></div>
      <input class="adze-input" id="f3" value="">
      <p class="adze-field__error"><i class="ph ph-warning-circle"></i>Add a slug so this work can be found.</p>
    </div>
    <div class="adze-field">
      <div class="adze-field__head"><label class="adze-label" for="f4">Bio</label><span class="adze-field__hint adze-numeric">128/280</span></div>
      <textarea class="adze-input adze-input--textarea" id="f4">Painter working between London and Margate.</textarea>
    </div>
  </div>

  <div class="panel">
    <h3>Select + toggles</h3>
    <div class="adze-field">
      <div class="adze-field__head"><label class="adze-label" for="f5">Category</label></div>
      <div class="adze-select-wrap">
        <select class="adze-input adze-select" id="f5"><option>Painting</option><option>Sculpture</option><option>Print</option></select>
        <i class="ph ph-caret-down adze-select__caret"></i>
      </div>
    </div>
    <hr style="border:0;border-top:1px solid var(--adze-border);margin:var(--adze-space-6) 0">
    <label class="adze-check">
      <input type="checkbox" class="adze-check__input" checked>
      <span class="adze-check__box"><i class="ph ph-check"></i></span>
      <span class="adze-check__text"><span class="adze-check__label">Feature on homepage</span>
      <span class="adze-check__desc">Shows in the top row of your gallery.</span></span>
    </label>
    <label class="adze-check">
      <input type="checkbox" class="adze-check__input">
      <span class="adze-check__box"><i class="ph ph-check"></i></span>
      <span class="adze-check__text"><span class="adze-check__label">Show in search results</span></span>
    </label>
    <hr style="border:0;border-top:1px solid var(--adze-border);margin:var(--adze-space-6) 0">
    <label class="adze-switch">
      <span class="adze-switch__text"><span class="adze-switch__label">Site is live</span>
      <span class="adze-switch__desc">Visitors can reach lydialott.co.uk</span></span>
      <input type="checkbox" role="switch" class="adze-switch__input" checked>
      <span class="adze-switch__track"><span class="adze-switch__thumb"></span></span>
    </label>
    <label class="adze-switch is-pending">
      <span class="adze-switch__text"><span class="adze-switch__label">Accept enquiries</span>
      <span class="adze-switch__desc">Saving…</span></span>
      <input type="checkbox" role="switch" class="adze-switch__input" disabled>
      <span class="adze-switch__track"><span class="adze-switch__thumb"></span></span>
    </label>
    <p class="note" style="margin-top:var(--adze-space-4)"><b>Checkbox</b> = takes effect on Save.
    <b>Switch</b> = takes effect immediately, and must show a pending state while the write is in flight.</p>
  </div>
</div>
""")


SWATCH = """
.sw-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: var(--adze-space-3); }
.sw { border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md); overflow: hidden; background: var(--adze-surface); }
.sw__chip { height: 56px; }
.sw__meta { padding: var(--adze-space-2) var(--adze-space-3); }
.sw__name { font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .04em; color: var(--adze-text); display: block; }
.sw__val { font-family: var(--adze-font-mono); font-size: 10px; color: var(--adze-text-faint); }
"""

def swatches(items):
    out = ['<div class="sw-grid">']
    for var, val in items:
        out.append(
            '<div class="sw"><div class="sw__chip" style="background:%s"></div>'
            '<div class="sw__meta"><span class="sw__name">%s</span>'
            '<span class="sw__val">%s</span></div></div>' % (var, var, val))
    out.append('</div>')
    return '\n'.join(out)


card('guidelines/color-core.html', 'Colour', 'Core palette',
     'Six-var contract, derived tokens, status', 'Colour', SWATCH + TAG, """
<div class="stack">
  <div class="panel">
    <h3>The six artist-contract variables</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">These are the only colours an artist may set.
    Everything else is derived from them with <code>color-mix()</code>, so six values produce a
    complete, coherent admin — including hovers, tints, sunken surfaces and focus rings.</p>
    """ + swatches([
        ('var(--adze-bg)', '#fbfbfd'),
        ('var(--adze-surface)', '#ffffff'),
        ('var(--adze-text)', '#1d1d1f'),
        ('var(--adze-accent)', '#1c4f82'),
        ('var(--adze-accent-text)', '#ffffff'),
        ('var(--adze-border)', '#e3e3e8'),
    ]) + """
  </div>

  <div class="panel">
    <h3>Derived — never set these directly</h3>
    """ + swatches([
        ('var(--adze-bg-sunken)', 'bg 94% + text'),
        ('var(--adze-surface-hover)', 'surface 96% + text'),
        ('var(--adze-border-strong)', 'border 55% + text'),
        ('var(--adze-text-muted)', 'text 62% + bg'),
        ('var(--adze-text-faint)', 'text 40% + bg'),
        ('var(--adze-accent-hover)', 'accent 86% + text'),
        ('var(--adze-accent-soft)', 'accent 10% + surface'),
        ('var(--adze-accent-line)', 'accent 32% + border'),
    ]) + """
  </div>

  <div class="panel">
    <h3>Status — fixed, not overridable</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">Status colours mean the same thing on every
    artist's admin. An artist whose accent is red must not get a red "saved".</p>
    """ + swatches([
        ('var(--adze-success)', '#1a8a52 / #4fc084'),
        ('var(--adze-warn)', '#a86b00 / #e0b055'),
        ('var(--adze-danger)', '#c8362a / #f0685c'),
    ]) + """
    <div class="row" style="margin-top:var(--adze-space-4)">
      <span class="adze-tag adze-tag--success"><span class="adze-tag__dot"></span>Live</span>
      <span class="adze-tag adze-tag--warn"><span class="adze-tag__dot"></span>Unpublished</span>
      <span class="adze-tag adze-tag--danger"><span class="adze-tag__dot"></span>Error</span>
    </div>
  </div>
</div>
""")

# ── The artist override, proven against real artist palettes ───────────────
DEMO = """
.demo { border-radius: var(--adze-radius-md); padding: var(--adze-space-4); border: 1px solid var(--adze-border); background: var(--adze-bg); }
.demo * { border-color: var(--adze-border); }
.demo-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--adze-space-3); }
.demo-title { font-size: var(--adze-text-sm); font-weight: var(--adze-weight-semibold); color: var(--adze-text); }
.demo-row { display: flex; align-items: center; gap: var(--adze-space-3); padding: var(--adze-space-2) 0; border-bottom: 1px solid var(--adze-border); }
.demo-row:last-of-type { border-bottom: 0; }
.demo-thumb { width: 32px; height: 32px; border-radius: var(--adze-radius-sm); background: var(--adze-bg-sunken); flex: 0 0 auto; }
.demo-name { flex: 1; font-size: var(--adze-text-xs); color: var(--adze-text); }
.demo-sub { font-size: 10px; color: var(--adze-text-muted); }
.demo-bar { height: 5px; border-radius: var(--adze-radius-pill); background: var(--adze-bg-sunken); overflow: hidden; margin-top: var(--adze-space-3); }
.demo-bar > i { display: block; height: 100%; width: 62%; background: var(--adze-accent); border-radius: var(--adze-radius-pill); }
.who { font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .06em; text-transform: uppercase; color: var(--adze-text-faint); margin-bottom: var(--adze-space-2); }
"""

def demo(who, css_vars):
    return """
<div>
  <div class="who">%s</div>
  <div class="demo adze-theme" style="%s">
    <div class="demo-head">
      <span class="demo-title">Gallery</span>
      <span class="adze-btn adze-btn--primary adze-btn--sm">Add</span>
    </div>
    <div class="demo-row"><span class="demo-thumb"></span><span class="demo-name">Study in Ochre<br><span class="demo-sub">Painting</span></span><span class="adze-tag adze-tag--success"><span class="adze-tag__dot"></span>Live</span></div>
    <div class="demo-row"><span class="demo-thumb"></span><span class="demo-name">Untitled #4<br><span class="demo-sub">Print</span></span><span class="adze-tag adze-tag--neutral">Draft</span></div>
    <div class="demo-bar"><i></i></div>
  </div>
</div>""" % (who, css_vars)


card('guidelines/color-artist-override.html', 'Colour', 'Artist override',
     'The same admin under five real artist palettes', 'Artist override',
     SWATCH + TAG + BTN + DEMO, """
<div class="stack">
  <div class="panel">
    <h3>The contract</h3>
    <p class="note">An artist sets six variables in their <code>config.json</code> under
    <code>admin_theme</code>. Nothing else is themeable — type, spacing, radius, motion and
    component behaviour are Adze's. That single axis of variation is what lets the loading
    states and the polish be built once and land on every artist's admin.</p>
    <p class="note" style="margin-top:var(--adze-space-3)"><b>Status colours deliberately do not
    change</b> — note the green "Live" chip holding steady across all five.</p>
  </div>
  <div class="panel">
    <h3>Same markup, five palettes</h3>
    <div class="grid" style="margin-top:var(--adze-space-4)">
""" + demo('adze (default)', '') +
    demo('mariaslaughter', '--adze-artist-bg:#0a0a0a;--adze-artist-surface:#161616;--adze-artist-text:#f0e6d6;--adze-artist-accent:#c9a573;--adze-artist-accent-text:#0a0a0a;--adze-artist-border:#3a3a3a;') +
    demo('rose', '--adze-artist-bg:#ffffff;--adze-artist-surface:#f8f8f8;--adze-artist-text:#000000;--adze-artist-accent:#000000;--adze-artist-accent-text:#ffffff;--adze-artist-border:#e8e8e8;') +
    demo('jackdt', '--adze-artist-bg:#f4f3ee;--adze-artist-surface:#fbfaf6;--adze-artist-text:#0b0d1a;--adze-artist-accent:#1a35ff;--adze-artist-accent-text:#ffffff;--adze-artist-border:#c7c5bd;') +
    demo('alfiebruce', '--adze-artist-bg:#000000;--adze-artist-surface:#111111;--adze-artist-text:#ffffff;--adze-artist-accent:#ffffff;--adze-artist-accent-text:#000000;--adze-artist-border:#262626;') + """
    </div>
  </div>
</div>
""")

card('guidelines/color-focus.html', 'Colour', 'Focus & states',
     'One ring everywhere; never colour alone', 'Focus', BTN + FORMS + TAG, """
<div class="grid">
  <div class="panel stack">
    <h3>The focus ring</h3>
    <p class="note">One ring, everywhere: a 3px accent-tinted halo via
    <code>--adze-focus-ring</code>, applied on <code>:focus-visible</code> only — so a mouse
    click doesn't ring but a Tab does.</p>
    <p class="note"><b>Tab through this card</b> to see it. Several places in the old chrome set
    <code>outline: none</code> and substituted a border-colour change, which fails at low contrast
    and vanishes entirely in dark mode.</p>
    <div class="row">
      <button class="adze-btn adze-btn--primary">Focus me</button>
      <button class="adze-btn adze-btn--secondary">And me</button>
      <a class="adze-link adze-link--standalone" href="#">A link</a>
    </div>
    <input class="adze-input" placeholder="And this input">
  </div>

  <div class="panel stack">
    <h3>Never colour alone</h3>
    <p class="note">Every state carries a second signal beside its colour — an icon, a dot, or
    text. Colour-only status is invisible to roughly 1 in 12 men.</p>
    <div class="adze-field adze-field--error">
      <div class="adze-field__head"><label class="adze-label">Slug</label></div>
      <input class="adze-input" value="">
      <p class="adze-field__error"><i class="ph ph-warning-circle"></i>Red border <b>plus</b> icon <b>plus</b> sentence.</p>
    </div>
    <div class="row">
      <span class="adze-tag adze-tag--success"><span class="adze-tag__dot"></span>Live</span>
      <span class="adze-tag adze-tag--warn"><span class="adze-tag__dot"></span>Unpublished</span>
      <span class="adze-tag adze-tag--danger"><span class="adze-tag__dot"></span>Error</span>
    </div>
    <p class="note">Tags carry a dot and a word, not just a hue.</p>
  </div>
</div>
""")


SPEC = """
.spec { display: flex; align-items: baseline; gap: var(--adze-space-4); padding: var(--adze-space-3) 0; border-bottom: 1px solid var(--adze-border); }
.spec:last-child { border-bottom: 0; }
.spec__tok { flex: 0 0 148px; font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .04em; color: var(--adze-text-faint); }
.spec__demo { flex: 1; min-width: 0; }
.bar { background: var(--adze-accent); border-radius: 2px; height: 14px; }
.box { background: var(--adze-accent-soft); border: 1px solid var(--adze-accent-line); }
"""

TYPE_ROWS = [
    ('--adze-text-display', '48px', 'Adze', 'font-size:48px;font-weight:600;letter-spacing:-0.02em;line-height:1.2'),
    ('--adze-text-3xl', '36px', 'Your sites', 'font-size:36px;font-weight:600;letter-spacing:-0.02em;line-height:1.2'),
    ('--adze-text-2xl', '28px', 'Gallery', 'font-size:28px;font-weight:600;letter-spacing:-0.01em;line-height:1.2'),
    ('--adze-text-xl', '22px', 'Recent works', 'font-size:22px;font-weight:600;letter-spacing:-0.01em;line-height:1.2'),
    ('--adze-text-lg', '18px', 'Section heading', 'font-size:18px;font-weight:600;line-height:1.35'),
    ('--adze-text-md', '15px', 'Card title / lead paragraph', 'font-size:15px;font-weight:600;line-height:1.35'),
    ('--adze-text-sm', '13px — BASE', 'Body copy, inputs, buttons and table cells all sit here.', 'font-size:13px;line-height:1.55'),
    ('--adze-text-xs', '12px', 'Secondary metadata and help text.', 'font-size:12px;line-height:1.55;color:var(--adze-text-muted)'),
    ('--adze-text-2xs', '11px — mono only', 'FIELD LABEL', 'font-family:var(--adze-font-mono);font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:var(--adze-text-muted)'),
]

card('guidelines/type-scale.html', 'Type', 'Scale',
     '11 → 48px, 13px base', 'Type scale', SPEC, """
<div class="panel">
  <h3>Scale</h3>
  <p class="note" style="margin-bottom:var(--adze-space-4)">~1.2 ratio, tuned to land on whole pixels.
  Base is <b>13px</b> — the old chrome ran at 10–11px, which is why it felt cramped.
  Nothing goes below <code>--adze-text-2xs</code>, and 2xs is mono-only.</p>
""" + '\n'.join(
    '<div class="spec"><div class="spec__tok">%s<br>%s</div>'
    '<div class="spec__demo"><span style="%s">%s</span></div></div>' % (tok, size, style, text)
    for tok, size, text, style in TYPE_ROWS) + """
</div>
""")

card('guidelines/type-voice.html', 'Type', 'Two voices',
     'Inter reads, JetBrains Mono scans', 'Two voices', SPEC + TAG + FORMS, """
<div class="stack">
  <div class="panel">
    <h3>The division of labour</h3>
    <p class="note">This is the "halfway between Apple and mono" rule made mechanical.
    <b>Inter</b> for anything a person <b>reads</b>. <b>JetBrains Mono</b> for anything a person
    <b>scans</b>.</p>
    <p class="note" style="margin-top:var(--adze-space-3)"><b>The test:</b> if you'd read it aloud
    in a sentence, it's Inter. If your eye lands on it to find a value, it's mono. Getting this
    wrong in either direction is what made the old chrome read as a control panel — mono headings
    shout, and Inter labels disappear.</p>
  </div>
  <div class="grid">
    <div class="panel">
      <h3 style="font-family:var(--adze-font-ui)">Inter — read</h3>
      <p style="font-size:22px;font-weight:600;letter-spacing:-0.01em;margin:0 0 var(--adze-space-3)">Your gallery</p>
      <p style="margin:0">Headings, body copy, button labels, form values, prose. Everything the
      user actually reads as language.</p>
    </div>
    <div class="panel">
      <h3 style="font-family:var(--adze-font-ui)">JetBrains Mono — scan</h3>
      <div class="adze-label" style="margin-bottom:var(--adze-space-2)">Field label</div>
      <div class="row" style="margin-bottom:var(--adze-space-3)">
        <span class="adze-tag adze-tag--success"><span class="adze-tag__dot"></span>Live</span>
        <span class="adze-tag adze-tag--neutral">Draft</span>
      </div>
      <div class="adze-numeric" style="font-size:22px">1,284</div>
      <div class="adze-numeric" style="font-size:12px;color:var(--adze-text-muted)">2026-07-30 · 4.2 MB</div>
      <p class="note" style="margin-top:var(--adze-space-3)">Labels, status chips, counts, dates,
      sizes, IDs. Tabular figures stop columns twitching as values update.</p>
    </div>
  </div>
  <div class="panel">
    <h3>Getting it wrong</h3>
    <div class="grid">
      <div>
        <div class="who" style="font-family:var(--adze-font-mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--adze-danger);margin-bottom:var(--adze-space-2)">✗ mono heading — shouts</div>
        <p style="font-family:var(--adze-font-mono);font-size:22px;font-weight:700;margin:0">YOUR GALLERY</p>
      </div>
      <div>
        <div class="who" style="font-family:var(--adze-font-mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--adze-danger);margin-bottom:var(--adze-space-2)">✗ Inter label — disappears</div>
        <p style="font-size:11px;color:var(--adze-text-muted);margin:0">Title</p>
        <input class="adze-input" style="width:100%;margin-top:4px" value="Study in Ochre" readonly>
      </div>
    </div>
  </div>
</div>
""" .replace('.adze-input', '.adze-input'))

card('guidelines/spacing-scale.html', 'Layout', 'Spacing & sizing',
     '4px grid, control heights, widths', 'Spacing', SPEC, """
<div class="stack">
  <div class="panel">
    <h3>Space scale</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">4px grid. The old chrome had no scale
    at all — <code>2px 6px</code>, <code>4px 10px</code>, <code>5px 11px</code>,
    <code>7px 10px</code>, every value invented at the call site. That's why nothing lined up.</p>
""" + '\n'.join(
    '<div class="spec"><div class="spec__tok">--adze-space-%s<br>%spx</div>'
    '<div class="spec__demo"><div class="bar" style="width:%spx"></div></div></div>' % (n, px, px)
    for n, px in [(1,4),(2,8),(3,12),(4,16),(5,20),(6,24),(8,32),(10,40),(12,48),(16,64)]) + """
  </div>
  <div class="grid">
    <div class="panel">
      <h3>Control heights</h3>
      <p class="note" style="margin-bottom:var(--adze-space-4)">Shared by every button, input and
      select so they align when placed in a row.</p>
""" + '\n'.join(
    '<div class="spec"><div class="spec__tok">--adze-control-%s<br>%spx</div>'
    '<div class="spec__demo"><div class="box" style="height:%spx;border-radius:8px"></div></div></div>' % (n, px, px)
    for n, px in [('sm',28),('md',36),('lg',44)]) + """
      <p class="note" style="margin-top:var(--adze-space-4)">Below 640px these grow to 36/44/48 —
      the 44px touch minimum. The old admin used 28px buttons on mobile, which is where artists
      actually use it.</p>
    </div>
    <div class="panel">
      <h3>Layout widths</h3>
""" + '\n'.join(
    '<div class="spec"><div class="spec__tok">--adze-width-%s<br>%s</div>'
    '<div class="spec__demo"><span class="note">%s</span></div></div>' % (n, v, d)
    for n, v, d in [('prose','68ch','Readable text column'),
                    ('form','560px','Single-column form'),
                    ('content','720px','Content admin main column'),
                    ('wide','1140px','Dashboard / multi-column')]) + """
    </div>
  </div>
</div>
""")

card('guidelines/radius-elevation.html', 'Layout', 'Radius & elevation',
     'Four radii, three two-layer shadows', 'Radius', SPEC, """
<div class="grid">
  <div class="panel">
    <h3>Radius</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">Four values, no more. The old chrome
    declared <code>--radius:4px</code> then hardcoded 8px 32 times, 6px 25 times, and
    2/3/5/10/12/20 besides.</p>
""" + '\n'.join(
    '<div class="spec"><div class="spec__tok">--adze-radius-%s<br>%s</div>'
    '<div class="spec__demo"><div class="box" style="height:44px;width:88px;border-radius:%s"></div>'
    '<span class="note">%s</span></div></div>' % (n, v, v, d)
    for n, v, d in [('sm','4px','Chips, tags, inline code'),
                    ('md','8px','BASE — buttons, inputs, cards'),
                    ('lg','12px','Modals, panels, images'),
                    ('pill','999px','Tabs, avatars, toggles')]) + """
  </div>
  <div class="panel">
    <h3>Elevation</h3>
    <p class="note" style="margin-bottom:var(--adze-space-6)">Two-layer shadows — a tight contact
    shadow plus a soft ambient one. A single-layer shadow is the main thing that makes a UI read
    as dated.</p>
    <div style="display:flex;flex-direction:column;gap:var(--adze-space-8);padding:var(--adze-space-2) 0">
      <div style="background:var(--adze-surface);border:1px solid var(--adze-border);border-radius:8px;padding:var(--adze-space-4);box-shadow:var(--adze-shadow-sm)"><span class="spec__tok">--adze-shadow-sm</span><br><span class="note">Resting cards, inputs</span></div>
      <div style="background:var(--adze-surface);border:1px solid var(--adze-border);border-radius:8px;padding:var(--adze-space-4);box-shadow:var(--adze-shadow-md)"><span class="spec__tok">--adze-shadow-md</span><br><span class="note">Hovered cards, popovers</span></div>
      <div style="background:var(--adze-surface);border:1px solid var(--adze-border);border-radius:8px;padding:var(--adze-space-4);box-shadow:var(--adze-shadow-lg)"><span class="spec__tok">--adze-shadow-lg</span><br><span class="note">Modals, drawers</span></div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-6)">Dark mode swaps to deeper, tighter
    shadows — the soft ambient layer is invisible on a dark background and only muddies the edge.</p>
  </div>
</div>
""")


MOTION = """
.mo { display: flex; align-items: center; gap: var(--adze-space-4); padding: var(--adze-space-3) 0; border-bottom: 1px solid var(--adze-border); }
.mo:last-child { border-bottom: 0; }
.mo__tok { flex: 0 0 190px; font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .04em; color: var(--adze-text-faint); }
.mo__track { flex: 1; height: 28px; background: var(--adze-bg-sunken); border-radius: var(--adze-radius-pill); position: relative; overflow: hidden; }
.mo__dot { position: absolute; top: 4px; left: 4px; width: 20px; height: 20px; border-radius: 50%; background: var(--adze-accent); }
.run .mo__dot { transform: translateX(calc(100% * 0 + var(--travel))); }
"""

card('guidelines/motion-timing.html', 'Motion', 'Timing & easing',
     'Five durations, four curves — press to run', 'Motion', MOTION + BTN, """
<div class="stack">
  <div class="panel">
    <h3>Motion</h3>
    <p class="note">The old chrome had four durations by accident (0.12s, 0.15s, 0.2s, 0.3s) and
    no easing at all, so everything moved linearly. Linear motion is the clearest tell of a dated
    interface — real objects don't start and stop instantly.</p>
    <p class="note" style="margin-top:var(--adze-space-3)">Things <b>entering</b> use
    <code>--adze-ease-out</code>. Things <b>leaving</b> use <code>--adze-ease-in</code> and a
    shorter duration; nobody wants to wait for a dismissal. Nothing exceeds
    <code>--adze-dur-slower</code> — if it needs longer, it's a progress state, not a transition.</p>
    <div class="row" style="margin-top:var(--adze-space-4)">
      <button class="adze-btn adze-btn--primary" onclick="run()">Run all</button>
    </div>
  </div>

  <div class="panel" id="stage">
    <h3>Duration</h3>
    <div class="mo"><div class="mo__tok">--adze-dur-instant<br>80ms</div><div class="mo__track"><div class="mo__dot" data-d="80" data-e="var(--adze-ease-out)"></div></div></div>
    <div class="mo"><div class="mo__tok">--adze-dur-fast<br>140ms · BASE</div><div class="mo__track"><div class="mo__dot" data-d="140" data-e="var(--adze-ease-out)"></div></div></div>
    <div class="mo"><div class="mo__tok">--adze-dur<br>220ms</div><div class="mo__track"><div class="mo__dot" data-d="220" data-e="var(--adze-ease-out)"></div></div></div>
    <div class="mo"><div class="mo__tok">--adze-dur-slow<br>320ms</div><div class="mo__track"><div class="mo__dot" data-d="320" data-e="var(--adze-ease-out)"></div></div></div>
    <div class="mo"><div class="mo__tok">--adze-dur-slower<br>480ms</div><div class="mo__track"><div class="mo__dot" data-d="480" data-e="var(--adze-ease-out)"></div></div></div>

    <h3 style="margin:var(--adze-space-8) 0 var(--adze-space-2)">Easing — all at 480ms</h3>
    <div class="mo"><div class="mo__tok">--adze-ease-out<br>fast start, soft landing</div><div class="mo__track"><div class="mo__dot" data-d="480" data-e="cubic-bezier(0.16,1,0.3,1)"></div></div></div>
    <div class="mo"><div class="mo__tok">--adze-ease-in<br>exits only</div><div class="mo__track"><div class="mo__dot" data-d="480" data-e="cubic-bezier(0.4,0,1,1)"></div></div></div>
    <div class="mo"><div class="mo__tok">--adze-ease-in-out<br>continuous / looping</div><div class="mo__track"><div class="mo__dot" data-d="480" data-e="cubic-bezier(0.4,0,0.2,1)"></div></div></div>
    <div class="mo"><div class="mo__tok">--adze-ease-spring<br>toggles, checks</div><div class="mo__track"><div class="mo__dot" data-d="480" data-e="cubic-bezier(0.34,1.4,0.64,1)"></div></div></div>
    <div class="mo"><div class="mo__tok">linear<br>never — for comparison</div><div class="mo__track"><div class="mo__dot" data-d="480" data-e="linear" style="background:var(--adze-danger)"></div></div></div>
  </div>

  <div class="panel">
    <h3>Reduced motion</h3>
    <p class="note">Every duration collapses to 1ms under
    <code>prefers-reduced-motion</code> — transitions aren't removed, so state changes still land,
    they just land immediately. Looping feedback (spinners, progress bars) keeps animating but
    slowly and without translation: it still needs to say "working".</p>
    <p class="note" style="margin-top:var(--adze-space-3)">This is load-bearing, not box-ticking —
    an animated progress bar that can't be turned off is a genuine problem for people with
    vestibular disorders.</p>
  </div>
</div>

<script>
function run() {
  document.querySelectorAll('.mo__dot').forEach(function (dot) {
    var track = dot.parentElement;
    var travel = track.clientWidth - 28;
    dot.style.transition = 'none';
    dot.style.transform = 'translateX(0)';
    void dot.offsetWidth;
    dot.style.transition = 'transform ' + dot.dataset.d + 'ms ' + dot.dataset.e;
    dot.style.transform = 'translateX(' + travel + 'px)';
  });
  setTimeout(function () {
    document.querySelectorAll('.mo__dot').forEach(function (dot) {
      dot.style.transition = 'transform 300ms cubic-bezier(0.4,0,1,1)';
      dot.style.transform = 'translateX(0)';
    });
  }, 1400);
}
setTimeout(run, 400);
setInterval(run, 3200);
</script>
""")


# ── Layout doctrine ────────────────────────────────────────────────────────
LAYOUT = """
.verdict { display: inline-flex; align-items: center; gap: var(--adze-space-1); font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .06em; text-transform: uppercase; margin-bottom: var(--adze-space-2); }
.verdict--yes { color: var(--adze-success); }
.verdict--no { color: var(--adze-danger); }
.verdict i { font-size: 1.25em; }
.stage { resize: horizontal; overflow: auto; min-width: 240px; max-width: 100%; padding: var(--adze-space-4); background: var(--adze-bg-sunken); border: 1px dashed var(--adze-border-strong); border-radius: var(--adze-radius-md); }
.autofit { display: grid; grid-template-columns: repeat(auto-fit, minmax(var(--adze-col-min), 1fr)); gap: var(--adze-space-4); }
.autofit .adze-field { margin-bottom: 0; }
.formw { max-width: var(--adze-width-form); }
.works { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: var(--adze-space-4); }
.work { border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md); background: var(--adze-surface); box-shadow: var(--adze-shadow-sm); overflow: hidden; }
.work__img { aspect-ratio: 4 / 5; background: linear-gradient(150deg, color-mix(in srgb, var(--adze-accent) var(--m), var(--adze-surface)), var(--adze-bg-sunken)); }
.work__meta { padding: var(--adze-space-3); display: flex; flex-direction: column; gap: var(--adze-space-1); }
.work__t { font-size: var(--adze-text-sm); font-weight: var(--adze-weight-medium); }
.ledger { border-top: 1px solid var(--adze-border); }
.ledger > div { display: flex; align-items: baseline; justify-content: space-between; gap: var(--adze-space-4); padding: var(--adze-space-3) 0; border-bottom: 1px solid var(--adze-border); font-size: var(--adze-text-sm); }
.own { background: var(--adze-bg-sunken); border-radius: var(--adze-radius-md); padding: var(--adze-space-4); display: flex; flex-direction: column; gap: var(--adze-space-4); }
.own .adze-field { background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); padding: var(--adze-space-3); }
.own--fixed .adze-field { margin-bottom: 0; }
.code { margin: 0; padding: var(--adze-space-3); background: var(--adze-bg-sunken); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); font-family: var(--adze-font-mono); font-size: var(--adze-text-xs); line-height: var(--adze-leading-relaxed); color: var(--adze-text-muted); overflow-x: auto; }
.code b { color: var(--adze-text); font-weight: var(--adze-weight-medium); }
"""

ROLE_ROWS = [
    ('identity', 'Title, slug',
     'First, on its own line. It names the thing; nothing shares its row.'),
    ('media', 'Image, upload',
     'Immediately after identity. An artist should see the picture before they see a text box.'),
    ('short', 'Year, medium, dimensions, price',
     'Packed into one auto-fit group at minmax(var(--adze-col-min), 1fr), so related metadata shares a row.'),
    ('long', 'Description, statement',
     'Full width of the form column — which is 560px, not the viewport.'),
    ('tags', 'Categories, collections',
     'Full width, below the long fields. Chips wrap; they do not need a column.'),
]

SHORT_FIELDS = [('Year', '2026'), ('Medium', 'Oil on linen'),
                ('Dimensions', '120 × 90 cm'), ('Price', '£2,400')]


def short_group():
    return '\n'.join(
        '<div class="adze-field"><div class="adze-field__head">'
        '<label class="adze-label">%s</label></div>'
        '<input class="adze-input" value="%s" readonly></div>' % (label, val)
        for label, val in SHORT_FIELDS)


WORK_ITEMS = [('22%', 'Study in Ochre', '2026 · oil'),
              ('9%', 'Untitled #4', '2026 · print'),
              ('34%', 'Low Tide', '2025 · oil'),
              ('15%', 'Margate, June', '2025 · photo'),
              ('27%', 'Cast I', '2024 · plaster'),
              ('6%', 'Sketch for Ochre', '2024 · pencil')]

LONG_TEXT = ("Painter working between London and Margate. Recent work is "
             "concerned with tidal light and the way a flat horizon refuses to "
             "hold still for long enough to be painted.")


def form_specimen(long_line):
    return """
<div class="adze-field">
  <div class="adze-field__head"><label class="adze-label">Title<span class="adze-field__req">*</span></label></div>
  <input class="adze-input" value="Study in Ochre" readonly>
</div>
<div class="adze-field">
  <div class="adze-field__head"><label class="adze-label">Statement</label></div>
  <textarea class="adze-input adze-input--textarea" readonly>""" + long_line + """</textarea>
</div>"""


card('guidelines/layout-columns.html', 'Layout', 'Layout & columns',
     'Auto-fit, not breakpoints — and the form stays 560px', 'Layout & columns',
     BTN + TAG + FORMS + SPEC + LAYOUT, """
<div class="stack">
  <div class="panel">
    <h3>A wider viewport means more columns, never longer lines</h3>
    <p class="note">This is the one people get wrong when they set out to "make it use the
    space". The <b>list</b> may widen on a large screen. The <b>form</b> does not — it stays at
    <code>--adze-width-form</code>, 560px, at every viewport. A 900px-wide text input is worse to
    use than a 560px one: the caret is a long way from the label, the value floats alone in a field
    of nothing, and a paragraph of prose runs past the ~75 characters an eye can track back from.</p>
    <div class="verdict verdict--yes" style="margin-top:var(--adze-space-6)"><i class="ph ph-check"></i>max-width: var(--adze-width-form)</div>
    <div class="formw">""" + form_specimen(LONG_TEXT) + """</div>
    <div class="verdict verdict--no" style="margin-top:var(--adze-space-6)"><i class="ph ph-x"></i>stretched to fill the container</div>
    <div>""" + form_specimen(LONG_TEXT) + """</div>
    <p class="note" style="margin-top:var(--adze-space-4)">Same fields, same tokens, more pixels
    spent. The second one is not more capable — it is the same form with a longer journey across
    it. Space earned by a wide screen is spent on <b>columns</b>, never on line length. On a narrow
    screen the two are identical, which is the whole point: the divergence only appears once there
    is room to misuse.</p>
  </div>

  <div class="panel">
    <h3>Auto-fit grids, not breakpoints</h3>
    <p class="note"><code>repeat(auto-fit, minmax(200px, 1fr))</code> reflows by the width actually
    available, has no breakpoints to maintain, and degrades correctly at every viewport — including
    the ones nobody tested. A media query is only warranted for something auto-fit genuinely cannot
    express: the touch-target height bump at 640px in <code>tokens/spacing.css</code> is the whole
    list. Every media query added after that is a future inconsistency, because the next person will
    add theirs at a different number.</p>
    <p class="note" style="margin-top:var(--adze-space-3)"><b>Drag the bottom-right corner</b> of
    the panel below. Four short fields go 4 → 2 → 1 without a single query.
    <i class="ph ph-arrows-horizontal" style="vertical-align:-.15em"></i></p>
    <div class="stage" style="margin-top:var(--adze-space-4)">
      <div class="autofit">""" + short_group() + """</div>
    </div>
    <pre class="code" style="margin-top:var(--adze-space-4)"><b>display</b>: grid;
<b>grid-template-columns</b>: repeat(auto-fit, minmax(var(--adze-col-min), 1fr));
<b>gap</b>: var(--adze-space-4);</pre>
  </div>

  <div class="panel">
    <h3>Layout is derived from field role, not declared per project</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">A field's <b>role</b> decides where it
    lands. Nothing in a schema says "put this in column two" — the schema says what the field
    <i>is</i>, and the layout follows. That is what lets a brand-new project get a good layout from
    a schema that says nothing about layout at all.</p>
""" + '\n'.join(
    '<div class="spec"><div class="spec__tok">%s</div>'
    '<div class="spec__demo"><div style="font-size:var(--adze-text-sm)">%s</div>'
    '<span class="note">%s</span></div></div>' % (role, egs, rule)
    for role, egs, rule in ROLE_ROWS) + """
    <div class="verdict verdict--yes" style="margin-top:var(--adze-space-6)"><i class="ph ph-check"></i>the whole form, derived</div>
    <div class="formw">
      <div class="adze-field">
        <div class="adze-field__head"><label class="adze-label">Title<span class="adze-field__req">*</span></label></div>
        <input class="adze-input" value="Study in Ochre" readonly>
      </div>
      <div class="adze-field">
        <div class="adze-field__head"><label class="adze-label">Image</label></div>
        <div class="work" style="max-width:180px"><div class="work__img" style="--m:22%"></div></div>
      </div>
      <div class="autofit" style="margin-bottom:var(--adze-space-4)">""" + short_group() + """</div>
      <div class="adze-field">
        <div class="adze-field__head"><label class="adze-label">Statement</label></div>
        <textarea class="adze-input adze-input--textarea" readonly>""" + LONG_TEXT + """</textarea>
      </div>
      <div class="adze-field">
        <div class="adze-field__head"><label class="adze-label">Tags</label></div>
        <div class="row">
          <span class="adze-tag adze-tag--neutral">Painting</span>
          <span class="adze-tag adze-tag--neutral">2026</span>
          <span class="adze-tag adze-tag--accent">Featured</span>
        </div>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-6)">The escape hatches are deliberately
    tiny — two keys, not a layout DSL. If you reach for a third, the role is wrong.</p>
    <pre class="code" style="margin-top:var(--adze-space-3)">field       { "role": "short" }                    packed into the auto-fit group
field       { "role": "short", <b>"width": "full"</b> }   the one per-field override
collection  { <b>"list": "grid"</b> }                     or "rows" — the one per-collection override</pre>
  </div>

  <div class="panel">
    <h3>A list of visual things is a grid of pictures</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">If the items have images, show the
    images. An artist scanning their own gallery recognises a painting in a fraction of the time it
    takes them to read its title — and half their titles are "Untitled".</p>
    <div class="grid">
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>list: "grid"</div>
        <div class="works">
""" + '\n'.join(
    '<div class="work"><div class="work__img" style="--m:%s"></div>'
    '<div class="work__meta"><span class="work__t">%s</span>'
    '<span class="mono">%s</span></div></div>' % (m, t, meta)
    for m, t, meta in WORK_ITEMS) + """
        </div>
      </div>
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>a ledger of titles</div>
        <div class="ledger">
""" + '\n'.join(
    '<div><span>%s</span><span class="adze-numeric mono">%s</span></div>' % (t, meta)
    for m, t, meta in WORK_ITEMS) + """
        </div>
        <p class="note" style="margin-top:var(--adze-space-3)">Everything the artist made, reduced
        to the one attribute a database found easiest to print.</p>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-6)"><b>The corollary is not optional.</b>
    A grid of pictures requires an image tier sized for cards. Serving the 2000px display image into
    a 200px slot is how a gallery of <span class="adze-numeric">32</span> works becomes a
    <span class="adze-numeric">25 MB</span> page load — on a phone, on the artist's own data. Cut a
    card tier at roughly <span class="adze-numeric">400px</span> and point the grid at it. If there
    is no card tier yet, that is the work; it is not a detail to follow later.</p>
  </div>

  <div class="panel">
    <h3>One spacing owner per stack</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">A container using <code>gap</code>
    whose children also carry <code>margin-bottom</code> gets both. Nothing errors — the form simply
    runs looser in one place than another, and the two drift further apart every time someone tunes
    one of them. This is a live bug class in this codebase: <code>.as-feedback</code> uses a flex
    <code>gap</code>, so its <code>.af-field</code> children have their bottom margin zeroed;
    without that the same form ran 32px there against 20px in the content admin.</p>
    <div class="grid">
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>gap 16 + margin-bottom 16 = <span class="adze-numeric">32px</span></div>
        <div class="own">""" + short_group() + """</div>
      </div>
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>gap owns it, margin zeroed = <span class="adze-numeric">16px</span></div>
        <div class="own own--fixed">""" + short_group() + """</div>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-4)">Pick one owner and say so where the
    container is defined. The trailing margin under the last child is the same bug wearing a hat —
    it is why a stack so often sits lower in its box than it sits in its own padding.</p>
  </div>
</div>
""")


# ── Motion choreography ────────────────────────────────────────────────────
CHOREO = """
.verdict { display: inline-flex; align-items: center; gap: var(--adze-space-1); font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .06em; text-transform: uppercase; margin-bottom: var(--adze-space-2); }
.verdict--yes { color: var(--adze-success); }
.verdict--no { color: var(--adze-danger); }
.verdict i { font-size: 1.25em; }
.chor { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: var(--adze-space-6); }
.pane { min-height: 210px; background: var(--adze-bg-sunken); border-radius: var(--adze-radius-md); padding: var(--adze-space-3); cursor: pointer; }

.se__row { display: flex; align-items: center; gap: var(--adze-space-3); overflow: hidden; max-height: 60px; padding: var(--adze-space-2); margin-bottom: var(--adze-space-2); background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); transition: opacity var(--adze-dur) var(--adze-ease-out), transform var(--adze-dur) var(--adze-ease-out), max-height var(--adze-dur) var(--adze-ease-out), margin var(--adze-dur) var(--adze-ease-out), padding var(--adze-dur) var(--adze-ease-out); }
.se.is-open .se__row { opacity: 0; transform: translateY(-4px); max-height: 0; margin-bottom: 0; padding-top: 0; padding-bottom: 0; border-width: 0; transition: opacity var(--adze-dur-fast) var(--adze-ease-in), transform var(--adze-dur-fast) var(--adze-ease-in), max-height var(--adze-dur-fast) var(--adze-ease-in), margin var(--adze-dur-fast) var(--adze-ease-in), padding var(--adze-dur-fast) var(--adze-ease-in); }
.se.is-open .se__row.is-target { opacity: 1; transform: none; max-height: 180px; padding: var(--adze-space-3); border-width: 1px; align-items: flex-start; transition: max-height var(--adze-dur) var(--adze-ease-out), padding var(--adze-dur) var(--adze-ease-out); }
.se__thumb { flex: 0 0 auto; width: 36px; height: 36px; border-radius: var(--adze-radius-sm); background: linear-gradient(150deg, color-mix(in srgb, var(--adze-accent) 26%, var(--adze-surface)), var(--adze-bg-sunken)); transition: width var(--adze-dur) var(--adze-ease-out), height var(--adze-dur) var(--adze-ease-out); }
.se.is-open .is-target .se__thumb { width: 84px; height: 105px; }
.se__t { font-size: var(--adze-text-sm); font-weight: var(--adze-weight-medium); }
.se__body { max-height: 0; opacity: 0; overflow: hidden; transition: opacity var(--adze-dur-fast) var(--adze-ease-in), max-height var(--adze-dur-fast) var(--adze-ease-in); }
.se.is-open .is-target .se__body { max-height: 90px; opacity: 1; transition: opacity var(--adze-dur) var(--adze-ease-out) var(--adze-dur-fast), max-height var(--adze-dur) var(--adze-ease-out); }

.xf { position: relative; }
.xf__layer { position: absolute; inset: var(--adze-space-3); transition: opacity var(--adze-dur) var(--adze-ease-in-out); }
.xf__layer--detail { opacity: 0; }
.xf.is-open .xf__layer--list { opacity: 0; }
.xf.is-open .xf__layer--detail { opacity: 1; }

.ee { position: relative; height: 104px; display: grid; place-items: center; background: var(--adze-bg-sunken); border-radius: var(--adze-radius-md); }
.ee__toast { display: inline-flex; align-items: center; gap: var(--adze-space-2); padding: var(--adze-space-2) var(--adze-space-4); background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-pill); box-shadow: var(--adze-shadow-md); font-size: var(--adze-text-xs); opacity: 0; transform: translateY(8px); transition: opacity var(--adze-dur-fast) var(--adze-ease-in), transform var(--adze-dur-fast) var(--adze-ease-in); }
.ee__toast.is-in { opacity: 1; transform: none; transition: opacity var(--adze-dur) var(--adze-ease-out), transform var(--adze-dur) var(--adze-ease-out); }
.ee--wrong .ee__toast, .ee--wrong .ee__toast.is-in { transition: opacity var(--adze-dur-slow) var(--adze-ease-in-out), transform var(--adze-dur-slow) var(--adze-ease-in-out); }

.stag { display: grid; grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)); gap: var(--adze-space-2); }
.stag__row { display: flex; align-items: center; gap: var(--adze-space-2); padding: var(--adze-space-2); background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); font-size: var(--adze-text-xs); }
.stag__thumb { flex: 0 0 auto; width: 18px; height: 18px; border-radius: var(--adze-radius-sm); background: var(--adze-accent-soft); }
.stag.is-run .stag__row { animation: adze-rise-in var(--adze-dur) var(--adze-ease-out) both; }
.stag--capped.is-run .stag__row { animation-delay: calc(min(var(--i), 8) * var(--adze-dur-fast) / 4); }
.stag--free.is-run .stag__row { animation-delay: calc(var(--i) * var(--adze-dur-fast) / 4); }

.re { background: var(--adze-bg-sunken); border-radius: var(--adze-radius-md); padding: var(--adze-space-4); }
.re__panel { background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md); box-shadow: var(--adze-shadow-sm); padding: var(--adze-space-4); display: flex; flex-direction: column; gap: var(--adze-space-3); }
.re__panel.is-entering { animation: adze-rise-in var(--adze-dur-slow) var(--adze-ease-out) both; }
.re__chip { opacity: 0; }
.re__chip.is-in { animation: adze-rise-in var(--adze-dur) var(--adze-ease-out) both; }

@keyframes chor-fill { from { width: 6%; } to { width: 94%; } }
.pbar { height: 6px; border-radius: var(--adze-radius-pill); background: var(--adze-bg-sunken); overflow: hidden; }
.pbar > i { display: block; height: 100%; background: var(--adze-accent); border-radius: var(--adze-radius-pill); animation: chor-fill 2.4s var(--adze-ease-in-out) infinite alternate; }
.code { margin: 0; padding: var(--adze-space-3); background: var(--adze-bg-sunken); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); font-family: var(--adze-font-mono); font-size: var(--adze-text-xs); line-height: var(--adze-leading-relaxed); color: var(--adze-text-muted); overflow-x: auto; }
.code b { color: var(--adze-text); font-weight: var(--adze-weight-medium); }
"""

SE_ROWS = [('Study in Ochre', '2026 · oil'), ('Untitled #4', '2026 · print'),
           ('Low Tide', '2025 · oil')]

STAG_ROWS = '\n'.join(
    '<div class="stag__row" style="--i:%d"><span class="stag__thumb"></span>'
    '<span>Work %02d</span></div>' % (i, i + 1)
    for i in range(32))


card('guidelines/motion-choreography.html', 'Motion', 'Motion choreography',
     'What moves, and why — arrival, exit, stagger, entrance', 'Motion choreography',
     BTN + TAG + CHOREO, """
<div class="stack">
  <div class="panel">
    <h3>What moves, and why</h3>
    <p class="note"><b>Timing &amp; easing</b> covers how long a movement takes and what curve it
    rides. This covers the harder question: what should move at all, and what the movement is
    telling the person watching it. Motion in this system has exactly one job — to explain
    <b>where a thing came from and where it went</b>. Motion that decorates is motion that has to be
    sat through, every time, forever.</p>
    <p class="note" style="margin-top:var(--adze-space-3)">The test: remove the animation and ask
    whether anything became harder to follow. If nothing did, the animation was never doing work.</p>
  </div>

  <div class="panel">
    <h3>List to detail is one element moving, not two elements fading</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">A crossfade says one screen ended and
    another began. A shared element says <i>that row is this page</i> — the thumbnail the artist
    clicked is the thumbnail they are now looking at, so they never have to work out where they
    are. Reuse the element and let it transition; don't build a second copy and dissolve between
    them. <b>Click either panel.</b></p>
    <div class="chor">
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>crossfade — where did it go?</div>
        <div class="pane xf" id="xf">
          <div class="xf__layer xf__layer--list">
""" + '\n'.join(
    '<div class="se__row"><span class="se__thumb"></span>'
    '<span class="se__t">%s<br><span class="mono">%s</span></span></div>' % (t, m)
    for t, m in SE_ROWS) + """
          </div>
          <div class="xf__layer xf__layer--detail">
            <div class="se__row" style="max-height:none;align-items:flex-start;padding:var(--adze-space-3)">
              <span class="se__thumb" style="width:84px;height:105px"></span>
              <span class="se__t">Study in Ochre<br><span class="mono">2026 · oil</span></span>
            </div>
          </div>
        </div>
      </div>
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>shared element — the row becomes the page</div>
        <div class="pane se" id="se">
          <div class="se__row is-target">
            <span class="se__thumb"></span>
            <span class="se__t">Study in Ochre<br><span class="mono">2026 · oil</span>
              <span class="se__body" style="display:block"><span class="note" style="display:block;margin-top:var(--adze-space-2)">Oil on linen, 120 × 90 cm. The detail view grew out of the row; nothing was replaced.</span></span>
            </span>
          </div>
""" + '\n'.join(
    '<div class="se__row"><span class="se__thumb"></span>'
    '<span class="se__t">%s<br><span class="mono">%s</span></span></div>' % (t, m)
    for t, m in SE_ROWS[1:]) + """
        </div>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-4)">The siblings leave with
    <code>--adze-ease-in</code> at <code>--adze-dur-fast</code> while the target arrives with
    <code>--adze-ease-out</code> at <code>--adze-dur</code>. The thing you are going to is the
    thing that gets the time.</p>
  </div>

  <div class="panel">
    <h3>Entering and leaving are not the same motion</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">Something arriving is announcing
    itself: <code>--adze-ease-out</code>, fast start, soft landing, <code>--adze-dur</code>.
    Something leaving is getting out of the way: <code>--adze-ease-in</code> and a
    <b>shorter</b> duration — <code>--adze-dur-fast</code>. Nobody has ever wanted to wait for a
    dismissal. Write the leave timing as the element's resting state and let the
    <code>.is-in</code> class override it; then each direction is stated once and cannot drift.</p>
    <div class="chor">
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>enters ease-out 220ms · leaves ease-in 140ms</div>
        <div class="ee"><span class="ee__toast"><i class="ph ph-check-circle" style="color:var(--adze-success)"></i>Saved</span></div>
      </div>
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>ease-in-out 320ms, both directions</div>
        <div class="ee ee--wrong"><span class="ee__toast"><i class="ph ph-check-circle" style="color:var(--adze-success)"></i>Saved</span></div>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-4)">The second one is not slower by much.
    It just refuses to leave, and a person who saves twenty times an hour feels every one of them.</p>
  </div>

  <div class="panel">
    <h3>Stagger must be capped</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">A per-row delay is lovely at six rows
    and absurd at thirty-two. Cap the index at <b>8</b> — after that every remaining row shares the
    last delay, so the wave still reads but the list finishes arriving. The step here is
    <code>--adze-dur-fast / 4</code>, which puts the capped total inside
    <code>--adze-dur-slow</code>. Uncapped, the last row of thirty-two lands past
    <code>--adze-dur-slower</code>, at which point the system's own rule says it stopped being a
    transition — and it is a very bad progress bar, because nothing is loading.</p>
    <div class="row" style="margin-bottom:var(--adze-space-4)">
      <button class="adze-btn adze-btn--primary adze-btn--sm" id="b-cap">Capped at 8</button>
      <button class="adze-btn adze-btn--secondary adze-btn--sm" id="b-free">Uncapped</button>
      <span class="note">last row arrives at <span class="adze-numeric" id="lastdelay">280ms</span></span>
    </div>
    <div class="stag stag--capped" id="stag">
""" + STAG_ROWS + """
    </div>
    <pre class="code" style="margin-top:var(--adze-space-4)"><b>animation</b>: adze-rise-in var(--adze-dur) var(--adze-ease-out) both;
<b>animation-delay</b>: calc(min(var(--i), 8) * var(--adze-dur-fast) / 4);</pre>
  </div>

  <div class="panel">
    <h3>An entrance fires on enter, not on every render</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">A panel's entrance animation belongs
    to the panel <i>appearing</i>. Tie it to a re-render instead and it replays on every state
    change — which, in an admin, means it replays every time the artist saves. It does not read as
    an animation at that point; it reads as <b>the screen flashing</b> whenever you touch anything.
    This was a real bug here. Press each Save a few times.</p>
    <div class="chor">
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>entrance bound to the render</div>
        <div class="re">
          <div class="re__panel" id="bad-panel">
            <span style="font-size:var(--adze-text-md);font-weight:var(--adze-weight-semibold)">Work details</span>
            <span class="mono">Study in Ochre · 2026</span>
            <div class="row">
              <button class="adze-btn adze-btn--primary adze-btn--sm" id="bad-save">Save</button>
              <span class="adze-tag adze-tag--success re__chip" id="bad-chip"><span class="adze-tag__dot"></span>Saved</span>
            </div>
          </div>
        </div>
      </div>
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>entrance bound to mount</div>
        <div class="re">
          <div class="re__panel" id="good-panel">
            <span style="font-size:var(--adze-text-md);font-weight:var(--adze-weight-semibold)">Work details</span>
            <span class="mono">Study in Ochre · 2026</span>
            <div class="row">
              <button class="adze-btn adze-btn--primary adze-btn--sm" id="good-save">Save</button>
              <span class="adze-tag adze-tag--success re__chip" id="good-chip"><span class="adze-tag__dot"></span>Saved</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-4)">Only the thing that changed should move.
    The panel did not arrive again; the save did.</p>
  </div>

  <div class="panel">
    <h3>Past --adze-dur-slower it is a progress state, not a transition</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">480ms is the ceiling. Anything longer
    is not a transition that needs tuning — it is a wait, and a wait needs a component that says so:
    a <code>Skeleton</code> when you know the shape of what is coming, a <code>ProgressBar</code>
    when you know how far along you are, a <code>Spinner</code> when you know neither. Stretching an
    animation to cover a slow request tells the person nothing except that the interface is fond of
    itself.</p>
    <div class="pbar"><i></i></div>
    <p class="note" style="margin-top:var(--adze-space-4)">Under
    <code>prefers-reduced-motion</code> the choreography still holds — the order things happen in,
    and which element is which, survive intact. Only the travel collapses. The autoplay loops on
    this card stay parked in that mode; the buttons still work.</p>
  </div>
</div>

<script>
var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

var se = document.getElementById('se'), xf = document.getElementById('xf');
function detail(on) {
  se.classList.toggle('is-open', on);
  xf.classList.toggle('is-open', on);
}
se.addEventListener('click', function () { detail(!se.classList.contains('is-open')); });
xf.addEventListener('click', function () { detail(!xf.classList.contains('is-open')); });

var toasts = document.querySelectorAll('.ee__toast');
function toast(on) {
  toasts.forEach(function (t) { t.classList.toggle('is-in', on); });
}

var stag = document.getElementById('stag');
var bCap = document.getElementById('b-cap'), bFree = document.getElementById('b-free');
var lastDelay = document.getElementById('lastdelay');
var capped = true;
function replay() {
  stag.classList.remove('is-run');
  void stag.offsetWidth;
  stag.classList.add('is-run');
}
function mode(cap) {
  capped = cap;
  stag.className = 'stag ' + (cap ? 'stag--capped' : 'stag--free');
  bCap.className = 'adze-btn adze-btn--sm ' + (cap ? 'adze-btn--primary' : 'adze-btn--secondary');
  bFree.className = 'adze-btn adze-btn--sm ' + (cap ? 'adze-btn--secondary' : 'adze-btn--primary');
  lastDelay.textContent = cap ? '280ms' : '1,085ms';
  replay();
}
bCap.addEventListener('click', function () { mode(true); });
bFree.addEventListener('click', function () { mode(false); });

function flash(id) {
  var c = document.getElementById(id);
  c.classList.remove('is-in');
  void c.offsetWidth;
  c.classList.add('is-in');
}
document.getElementById('bad-save').addEventListener('click', function () {
  var p = document.getElementById('bad-panel');
  p.classList.remove('is-entering');
  void p.offsetWidth;
  p.classList.add('is-entering');
  flash('bad-chip');
});
document.getElementById('good-save').addEventListener('click', function () { flash('good-chip'); });

function cycle() {
  detail(true);
  toast(true);
  replay();
  setTimeout(function () { detail(false); toast(false); }, 1900);
}
if (!RM) {
  setTimeout(cycle, 500);
  setInterval(cycle, 4200);
}
</script>
""")


# ── Bounded editors ────────────────────────────────────────────────────────
# The `.paste` values below are deliberately NOT tokens — foreign inline styles
# are the thing being demonstrated, and they arrive as content, not stylesheet.
# The card's own CSS is tokens throughout.
EDITOR = """
.verdict { display: inline-flex; align-items: center; gap: var(--adze-space-1); font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .06em; text-transform: uppercase; margin-bottom: var(--adze-space-2); }
.verdict--yes { color: var(--adze-success); }
.verdict--no { color: var(--adze-danger); }
.verdict i { font-size: 1.25em; }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--adze-space-6); }
.page { background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md); padding: var(--adze-space-6); }
.page__h { font-size: var(--adze-text-xl); font-weight: var(--adze-weight-semibold); letter-spacing: var(--adze-tracking-tight); margin-bottom: var(--adze-space-4); }
.page__lede { margin: 0 0 var(--adze-space-4); font-size: var(--adze-text-lg); line-height: var(--adze-leading-snug); letter-spacing: var(--adze-tracking-tight); color: var(--adze-text); }
.page__body { margin: 0; font-size: var(--adze-text-sm); line-height: var(--adze-leading-relaxed); color: var(--adze-text-muted); }
.slot { outline: 1px dashed var(--adze-accent-line); outline-offset: var(--adze-space-1); }
.tb { display: flex; flex-wrap: wrap; align-items: center; gap: var(--adze-space-1); padding: var(--adze-space-2); background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md) var(--adze-radius-md) 0 0; }
.tb__sep { width: 1px; align-self: stretch; background: var(--adze-border); margin: 0 var(--adze-space-1); }
.tb + .page { border-top: 0; border-radius: 0 0 var(--adze-radius-md) var(--adze-radius-md); }
.code { margin: 0; padding: var(--adze-space-3); background: var(--adze-bg-sunken); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); font-family: var(--adze-font-mono); font-size: var(--adze-text-xs); line-height: var(--adze-leading-relaxed); color: var(--adze-text-muted); overflow-x: auto; }
.code b { color: var(--adze-text); font-weight: var(--adze-weight-medium); }
.code s { color: var(--adze-danger); text-decoration: none; }
.gate { display: flex; align-items: flex-start; gap: var(--adze-space-3); padding: var(--adze-space-3) 0; border-bottom: 1px solid var(--adze-border); }
.gate:last-child { border-bottom: 0; }
.gate__n { flex: 0 0 auto; display: grid; place-items: center; width: 20px; height: 20px; border-radius: var(--adze-radius-pill); background: var(--adze-accent-soft); color: var(--adze-accent); font-family: var(--adze-font-mono); font-size: 10px; }
.gate__t { min-width: 0; }
.gate__t code { font-size: var(--adze-text-xs); }
"""

TOOLBAR_WIDE = [('text-h-one', 'Heading 1'), ('text-h-two', 'Heading 2'),
                ('text-aa', 'Font size'), ('palette', 'Colour'),
                ('paint-bucket', 'Highlight'), ('text-align-left', 'Align'),
                ('list-bullets', 'Bullets'), ('list-numbers', 'Numbers'),
                ('quotes', 'Blockquote'), ('code', 'Code'),
                ('image', 'Image'), ('table', 'Table')]

PASTED = ('<span style="font-family:Calibri,sans-serif;font-size:19pt;'
          'color:#1F497D">Painter working</span> between London and '
          '<span style="background:#FFFF00">Margate</span>.')

BOUNDED = ('<b>Painter working</b> between London and <i>Margate</i>. '
           'Recent work is at <a class="adze-link adze-link--inline" href="#">the Turner</a>.')

BODY_COPY = ('Recent work is concerned with tidal light and the way a flat '
             'horizon refuses to hold still for long enough to be painted.')


card('guidelines/editor-bounds.html', 'Components', 'Bounded editors',
     'An editor may only offer what the page already styles', 'Bounded editors',
     BTN + TAG + FORMS + EDITOR, """
<div class="stack">
  <div class="panel">
    <h3>An editor may only offer formatting the page already styles</h3>
    <p class="note">A rich-text editor embedded in a designed page is not a document editor that
    happens to be small. It is a hole cut in someone's layout, and everything it permits will
    eventually appear there. In this system the permitted set is <b>bold, italic, link</b> — because
    those are the three the page CSS styles — and nothing else.</p>
    <p class="note" style="margin-top:var(--adze-space-3)">An unbounded toolbar is how a design gets
    destroyed by the person it was built for. Not maliciously: the artist wants their exhibition
    title to stand out, finds a heading button, and uses it. The button was the promise that it
    would work.</p>
  </div>

  <div class="panel">
    <h3>What it prevents</h3>
    <p class="note" style="margin-bottom:var(--adze-space-6)">The same slot in the same designed
    page — a lede the type scale already sized, tracked and coloured. On the left, a paste from Word
    carrying its own font, size and colour, plus a heading and a list the page never anticipated.
    On the right, the same words through a bounded editor.</p>
    <div class="two">
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>unbounded — the design is gone</div>
        <div class="tb">
          <span class="adze-btn adze-btn--ghost adze-btn--sm"><i class="ph ph-text-b"></i></span>
          <span class="adze-btn adze-btn--ghost adze-btn--sm"><i class="ph ph-text-italic"></i></span>
          <span class="adze-btn adze-btn--ghost adze-btn--sm"><i class="ph ph-link"></i></span>
          <span class="tb__sep"></span>
""" + '\n'.join(
    '<span class="adze-btn adze-btn--ghost adze-btn--sm" title="%s"><i class="ph ph-%s"></i></span>'
    % (label, icon) for icon, label in TOOLBAR_WIDE) + """
        </div>
        <div class="page">
          <div class="page__h">About</div>
          <p class="page__lede slot">""" + PASTED + """</p>
          <h1 style="font-family:'Times New Roman',serif;font-size:2em;color:#C00000;margin:0 0 8px">Recent work</h1>
          <ul style="margin:0;padding-left:22px;font-family:Calibri,sans-serif;font-size:11pt">
            <li>tidal light</li>
            <li>a flat horizon</li>
          </ul>
        </div>
      </div>
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>bounded — bold, italic, link</div>
        <div class="tb">
          <span class="adze-btn adze-btn--ghost adze-btn--sm"><i class="ph ph-text-b"></i></span>
          <span class="adze-btn adze-btn--ghost adze-btn--sm"><i class="ph ph-text-italic"></i></span>
          <span class="adze-btn adze-btn--ghost adze-btn--sm"><i class="ph ph-link"></i></span>
        </div>
        <div class="page">
          <div class="page__h">About</div>
          <p class="page__lede slot">""" + BOUNDED + """</p>
          <p class="page__body">""" + BODY_COPY + """</p>
        </div>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-6)">Nothing on the left is a bug. Every one
    of those marks is a feature working exactly as offered.</p>
    <p class="note" style="margin-top:var(--adze-space-3)"><b>If you are reading this in a light
    theme, switch to dark and look at that panel again.</b> The pasted colours do not know the theme
    exists: the navy drops to almost unreadable against the dark surface and the highlight burns a
    hole in the page. Foreign formatting does not merely look wrong — it stops working outright on
    half the artist palettes, and the site it stops working on is the artist's own.</p>
  </div>

  <div class="panel">
    <h3>The toolbar is not the constraint</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">This is the part that gets built
    wrong. Shipping a three-button toolbar and calling it bounded leaves every other route wide
    open: <b>paste</b> carries its own markup and never touches the toolbar, and so do the keyboard
    shortcuts the library registers by default. The constraint has to live where the formats are
    defined, not where they are displayed.</p>
    <div class="gate">
      <span class="gate__n">1</span>
      <div class="gate__t">
        <div style="font-size:var(--adze-text-sm);font-weight:var(--adze-weight-medium)">The format registry</div>
        <span class="note">The editor is built from the permitted list, so header, list, blockquote,
        image, colour, size and align have nothing to land on <b>however they arrive</b> — button,
        shortcut or paste. It is also what keeps Enter to a plain paragraph: no other block format
        exists.</span>
      </div>
    </div>
    <div class="gate">
      <span class="gate__n">2</span>
      <div class="gate__t">
        <div style="font-size:var(--adze-text-sm);font-weight:var(--adze-weight-medium)">The paste sanitiser</div>
        <span class="note">Paste gets its own gate, because it bypasses everything else. It walks
        the pasted tree and <b>rebuilds</b> each run from the permitted attributes only, rather than
        trying to strip the bad ones — a whitelist you construct from cannot be incomplete the way a
        blacklist can. Embeds carry no copy and are dropped; link hrefs are checked against a scheme
        allowlist on the way through.</span>
      </div>
    </div>
    <div class="gate">
      <span class="gate__n">3</span>
      <div class="gate__t">
        <div style="font-size:var(--adze-text-sm);font-weight:var(--adze-weight-medium)">The server gate</div>
        <span class="note">The client-side restriction protects the <b>design</b>. It is not a
        control — a request can be made without it. The whitelist that runs on write is the control,
        and it permits the same four things and nothing else: <code>b</code>, <code>i</code>,
        <code>a</code>, <code>br</code>.</span>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-4)">Worked example:
    <code>_shared/shell/field-editors.js</code>, field type <code>copyrich</code>. Its
    <code>COPY_FORMATS</code> constant is stated once and consumed three ways — the format registry,
    the toolbar, and the paste matcher — so the three can never disagree about what is permitted.</p>
    <pre class="code" style="margin-top:var(--adze-space-3)">const <b>COPY_FORMATS</b> = ['bold', 'italic', 'link'];

new Quill(host, {
  <b>formats</b>: COPY_FORMATS,                        the registry — not a smaller toolbar
  modules: { toolbar: [['bold', 'italic', 'link']] },
});
q.clipboard.<b>addMatcher</b>(Node.ELEMENT_NODE, ...)   paste, rebuilt from COPY_FORMATS only</pre>
  </div>

  <div class="panel">
    <h3>The output is an inline fragment, not a block</h3>
    <p class="note" style="margin-bottom:var(--adze-space-4)">A copy slot is the <b>inner</b> content
    of an element the designer already wrote. Most editors think in blocks and hand back
    <code>&lt;p&gt;…&lt;/p&gt;</code>. Nested inside a slot that is itself a <code>&lt;p&gt;</code>,
    the parser closes the outer tag — and the class that carried the design goes with it.</p>
    <pre class="code">&lt;p class="lede" data-copy-rich="lede"&gt;
  &lt;p&gt;Painter working between London and Margate.&lt;/p&gt;   <s>editor emitted a block</s>
&lt;/p&gt;</pre>
    <div class="two" style="margin-top:var(--adze-space-6)">
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>inline fragment — class survives</div>
        <div class="page"><p class="page__lede">""" + BOUNDED + """</p></div>
      </div>
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>block wrapper — class stopped applying</div>
        <div class="page"><p>""" + BOUNDED + """</p></div>
      </div>
    </div>
    <p class="note" style="margin-top:var(--adze-space-4)">Then the second failure lands on top of
    the first: the server whitelist has no <code>p</code>, so the tags are stripped to nothing and
    two paragraphs run silently into one line. <code>&lt;br&gt;</code> is the only break permitted,
    so that is what a line break has to become. An editor that wraps its content in a block must
    have that wrapper unwrapped on the way out.</p>
  </div>

  <div class="panel">
    <h3>Widening the set is a decision about every page at once</h3>
    <p class="note">A request for one more format always arrives as a local convenience — one
    artist, one page, one heading. It is not local. The permitted set is a property of the whole
    system, and adding to it means every page's CSS now has to style that format, on every artist
    theme, forever. There is no per-field version of this decision.</p>
    <p class="note" style="margin-top:var(--adze-space-3)">The honest answer to "I need a heading
    here" is almost always that the <b>page</b> needs a heading slot — a field the design owns and
    styles — not that the copy editor needs a heading button.</p>
  </div>
</div>
""")


# ── Account & session ──────────────────────────────────────────────────────
ACCOUNT = """
.verdict { display: inline-flex; align-items: center; gap: var(--adze-space-1); font-family: var(--adze-font-mono); font-size: 10px; letter-spacing: .06em; text-transform: uppercase; margin-bottom: var(--adze-space-2); }
.verdict--yes { color: var(--adze-success); }
.verdict--no { color: var(--adze-danger); }
.verdict i { font-size: 1.25em; }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: var(--adze-space-6); }
.code { margin: 0; padding: var(--adze-space-3); background: var(--adze-bg-sunken); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); font-family: var(--adze-font-mono); font-size: var(--adze-text-xs); line-height: var(--adze-leading-relaxed); color: var(--adze-text-muted); overflow-x: auto; }

/* The account row, as it renders at the foot of the artist landing page. */
.acct { display: flex; flex-direction: column; gap: var(--adze-space-4); padding-top: var(--adze-space-6); border-top: 1px solid var(--adze-border); }
.acct__item { display: flex; flex-direction: column; align-items: flex-start; gap: var(--adze-space-3); }
.acct__form { display: flex; flex-direction: column; gap: var(--adze-space-3); align-self: stretch; }
.acct__hint { margin: 0; font-size: var(--adze-text-xs); color: var(--adze-text-faint); }
.acct__acts { display: flex; justify-content: flex-end; align-self: stretch; }
.acct__quiet { font-size: var(--adze-text-sm); color: var(--adze-text-faint); text-decoration: none; }

/* Password field: input plus a reveal toggle inside its own box. */
.pw { position: relative; display: block; }
.pw .adze-input { display: block; padding-right: var(--adze-space-10); }
.pw__eye { position: absolute; right: var(--adze-space-1); top: 50%; transform: translateY(-50%); display: grid; place-items: center; width: var(--adze-control-sm); height: var(--adze-control-sm); background: none; border: 0; padding: 0; color: var(--adze-text-faint); cursor: pointer; }

/* The re-auth overlay, shown over a page that keeps its content. */
.stagebox { position: relative; height: 280px; border: 1px solid var(--adze-border); border-radius: var(--adze-radius-md); overflow: hidden; background: var(--adze-bg); }
.stagebox__page { padding: var(--adze-space-4); display: flex; flex-direction: column; gap: var(--adze-space-3); }
.stagebox__row { height: 10px; border-radius: var(--adze-radius-pill); background: var(--adze-bg-sunken); }
.stagebox__words { padding: var(--adze-space-3); background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-sm); font-size: var(--adze-text-xs); color: var(--adze-text); }
.stagebox__over { position: absolute; inset: 0; display: grid; place-items: center; padding: var(--adze-space-4); background: color-mix(in srgb, var(--adze-bg) 82%, transparent); backdrop-filter: blur(2px); }
.stagebox__box { width: 100%; max-width: 240px; padding: var(--adze-space-5); background: var(--adze-surface); border: 1px solid var(--adze-border); border-radius: var(--adze-radius-lg); box-shadow: var(--adze-shadow-lg); text-align: center; display: flex; flex-direction: column; gap: var(--adze-space-3); }
.stagebox__t { font-size: var(--adze-text-md); font-weight: var(--adze-weight-semibold); }
.stagebox__b { font-size: var(--adze-text-xs); color: var(--adze-text-muted); }
.stagebox--wiped .stagebox__page { opacity: 0; }
.stagebox--wiped::after { content: 'root.innerHTML = ""'; position: absolute; inset: 0; display: grid; place-items: center; font-family: var(--adze-font-mono); font-size: var(--adze-text-xs); color: var(--adze-danger); }
"""

EYE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
       'stroke-linecap="round" stroke-linejoin="round" width="18" height="18">'
       '<path d="M2.5 12S6 5.8 12 5.8 21.5 12 21.5 12 18 18.2 12 18.2 2.5 12 2.5 12Z"/>'
       '<circle cx="12" cy="12" r="3.1"/></svg>')

WORDS = 'Recent work is concerned with tidal light and the way a flat…'


def pwfield(placeholder):
    return ('<label class="pw"><input class="adze-input" type="password" '
            'placeholder="%s" value="•••••••••">'
            '<span class="pw__eye">%s</span></label>' % (placeholder, EYE))


card('components/account/account.card.html', 'Components', 'Account & session',
     'Password change, account row, re-auth overlay', 'Account & session',
     BTN + TAG + FORMS + ACCOUNT, """
<div class="grid">

  <div class="panel stack">
    <h3>Change password</h3>
    <p class="note">One form, two mountings. At the foot of the artist landing page it is
    collapsed behind its own toggle — this is a once-a-year task and three empty boxes on a page
    whose job is to get someone into their editor is three boxes of noise. Inside a modal already
    titled <i>Change password</i> it opens flat, because a link saying "change your password" under
    that heading is the same sentence twice.</p>
    <div class="acct">
      <div class="acct__item">
        <a class="adze-link adze-link--standalone" href="#">Never mind</a>
        <div class="acct__form">
          """ + pwfield('Current password') + """
          """ + pwfield('New password') + """
          """ + pwfield('Repeat the new password') + """
          <p class="acct__hint">At least 6 characters. This signs you out on your other devices.</p>
          <div class="acct__acts"><button class="adze-btn adze-btn--secondary">Change password</button></div>
        </div>
      </div>
      <div class="acct__item"><a class="acct__quiet" href="#">Open the Adze control panel &rarr;</a></div>
    </div>
    <p class="note">The hint is not politeness. The endpoint rewrites the artist's API key and
    revokes every other session, so saying so costs one line and saves the support message.</p>
  </div>

  <div class="panel stack">
    <h3>Reveal, always</h3>
    <p class="note">Every password field in this system carries its toggle. A masked box gives you
    no way to tell a typo from a wrong password, or to notice a password manager quietly
    overwriting what you typed — and the artist who most needs to see the characters is the one
    already locked out.</p>
    <div class="stack" style="gap:var(--adze-space-3)">
      """ + pwfield('Password') + """
      <label class="pw"><input class="adze-input" type="text" value="tidal-light-2026">
        <span class="pw__eye" style="color:var(--adze-accent)">""" + EYE + """</span></label>
    </div>
    <p class="note">Revealed is a state worth seeing at a glance, so it takes the accent. The icon
    is inline SVG on <code>currentColor</code>: the artist admin has no external origins, and an
    icon font would be the only thing on the page reaching off-host.</p>
    <p class="note"><b>The wrapper carries the field's margin, never the input.</b> An
    <code>&lt;input&gt;</code> is inline-block, so it sits on its wrapper's text baseline and leaves
    ~12px of descender space beneath — and an adornment centred on the <i>wrapper</i> then lands
    half a margin low, resting on the floor of the field. <code>display: block</code> on the input
    kills the line box. Nudging the offset instead treats the symptom.</p>
  </div>

  <div class="panel stack">
    <h3>A session ending must not take the work with it</h3>
    <p class="note">Signing back in is a thing that happens <i>to</i> someone mid-sentence. It is
    never a reason to rebuild the page.</p>
    <div class="two">
      <div>
        <div class="verdict verdict--no"><i class="ph ph-x"></i>login screen</div>
        <div class="stagebox stagebox--wiped">
          <div class="stagebox__page">
            <div class="stagebox__row" style="width:40%"></div>
            <div class="stagebox__words">""" + WORDS + """</div>
            <div class="stagebox__row" style="width:70%"></div>
          </div>
        </div>
      </div>
      <div>
        <div class="verdict verdict--yes"><i class="ph ph-check"></i>overlay</div>
        <div class="stagebox">
          <div class="stagebox__page">
            <div class="stagebox__row" style="width:40%"></div>
            <div class="stagebox__words">""" + WORDS + """</div>
            <div class="stagebox__row" style="width:70%"></div>
          </div>
          <div class="stagebox__over">
            <div class="stagebox__box">
              <div class="stagebox__t">Signed out</div>
              <div class="stagebox__b">Sign in again to carry on — nothing you have typed has been lost.</div>
              """ + pwfield('Password') + """
              <button class="adze-btn adze-btn--primary">Sign back in</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <p class="note">The left-hand pattern is what a login screen does, and it is a data-loss path
    with a straight face: an autosaving editor's own status line reads <i>"your words are still
    here, and this keeps trying"</i> while the element holding those words is being removed from
    the document.</p>
    <p class="note"><b>Fixed, not absolute.</b> The session can end with the artist scrolled far
    down a long form; a box positioned inside the page opens at the top of the document, behind
    them. The overlay has to be where they are looking. It dims rather than hides what's underneath
    — seeing your own work still sitting there is the reassurance the message is making in words.</p>
    <p class="note">Don't retry the failed write from the overlay, and don't stack one per failed
    request. Several requests failing together is the normal case, and four password prompts is
    worse than the bug.</p>
  </div>

</div>
""")
