Rebuild the auto-generated docs index in root `CLAUDE.md`.

```
python3 scripts/compile_docs.py
```

Run after adding, removing, or renaming any `CLAUDE.md` file anywhere in
the tree. The script walks the repo, pulls the first `# heading` from
each subdirectory's `CLAUDE.md`, and splices a table into the root
`CLAUDE.md` between the `<!-- DOCS:START -->` / `<!-- DOCS:END -->`
markers.

Do not hand-edit the content between those markers — it's regenerated
every run.
