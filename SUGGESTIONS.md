# OpenBoardView — Improvement Suggestions

> Branch: `feat/wasm-build` | Date: 2026-09-14 | Status: draft / revisit later

## 1. P0 — Fix WASM `null function` crash (`prompt.md`)

**Symptom:** `Module._loadBoardFromMemory(ptr,len)` → `RuntimeError: null function` / `invoke_vij` (indirect call table slot 0). `_wasmTest` and `_testData` work.

**Root cause:** Dead-code elimination removes the `SDL_LogError` / `SDL_LogMessageV` target used inside `ENSURE_OR_FAIL` (`utils.h`) → `BRD2File.cpp` → `BRDFileBase.h:READ_UINT/READ_STR`. Linker thinks `void(int,i64)` is never called indirectly.

**Proposed fix (minimal, 3 files):**

`src/openboardview/utils.h` — stub logging on Emscripten:
```cpp
#ifdef PLATFORM_EMSCRIPTEN
#undef ENSURE_OR_FAIL
#define ENSURE_OR_FAIL(X, ERROR_MSG, ACTION) \
  if (!(X)) { ERROR_MSG = "ENSURE " #X " failed at " __FILE__ ":" + std::to_string(__LINE__); ACTION; }
#endif
```

`src/openboardview/CMakeLists.txt` (EMSCRIPTEN block, ~line 185):
```cmake
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -fexceptions")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -O2 -fexceptions \
  -s USE_SDL=2 -s USE_SQLITE3=1 -s USE_ZLIB=1 \
  -s ALLOW_MEMORY_GROWTH=1 -s WASM=1 -s STACK_SIZE=5MB \
  -s MODULARIZE=1 -s EXPORT_NAME=OpenBoardView \
  -s EXPORTED_FUNCTIONS=_malloc,_free,_main,_loadBoardFromMemory,_wasmTest,_testData \
  -s EXPORTED_RUNTIME_METHODS=ccall,cwrap,HEAPU8,addOnPostRun \
  -s DISABLE_EXCEPTION_CATCHING=0 -s ERROR_ON_UNDEFINED_SYMBOLS=0 \
  -Wl,--no-gc-sections")
```

`src/openboardview/main_opengl.cpp` — guard SQLite/font/ImGui init with `#ifndef PLATFORM_EMSCRIPTEN` and verify with:
```bash
wasm-objdump -x build_wasm/src/openboardview/openboardview.wasm | grep -A2 table
emcc --show-ports  # confirm SDL2 port
```

> Currently `WASM=0` (5.6 MB asm.js) hides the bug but is 3× larger. Restore `WASM=1` + Brotli once table is stable.

**Verification:**
```js
var buf = new Uint8Array([0,0,0,0,0]);
var ptr = Module._malloc(buf.length);
Module.HEAPU8.set(buf, ptr);
console.log(Module._loadBoardFromMemory(ptr, buf.length)); // expect 1, not throw
Module._free(ptr);
```

---

## 2. WASM JS API ergonomics

- Replace `EM_ASM` inline `Module.loadBoardFromMemory` (`main_opengl.cpp:352`) with `cwrap`/`embind` + `MODULARIZE=1`. SPA usage becomes:
  ```js
  const OBV = await OpenBoardView();
  const code = OBV.loadBoardFromMemory(arrayBuffer); // 0=ok
  ```
- Export a Promise-based `onRuntimeInitialized` helper and typed result `{code, error}` instead of bare `0/1/-1`.
- Split `openboardview.js` (5.6 MB) into `openboardview.js` + `openboardview.wasm` (+ `.gz`/`.br`) and serve with `COOP/COEP` already in `_app.py`.
- Add drag-drop + error toast to `openboardview_wasm/_static/index.html` (currently silent on parse fail, full-viewport canvas only).

## 3. Python package (`openboardview_wasm/`)

- Add `py.typed`, `tests/test_app.py` for `make_static_files_app` header assertions (`Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy`).
- Add `ruff` + `mypy --strict` to `pyproject.toml` / `pre-commit`.
- Version the `_static/openboardview.js` artifact: store `VERSION` + `fetch --version <tag>` and check `MANIFEST.in` in CI.
- Consider `hatch` build backend (already `setuptools`); document `uv sync` + `openboardview-wasm serve --port`.

## 4. Build & CI

- `scripts/build-wasm.sh` uses `EM_CONFIG=/tmp/emscripten_config` (FROZEN_CACHE hack) — switch to `source emsdk_env.sh` and cache `~/.emscripten_cache` in GitHub Actions.
- Add `.github/workflows/wasm.yml`: `emcc 3.1.69 → cmake -DCMAKE_BUILD_TYPE=Release → make → node scripts/test-smoke.js && node scripts/test-with-file.js`.
- Unify `build.sh` / `build-wasm.sh` thread detection, add `ccache`/`sccache`.
- Cache `build_wasm/` keyed on `src/openboardview/CMakeLists.txt` + `src/**/*.cpp`.

## 5. C++ modernization (low-risk)

- Bump `CMAKE_CXX_STANDARD 11 → 17` (Emscripten 3.1+ supports it). Replace `calloc/free file_buf` in `BRD2File.cpp:18` with `std::vector<char>`.
- Harden `BRDFileBase.h` macros `READ_INT`/`READ_UINT`/`READ_STR` (currently `strtol` without bounds, `isspace` UB on signed char).
- Enforce existing `.clang-format` + `.editorconfig` via `pre-commit` hook; run `clang-tidy` on `FileFormats/*`.
- Remove global `std::unique_ptr<BoardView> g_app` mutable singleton — pass `BoardView&` into `loadBoardFromMemory` or make it `thread_local`.

## 6. Docs & DX

- Merge `WASM_PORT.md` (install/SPA/CLI) + `prompt.md` (bug log) → `docs/wasm.md` with single `fetch('/board.brd') → Module.loadBoardFromMemory` example (already in `AGENTS.md`).
- Document `?file=` auto-load, `Module._loadBoardFromMemory(ptr,len)` low-level API, and return codes in one place.
- Add `CONTRIBUTING.md` for `git clone --recursive` + `./scripts/build-wasm.sh --recompile`.

## 7. Testing

- Promote `scripts/test-smoke.js` / `test-with-file.js` / `test-node.mjs` to `npm test` + `pytest` parity; add a 5-byte and a real `BRD2` fixture.
- Add native `ctest` for `BRD2File::verifyFormat` (golden files in `asset/`).

## 8. Perf & bundle size

- Measure `wasm-opt -Oz` vs `-O2` on the 5.6 MB asm.js / future `.wasm`.
- Lazy-load `openboardview.js` (currently blocking `<script src>` in `index.html`); use `import()` + `await`.

---

### Suggested order when revisiting

1. §1 P0 fix → rebuild `WASM=1` and confirm `invoke_vij` gone.
2. §2 modularize + §4 CI (prevents regression).
3. §3 Python typing/tests + §6 docs.
4. §5 C++ cleanup + §7 fixtures.
