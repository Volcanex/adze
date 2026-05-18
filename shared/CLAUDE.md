# shared/ — legacy stub, do not use

This directory (`shared/`, no underscore) is **legacy and unused**. All
live platform code lives in `_shared/` (with the underscore).

- `database.py` / `websocket_utils.py` and their `*_instructions.md` files
  describe a file-based NoSQL store and websocket helpers that an earlier
  iteration of Adze exposed to artist pages. Nothing in the current
  codebase imports them.
- Do not add new code here. New shared code goes in `_shared/`.
- Kept only so old artist pages that may still `import shared.*` don't
  break; safe to delete once confirmed no artist references it.
