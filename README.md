<div align="center">

# 🔎 PCBView

**A blazing-fast, 100% client-side Web PCB Viewer.**<br>
Drag & drop your board files instantly (.brd, .bdv, .asc, .cad, etc.). No server uploads. No tracking.

[![Pages](https://github.com/pannet1/PCBView/actions/workflows/pages.yml/badge.svg)](https://pannet1.github.io/PCBView/)
[![Build](https://github.com/pannet1/PCBView/actions/workflows/make_packages.yml/badge.svg)](https://github.com/pannet1/PCBView/actions/)

[**✨ Try it Live! ✨**](https://pannet1.github.io/PCBView/)

</div>

---

**PCBView** is a lightweight [Emscripten](https://emscripten.org/) WebAssembly port of the excellent [OpenBoardView](https://github.com/OpenBoardView/OpenBoardView). It brings the power of native desktop PCB visualization directly to the web.

> ⚠️ **Note:** This repository is focused strictly on the WASM conversion, packaging, and GitHub Pages hosting. For the native desktop application and feature requests, please visit the upstream repository: [OpenBoardView/OpenBoardView](https://github.com/OpenBoardView/OpenBoardView).

## 🚀 Features

- **100% Client-Side:** Your files stay on your machine. Everything runs securely inside your browser using WebAssembly.
- **Drag & Drop:** Instantly load board files (BRD2, BRD, BDV, BVR, BVR3, ASC, CAD, CST, etc.) by dropping them onto the page.
- **High Performance:** Powered by C++, SDL2, and ImGui, compiled to high-speed WASM.
- **Embeddable:** Easily integrate the viewer into your own Python/FastAPI backend or static HTML site.

## 🎮 Try it Out

* **Web Viewer:** [https://pannet1.github.io/PCBView/](https://pannet1.github.io/PCBView/)
* **Direct File Load:** You can auto-load a file using URL parameters: `https://pannet1.github.io/PCBView/?file=sample.brd` or `?file=https://your-domain.com/board.brd`

## 📦 Embed in Your App

You can easily embed PCBView into your Python backend or frontend applications.

### Python / FastAPI
```toml
# In your pyproject.toml
pcbview-wasm = { git = "https://github.com/pannet1/PCBView", branch = "master" }
```

```python
from fastapi import FastAPI
from pcbview import make_static_files_app

app = FastAPI()
app.mount("/pcb", make_static_files_app(), name="pcb")
```

### Static HTML
```html
<canvas id="canvas"></canvas>
<script src="/pcb/openboardview.js"></script>
<script>
  // Pass an ArrayBuffer to load a board natively
  const res = Module.loadBoardFromMemory(arrayBuffer); // Returns 0 on success
</script>
```

📚 See the [WASM_PORT.md](WASM_PORT.md) for full JS API documentation, CLI tooling, and build instructions.

## 🛠️ Build from Source

To compile the C++ source to WebAssembly yourself:

```bash
git clone https://github.com/pannet1/PCBView
cd PCBView
./scripts/build-wasm.sh  # Requires Emscripten 3.1.69
# The built artifacts will be located at:
# build_wasm/src/openboardview/openboardview.js -> openboardview_wasm/_static/
```

## 💖 Credits & Acknowledgements

* **Upstream Viewer:** [OpenBoardView/OpenBoardView](https://github.com/OpenBoardView/OpenBoardView) (MIT) — Huge thanks to Paul Daniels, chloridite, and all contributors. All board parsing, rendering logic, and core UI belong to them.
* **Web Port Technology:** [Emscripten](https://emscripten.org/) (MIT) — Enabling C++ SDL2/ImGui to run in WebAssembly.
* **This Fork:** [pannet1/PCBView](https://github.com/pannet1/PCBView) (MIT) — Maintained by pannet1 for packaging as `pcbview-wasm` and GitHub Pages deployment.

---
<div align="center">
  <i>Files never leave your device. No storage, no tracking.</i>
</div>
