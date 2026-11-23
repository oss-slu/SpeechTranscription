# ADR-0001: Saltify 2.0 desktop runtime and Python processing boundary

| | |
|---|---|
| **Status** | Proposed. Needs maintainer approval before frontend work starts (#358, #351, #352) |
| **Issue** | [#365](https://github.com/oss-slu/SpeechTranscription/issues/365), parent [#348](https://github.com/oss-slu/SpeechTranscription/issues/348), roadmap [#357](https://github.com/oss-slu/SpeechTranscription/issues/357) |
| **Inputs** | [Current-state inventory](current-state-inventory.md), design-system foundation from [#361](https://github.com/oss-slu/SpeechTranscription/issues/361) / PR [#367](https://github.com/oss-slu/SpeechTranscription/pull/367) |
| **Unblocks** | #363 typed processing contract, #364 session schema, #361/#350 design system, #356 packaging |

## 1. Decision

**Build the Saltify 2.0 UI with Electron + React + TypeScript. Run all existing
processing in a separate Python sidecar process that the Electron main process
starts and supervises. They talk over newline-delimited JSON messages on the
sidecar's stdin/stdout.**

```text
┌──────────────────────── Electron app ────────────────────────┐
│  Renderer (React + TS, sandboxed, no Node)                   │
│    pages → SessionProvider (#366) → window.saltify API       │
│                                       ▲  contextBridge       │
│  Preload (typed, minimal) ────────────┘                      │
│  Main process: windows, menus, file dialogs, sidecar         │
│                supervisor, app-data paths                    │
└───────────────┬──────────────────────────────────────────────┘
                │ stdio, NDJSON, versioned envelope (#363)
┌───────────────▼──────────────────────────────────────────────┐
│  Python sidecar (PyInstaller --onedir)                       │
│    sidecar/  protocol, dispatcher, handlers  (new, thin)     │
│    job runner = components/processing.py pattern (retained)  │
│      └─ spawn worker per heavy job → Whisper / pyannote      │
│    retained: diarizationAndTranscription, grammar,           │
│      addConventions, salt_utils, export, audio (core),       │
│      java_runtime, ffmpeg_runtime, nltk_resources, selftest  │
│    bundled: JRE 17, ffmpeg/ffprobe, NLTK data, models        │
└──────────────────────────────────────────────────────────────┘
```

## 2. Context

Saltify 1.x is a CustomTkinter monolith. `GUI.py` and `components/audio_menu.py`
(1,630 lines together) mix the window, session state, audio I/O, job
orchestration, grammar review and export. The processing modules themselves have
no UI imports, apart from `audio.py`. Details are in the
[inventory](current-state-inventory.md).

2.0 needs a modern, themeable, accessible desktop UI on Windows and macOS. Its
dashboard and transcription workspace must be reviewable on fixture data before
persistence exists (#358). Everything must still run offline and locally, because
the recordings are of children (#354), and it must still package the processing
stack Saltify already depends on: Whisper/torch, pyannote, LanguageTool + JRE,
NLTK and ffmpeg.

## 3. Options considered

All three candidates render the UI with HTML/CSS. That is why PR #367 could write
the design tokens as stack-neutral JSON → CSS custom properties before this
decision. **None of the options below invalidates #367.**

### A. Electron + React/TypeScript + Python sidecar (selected)

- **Rendering:** a bundled Chromium, identical on Windows and macOS.
- **Python:** a separate process. The main process spawns it and supervises it.
- **Packaging:** electron-builder (NSIS/MSI on Windows, DMG on macOS). It has
  built-in code signing, notarization and auto-update. The sidecar ships as
  `extraResources`.
- **Contributor setup:** Node LTS + Python 3.11. TypeScript and React are the most
  common skill set in the contributor pool.

### B. Tauri + React/TypeScript + Python sidecar

- **Rendering:** the OS webview. That's WebView2 (Chromium) on Windows and WKWebView
  (Safari/WebKit) on macOS.
- **Python:** the same sidecar model (`externalBin`).
- **Packaging:** the Tauri bundler. The shell is small (a few MB).
- **Contributor setup:** a Rust toolchain on top of Node + Python, plus native build
  prerequisites (MSVC build tools on Windows, Xcode CLT on macOS).

### C. Python webview host (pywebview) + web UI

- **Rendering:** the OS webview, through pywebview. That's WebView2 via pythonnet on
  Windows and WKWebView via PyObjC on macOS.
- **Python:** the same process that hosts the window, with a JS↔Python bridge.
- **Packaging:** the existing PyInstaller pipeline, plus the webview backends.
- **Contributor setup:** Python + Node, for building the web UI. No Rust.

## 4. Evaluation

Scores run from 1 (poor) to 3 (good) against the criteria #365 names.

| Criterion | A. Electron | B. Tauri | C. pywebview |
|---|:-:|:-:|:-:|
| Windows/macOS consistency | **3** One engine on both | 2 Chromium vs WebKit. Fonts, focus rings, `<audio>`, `getUserMedia` and scrollbars differ | 2 Same split as Tauri, plus less mature bridges |
| Offline / local processing | 3 | 3 | 3 |
| Packaging and signing | **3** Mature signing, notarization and update. Sidecar is one more resource | 2 Good bundler, but sidecar signing and notarization need more manual work | 1 Stays on PyInstaller `--onefile`, adds pythonnet/PyObjC to it, no update story |
| Contributor setup | **3** Node + Python | 1 Rust toolchain and native prerequisites on student machines | 2 Python-first, but debugging spans two runtimes in one process |
| Migration risk | **3** New code in new directories. Legacy app untouched. Processing reused as is | 3 Same boundary as A | 2 Easiest to call Python directly from UI code, which recreates the coupling #348 is meant to remove |
| Installer size | 2 Chromium adds ~100 MB | **3** | 3 |
| Fit with #367 design system | **3** Contrast and fonts verified once, in one engine | 2 Must be reviewed in both engines | 2 Must be reviewed in both engines |

**Why A wins.** Saltify's payload is dominated by torch, Whisper, the JRE and NLTK
data, which already amount to hundreds of megabytes (inventory §3.1). Tauri's main
advantage, a small shell, therefore barely changes what users download. The costs
it adds are real: a Rust toolchain for every student contributor, and two rendering
engines to keep the accessibility rules from #361 true in. Electron gives one
engine to test against, the most mature signing/notarization path (Saltify ships
unsigned today), and a stack most contributors already know.

### Rejected alternatives

- **B. Tauri.** Rejected for contributor cost (Rust + native toolchains) and the
  WebKit/Chromium split. Its size win is small next to Saltify's Python payload.
  *Kept as the fallback:* the sidecar and contract (§5) are the same, so switching
  later replaces only the shell.
- **C. pywebview.** Rejected because hosting the UI in the processing process blurs
  the very boundary #348 asks for. It also keeps `--onefile` startup costs, and
  pythonnet/PyObjC add packaging risk to an already fragile PyInstaller build. It
  splits rendering engines the same way Tauri does.
- **Not evaluated: native Python toolkits (PySide6/Qt, a rebuilt CustomTkinter).**
  These are out of #365's scope. They would also discard #367's CSS token output.

## 5. Boundaries

### 5.1 Process boundary

| Process | Owns | Must not |
|---|---|---|
| **Renderer** | Pages, components, view state, audio playback (`<audio>`), recording (`MediaRecorder`), waveform drawing | Use Node, the filesystem or Python directly. Page components see only the `SessionProvider` interface (#366) |
| **Preload** | A typed `window.saltify` API forwarding to main | Contain logic |
| **Main** | Windows, menus, native file dialogs, app-data paths, sidecar lifecycle, forwarding requests and events | Run processing or hold transcript text longer than a request takes |
| **Sidecar** | Every request in the #363 contract: import/convert audio, transcription, diarization, grammar, SALT, SUGAR, exports, self-test | Touch UI state. Write to stdout outside the protocol |
| **Worker** (spawned by the sidecar) | One heavy job (Whisper, pyannote) | Outlive cancellation |

Recording and playback move into the renderer. The synchronized workspace (#352)
needs `currentTime` on the UI side anyway, and Chromium behaves the same on both
OSes. This removes PyAudio/portaudio from the shipped app. The renderer saves the
recording through main to a session-owned file, and the sidecar converts it to WAV
with the bundled ffmpeg.

### 5.2 Transport and envelope

This section is the input #363 builds the full contract on.

- **Transport:** the sidecar's stdin/stdout, one JSON object per line (UTF-8). Logs
  go to stderr, which main writes to a rotating log file with redaction (#354).
  There is no TCP/HTTP port, so nothing listens on the network. The child also dies
  with its parent's pipes.
- **Envelope fields:** `v` (protocol major version), `id` (request id),
  `type` = `request | event | result | error | cancel`, `method`, `payload`.
  - Progress is an `event` carrying `{stage, fraction}`. That's today's `("progress",
    stage, fraction)`.
  - `result`/`error` close a request. That's today's `done`/`error`. `error` carries a
    stable `code`, a user `message` (from `describeTranscriptionError`-style text)
    and `retryable`. `details` go only to the log.
  - `cancel` with the request `id` terminates that job's worker. That's today's
    `TranscriptionJob.cancel()`.
- **Handshake:** the first line from the sidecar is `ready`, with `{v, appVersion,
  capabilities}`. Main refuses a major-version mismatch and shows a "reinstall"
  error.
- **Schemas:** #363 defines the request/result schemas, its fixtures and its
  versioning rules. The ADR only fixes the envelope and transport.

### 5.3 Branch and directory boundary

```text
desktop/          Electron main, preload, renderer (React + TS, Vite). New.
sidecar/          Python package: __main__, protocol, dispatcher, handlers. New.
contracts/        Versioned message schemas + fixtures (owned by #363). New.
docs/saltify-2.0/ Design system (#367), architecture (this ADR).
*.py, components/ Legacy app + retained processing modules. Unchanged entry point.
```

- The legacy `GUI.py` keeps building, releasing and passing its tests until #356
  declares 2.0 the replacement.
- Retained modules are *imported* by `sidecar/`, not moved, so both apps share one
  copy. Any change to a retained module must keep the legacy tests green.
- New CI workflows are path-filtered to `desktop/`, `sidecar/` and `contracts/`, so
  2.0 work doesn't slow legacy builds, and the other way round.
- 2.0 work lands as ordinary PRs into `main`, inside these new directories. Per
  #358, UI pages are reviewed in their own PR before merging.

### 5.4 Packaging boundary

- **Sidecar build:** PyInstaller **`--onedir`**, not `--onefile`. This avoids
  re-extracting torch to a temp dir on every launch and leaving bundle copies in
  temp. Bundled with the sidecar: JRE 17, ffmpeg/ffprobe **on both OSes** (Windows
  currently has none), NLTK data, the `pattern` model and the Whisper `small.en`
  weights. Bundling the weights makes the first run offline. Bundling them versus
  downloading them on first run is a size/privacy trade-off for #354/#356.
- **App build:** electron-builder places the sidecar dir in `resources/sidecar/`.
  Main resolves the sidecar command as follows:
  - **Development:** `<venv>/python -m sidecar`
  - **Packaged:** `resources/sidecar/saltify-sidecar[.exe]`
- **Smoke test:** the existing `HEADLESS` self-test becomes `saltify-sidecar
  --selftest`, run by CI against the packaged app, as today.
- **Signing:** electron-builder signs the app. On macOS, every nested Mach-O in the
  sidecar (JRE, ffmpeg, torch dylibs) must be signed with the hardened runtime, and
  the app needs `NSMicrophoneUsageDescription` and the audio-input entitlement.

## 6. Retained modules and required adapters

| Module | Decision | Adapter work |
|---|---|---|
| `components/processing.py` | Retain as the job runner | Generalise beyond transcription: method name + args → worker. Keep spawn/terminate semantics |
| `diarizationAndTranscription.py` | Retain | Return structured segments (`startMs`, `endMs`, `text`, `speaker?`) instead of the formatted string. Lazy-import pyannote only for diarization |
| `grammar.py`, `addConventions.py`, `components/salt_utils.py` | Retain | Streaming handler: one `event` per correction, using `getProgress` and `shouldStop` |
| `export.py` | Retain Word export | Takes the transcript model, not editor text. Printing moves to the renderer |
| `audio.py` | Split | Extract normalize/convert/duration/peaks into a UI-free module. Record/playback go away in 2.0 |
| `java_runtime.py`, `ffmpeg_runtime.py`, `nltk_resources.py` | Retain | Called once at sidecar startup, before other imports. Replace `print` with logging |
| `selftest.py` | Retain | Exposed as `--selftest` |
| `GUI.py`, `audio_menu.py`, `user_menu.py`, `utils.py`, `constants.py`, `error_handler.py` popup, `CTkXYFrame`, matplotlib waveform | Replaced by `desktop/` | — |

**Before anything else is imported, the sidecar must redirect `sys.stdout` to
stderr and keep the real stdout only for protocol writes.** Several retained
modules `print()` to stdout (inventory §4), and any stray line would corrupt the
protocol.

## 7. Process lifecycle

| Phase | Development | Packaged |
|---|---|---|
| Start | `npm run dev` starts Vite and Electron. Main spawns `python -m sidecar` from the repo venv | Main spawns the bundled sidecar on app launch |
| Ready | Waits for the `ready` handshake. The UI shows a "Starting processing engine" state (#366 loading fixture) | Same. Timeout leads to an error state with "View log" / "Retry" |
| Heavy job | The sidecar spawns a worker per job. Whisper loads in the worker | Same |
| Cancel | `cancel` → terminate → kill after 2 s, as `TranscriptionJob` does today | Same |
| Crash | Main sees exit/EOF, fails in-flight requests with `code: ENGINE_EXITED`, and restarts with backoff (max 3) | Same |
| Quit | Main closes stdin. The sidecar cancels its jobs and exits. Main kills it after a timeout | Same. No orphan processes, no temp copies |
| Test | Contract tests run the sidecar with fixtures (#359). Renderer tests use the fixture provider | CI runs `--selftest` on both OS builds |

## 8. Risks

| Risk | Mitigation |
|---|---|
| Whisper/torch startup (seconds, high memory) on every job | Lazy imports. Optionally a warm, long-lived transcription worker later, as a measured optimisation (#355). Show staged progress from the start |
| pyannote needs an HF token and network | Keep diarization optional and off by default (#133). Treat it as an "external service" under #354 |
| LanguageTool/JRE packaging and signing on macOS | Reuse the #310 bundling. Sign the JRE's nested binaries. Keep the self-test check |
| Microphone permission on macOS and device differences | `NSMicrophoneUsageDescription` + entitlement. Recording-failure states in the UI. Manual test matrix in #355 |
| PyInstaller fragility (`setuptools<81` pin, hidden imports) | Same pins, `--onedir`, self-test gate. The sidecar build is a separate CI job, so failures are isolated |
| Two UIs to maintain during migration | Retained modules are shared, not forked. Legacy stays frozen apart from fixes. #356 sets the cut-over |
| Stray stdout from libraries corrupts the protocol | Redirect stdout at sidecar entry. Contract tests fail on any non-JSON line |
| Electron security | `contextIsolation`, `sandbox`, no `nodeIntegration`, strict CSP, no remote content, fonts bundled (as #367 requires) |

## 9. Consequences

- Contributors need Node LTS in addition to Python 3.11. MySQL can be dropped from
  `DEVELOPER_GUIDE.md`, because nothing uses it.
- `build_design_tokens.py` (#367) can add a TypeScript or CSS-module output for
  `desktop/` from the same JSON. The token values don't fork.
- #363 can now write schemas against the §5.2 envelope. #364 can assume main owns
  app-data paths and the sidecar owns derived files. #366 can assume page
  components only ever see a provider.
- The installer grows by roughly 100 MB for Chromium. PyAudio, `sv_ttk`,
  matplotlib (in the UI) and CustomTkinter leave the 2.0 bundle.

## 10. Open questions for reviewers

1. Bundle the Whisper weights, which makes the app offline from first launch, or
   download them on first run with consent? Needs a decision with #354.
2. Is Intel macOS still a target? Today's build is arm64-only.
3. Is a warm transcription worker in scope for the first release, or deferred to
   #355 performance work?
