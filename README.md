# PCBView — Browser PCB Viewer

[![Pages](https://github.com/pannet1/PCBView/actions/workflows/pages.yml/badge.svg)](https://pannet1.github.io/PCBView/) [![Build](https://github.com/pannet1/PCBView/actions/workflows/make_packages.yml/badge.svg)](https://github.com/pannet1/PCBView/actions/)

> **Live:** https://pannet1.github.io/PCBView/ — drag & drop any `.brd` (BRD2, BRD, BDV, BVR, etc.) — 100% client-side, no upload to server.

**PCBView** is a thin [Emscripten](https://emscripten.org/) port of [OpenBoardView](https://github.com/OpenBoardView/OpenBoardView) for the web. Board files are parsed in-browser via `Module.loadBoardFromMemory()` — nothing is uploaded.

No active feature development here — just the WASM conversion and GitHub Pages hosting. For the native desktop app, use [OpenBoardView/OpenBoardView](https://github.com/OpenBoardView/OpenBoardView).

## Try it

* **Website:** https://pannet1.github.io/PCBView/ — click **Load sample** (HP Pavilion) or drop your own `.brd`
* **Direct file:** https://pannet1.github.io/PCBView/?file=sample.brd or `?file=https://…/board.brd`

## Embed in your app

```toml
# uv / pip — either name works, pcbview-wasm is new
pcbview-wasm = { git = "https://github.com/pannet1/PCBView", branch = "master" }
```

```python
from pcbview import make_static_files_app  # or: from openboardview_wasm import ...
app.mount("/pcb", make_static_files_app(), name="pcb")
```

```html
<canvas id="canvas"></canvas>
<script src="/pcb/openboardview.js"></script>
<script>
  const res = Module.loadBoardFromMemory(arrayBuffer) // 0 = success
</script>
```

See [WASM_PORT.md](WASM_PORT.md) for JS API (`loadBoardFromMemory`, `_loadBoardFromMemory`), CLI, and build docs.

## Build from source

```bash
git clone https://github.com/pannet1/PCBView
cd PCBView
./scripts/build-wasm.sh  # needs Emscripten 3.1.69
# output: build_wasm/src/openboardview/openboardview.js -> openboardview_wasm/_static/
```

## Credits

* **Upstream viewer:** [OpenBoardView/OpenBoardView](https://github.com/OpenBoardView/OpenBoardView) (MIT) — Paul Daniels, chloridite and contributors. All board parsing, rendering and UI is theirs.
* **Web port:** [Emscripten](https://emscripten.org/) (MIT) — C++ SDL2/ImGui → WebAssembly.
* **This fork:** [pannet1/PCBView](https://github.com/pannet1/PCBView) (MIT) — packaging as `pcbview-wasm` + GitHub Pages. Fork detached from upstream to host the web build independently.

_Board files stay in your browser. No storage, no tracking._
