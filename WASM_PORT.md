# PCBView — WASM

**PCBView** is an [Emscripten](https://emscripten.org/) port of [OpenBoardView/OpenBoardView](https://github.com/OpenBoardView/OpenBoardView) compiled to WebAssembly/asm.js for the browser.

Live: **https://pannet1.github.io/PCBView/** — drag & drop any `.brd` file, 100% client-side.

Credits: Upstream viewer © OpenBoardView contributors (MIT), Web port via Emscripten (MIT), packaging by [pannet1/PCBView](https://github.com/pannet1/PCBView).

## Install

```toml
# pyproject.toml (either name works — pcbview-wasm is new, openboardview-wasm kept for compat)
pcbview-wasm = { git = "https://github.com/pannet1/PCBView", branch = "master" }
# or: openboardview-wasm = { git = "https://github.com/pannet1/PCBView" }
```

```bash
uv sync  # or pip install pcbview-wasm
```

## FastAPI — 2 lines

```python
from openboardview_wasm import make_static_files_app  # also: from pcbview import make_static_files_app
app.mount("/wasm", make_static_files_app(), name="wasm")
```

This serves `openboardview.js` + `index.html` at `/wasm/` with COOP/COEP headers (required for SharedArrayBuffer).

## SPA — canvas + script

```html
<canvas id="canvas"></canvas>
<script src="/wasm/openboardview.js"></script>
<script>
  const res = Module.loadBoardFromMemory(arrayBuffer)
  // 0 = success
</script>
```

Or load from URL: `https://yourdomain/wasm/?file=https://server/board.brd`

## JS API

### `Module.loadBoardFromMemory(arrayBuffer) → number`

| Return | Meaning |
|--------|---------|
| `0` | Board loaded |
| `1` | Parse failed |
| `-1` | Invalid input |

### `Module._loadBoardFromMemory(ptr, length) → number`

Low-level. Takes a WASM heap pointer + length.

## CLI

```bash
openboardview-wasm fetch        # download pre-built JS → ./wasm/
openboardview-wasm serve        # test server on :8080
openboardview-wasm build        # build from C++ (needs Emscripten)
```

## Build from source

```bash
git clone https://github.com/pannet1/PCBView
cd PCBView
./scripts/build-wasm.sh  # needs Emscripten 3.1.69 (via setup-emsdk or emsdk)
```

Output: `build_wasm/src/openboardview/openboardview.js`

## Deploy

```bash
# update your _static after rebuilding
cp build_wasm/src/openboardview/openboardview.js openboardview_wasm/_static/
```

Then commit and push. Users get the update on next `uv sync`.

## Files

| File | Description |
|------|-------------|
| `openboardview.js` | 5.6 MB asm.js (no .wasm) |
| `index.html` | Test page with `?file=` auto-load |

## Notes

- Fonts not available in browser — ImGui uses default (harmless warnings)
- SQLite annotations disabled in WASM — read-only viewer
- GitHub Pages is static — board files stay in your browser, never uploaded

## Credits

* **Upstream viewer:** [OpenBoardView/OpenBoardView](https://github.com/OpenBoardView/OpenBoardView) (MIT) — Paul Daniels, chloridite and contributors.
* **Web port:** [Emscripten](https://emscripten.org/) (MIT) — C++ SDL2/ImGui → WebAssembly.
* **This fork:** [pannet1/PCBView](https://github.com/pannet1/PCBView) (MIT) — packaging as `pcbview-wasm` + GitHub Pages. Fork detached from upstream to host the web build independently.
