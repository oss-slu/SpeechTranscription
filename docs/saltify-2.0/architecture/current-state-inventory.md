# Saltify 1.x current-state inventory

Input to [ADR-0001](ADR-0001-desktop-runtime.md) and the start condition of
[#365](https://github.com/oss-slu/SpeechTranscription/issues/365) /
[#348](https://github.com/oss-slu/SpeechTranscription/issues/348). This is a
snapshot of `main` at `2a8807b9`, taken after #332 merged.

## 1. Modules

| Module | Lines | What it does | UI coupling | 2.0 fate |
|---|---:|---|---|---|
| `GUI.py` | 370 | Entry point. `freeze_support()`, `HEADLESS` self-test switch, ffmpeg/NLTK setup, `mainGUI(CTk)` window, in-memory session list, rename/delete, help overlay, waveform popup | Total | **Replace** |
| `components/audio_menu.py` | 1260 | One session's whole workspace: upload/record, playback, transcription job polling, speaker labelling, transcript colour coding, grammar review loop, conventions box, Word export | Total. It also orchestrates the processing | **Replace**. Move the orchestration logic into the sidecar |
| `components/user_menu.py`, `utils.py`, `constants.py` | 78 | Sidebar, theme switch, button helpers, font sizes, icons, `user_settings.txt` | Total | **Replace** |
| `components/error_handler.py` | 51 | `global_error_handler` decorator, CTk error popup with "file a bug" | Popup is CTk | **Replace** the popup. Keep the "retry / file bug" behaviour as UI states |
| `components/processing.py` | 122 | `TranscriptionJob`: spawn-context worker process, message queue of `progress` / `done` / `error` tuples, cancel = terminate → kill, `describeTranscriptionError` | None | **Retain**. It becomes the sidecar's job runner |
| `diarizationAndTranscription.py` | 194 | Whisper `small.en` load + cache, tqdm progress hook, `transcribe()` → formatted `"[m:ss] line"` string, `diarizeAndTranscribe()` via pyannote + `ACCESS_TOKEN` | None | **Retain behind an adapter** (see §4) |
| `audio.py` | 318 | `AudioManager`: PyAudio record/playback threads, pydub upload + normalize, waveform file, duration, seek | Takes a `customtkinter.CTk` root and calls back into `audio_menu` | **Split.** Keep normalize/convert/duration/waveform data. Move record and playback to the UI |
| `grammar.py` | 96 | NLTK resource setup (never downloads when frozen), `GrammarChecker` sentence iterator with `getProgress` and cancellable `getNextCorrection` | None | **Retain** |
| `addConventions.py` | 311 | LanguageTool correction, SALT inflectional morphemes, error-code removal, `pattern` conjugation | None | **Retain** |
| `components/salt_utils.py` | 11 | Formats a correction for the conventions box | None | **Retain** |
| `export.py` | 21 | `python-docx` Word export, default filename, `printTranscription` (OS print) | None | **Retain** Word export. Move printing to the UI |
| `java_runtime.py`, `ffmpeg_runtime.py`, `nltk_resources.py` | 132 | Locate the bundled JRE / ffmpeg / NLTK data under `get_base_path()` and fix PATH, `JAVA_HOME` and exec bits | None | **Retain** inside the sidecar |
| `selftest.py` | 121 | Packaged smoke test: bundled Java, ffmpeg, NLTK, app imports, report file | None | **Retain** as `sidecar --selftest` |
| `client_info.py` | 19 | Unused data holder | None | Drop |
| `CTkXYFrame` (submodule) | — | Scrollable CTk frame | Total | Drop with the legacy UI |

Tests (`tests/`, ~1,300 lines) cover processing, audio normalize/playback,
grammar/morphemes, SALT utils, the runtime locators and the self-test. All of them
except `test_gui.py` and `test_audio_playback.py` test modules the 2.0 sidecar keeps.

## 2. Processing behaviour worth preserving

- **Process isolation for cancellation.** Whisper can't be interrupted, so
  `TranscriptionJob` runs it in a `spawn` child and terminates it. The message tuples
  (`progress`/`done`/`error`) map almost one to one onto request/event/result messages.
- **User-facing error text.** `describeTranscriptionError` already turns exceptions
  into "what happened + what to do" messages. 2.0 should keep this text and add a
  stable error `code` beside it.
- **Grammar is incremental and cancellable** (`shouldStop` is checked between
  sentences, and `getProgress()` gives a fraction).
- **Frozen-app guards.** NLTK never downloads when `sys.frozen`. ffmpeg must be on
  PATH before `pydub` is imported. LanguageTool needs `JAVA_HOME` set before first use.

## 3. Packaging and CI

| Item | Windows (`windows-build.yml`) | macOS (`macos-build.yml`) |
|---|---|---|
| Runner / Python | `windows-latest`, 3.11.7 | `macos-latest` (arm64), 3.11.7 |
| Bundler | PyInstaller 6, `--onefile --windowed` | PyInstaller 6, `--onefile` |
| JRE | Temurin 17 zip → `jre/` | Temurin 17 aarch64 tarball → `jre/` |
| ffmpeg | **Not bundled.** The self-test skips it ("only bundled in the macOS build"), so users need ffmpeg installed | Pinned **arm64-only** static build, SHA-256 checked → `ffmpeg_bin/` |
| Data | `images`, `nltk_data`, `CTkXYFrame`, `pattern` `en-model.slp`, collected data for whisper / lightning / pyannote / language_tool / sv_ttk | Same, plus `--add-binary` ffmpeg |
| Smoke test | `HEADLESS=true` with Java stripped from PATH, report via `SALTIFY_SELFTEST_REPORT` | Same pattern |
| SBOM | anchore, scanning the Python env | Same |
| Signing | None | None. Ships as a bare executable plus the install guide |
| Release | `release.yml` on push to `main`: zips both artifacts and the SBOMs | |

Constraints that carry over to any 2.0 runtime:

1. **Payload is dominated by Python.** torch, Whisper, pyannote, the JRE and NLTK data
   are already hundreds of megabytes. Installer size doesn't separate the candidates.
2. **`--onefile` re-extracts to a temp `_MEI*` dir on every launch.** That slows a
   torch import and leaves copies of the bundle in temp. A sidecar should use `--onedir`.
3. **The Whisper model is not bundled.** `whisper.load_model("small.en")` downloads to
   `~/.cache/whisper` on first transcription, so the first run needs the network. This
   affects the offline promise and #354.
4. **Diarization needs a Hugging Face token** (`ACCESS_TOKEN` in `.env`) and a
   download. It's implemented but not wired into the UI (#133).
5. **macOS is arm64-only** because of the pinned ffmpeg build, and **Windows doesn't
   bundle ffmpeg at all**. 2.0 should bundle it on both.
6. **Nothing is signed or notarized.** Any runtime that adds signing must sign every
   nested Mach-O (JRE, ffmpeg, torch dylibs).

## 4. Debt the adapter layer must absorb

- `transcribe()` returns a pre-formatted string with start times only (`m:ss`). The
  synchronized workspace (#352) needs segment start/end times in ms, text and an
  optional speaker. The adapter should return Whisper's segments, not the string.
- `diarizationAndTranscription` imports `pyannote.audio` at module import, even for
  plain transcription. That adds startup cost to every worker.
- The runtime modules `print()` to **stdout** (`java_runtime` 8 calls,
  `diarizationAndTranscription` 7, `audio` 2, `ffmpeg_runtime` 2). A stdio-based
  protocol must take stdout away from them (redirect to stderr / logging) before any
  of them are imported.
- `audio.py` imports `customtkinter` and calls into `audio_menu`. The kept parts
  (normalize, duration, waveform data) need to be extracted from that class.
- Sessions live only in memory (`mainGUI.audioMenuList`), and settings are a bare
  `user_settings.txt` in the working directory. There is nothing durable to migrate
  except user-saved audio/Word files (#349, #356).
- Unused dependencies: `mysql-connector-python` (installed by CI and required by
  `DEVELOPER_GUIDE.md`), `sv_ttk`, `simple_diarizer`, `spectralcluster`, `Resemblyzer`.
  No module imports them.
