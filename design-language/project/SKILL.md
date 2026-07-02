---
name: lastplace-design
description: Use this skill to generate well-branded interfaces and assets for Last Place, the UK web design studio, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `readme.md` file within this skill, and explore the other available files.

Last Place is a small UK web design studio. The brand is web-native and quiet:
a single confident **hyperlink blue** (`#0000EE`), black ink, lots of white
space, set in **Cormorant**, with **forest green** as a rare second voice and a
**blue lino-print plant** as the recurring mark.

Key files:
- `styles.css` — the single CSS entry point (link this; it `@import`s everything).
- `tokens/` — colour, typography, spacing, fonts, base element styles.
- `cards/` — foundation specimen cards (colours, type, spacing, brand).
- `components/` — React primitives (`core/`: Button, TextLink, Tag, Card; `forms/`: Field, Checkbox, Switch).
- `ui_kits/studio-site/` — a full interactive recreation of the studio website.
- `assets/` — the plant mark (`plant-mark-blue.png`, `plant-mark-blue-knockout.png`).

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy
assets out and create static HTML files for the user to view — link `styles.css`
for the tokens, set headings in Cormorant, use the hyperlink blue for links and
the one primary action, and keep a lot of space on the page. If working on
production code, copy assets and read the rules here to become an expert in
designing with this brand.

If the user invokes this skill without any other guidance, ask them what they
want to build or design, ask some questions, and act as an expert designer who
outputs HTML artifacts _or_ production code, depending on the need.
