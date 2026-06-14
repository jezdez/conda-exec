# Changelog

## 0.3.0 (2026-06-14)

This release intentionally jumps to `0.3.0` so the modern conda-exec package can
supersede the historical `conda-forge::conda-exec` `0.2.1` package line.

### Highlights

- Added script lockfile support for reproducible PEP 723 script execution.
- Added automatic cache cleanup with configurable age and frequency controls.
- Hardened cache keys, solver error handling, metadata validation, temporary
  prefix cleanup, and Windows binary discovery.
- Added completion metadata for conda-completion `0.3.0`, including the `ce`
  alias, context-aware `TOOL` completion, cached tool discovery, `--with`
  package specs, `--channel` channels, `--clean` cached tools, and `--lock`
  script paths.
- Expanded documentation across how-to, reference, explanation, tutorial, and
  demo sections.

### Script lockfiles

- Added `--lock` to generate or reuse script lock data for metadata-backed
  script runs.
- Added `--embed` to write generated lock data into the script itself.
- Added sidecar lock discovery and digest checks so out-of-date lock data is
  ignored when script dependency metadata changes.
- Added `--ignore-lock` and `--refresh` paths for bypassing or regenerating lock
  data.
- Reused conda's environment exporter/specifier plugin APIs instead of
  hardcoding a lockfile format.

### Cache management

- Added automatic cleanup for old cached environments.
- Added config support through conda plugin settings and direct
  `CONDA_EXEC_*` environment variable aliases.
- Moved cleanup selection and removal behavior into the cache layer.
- Stored the cleanup invocation counter under conda-exec's data directory with
  atomic writes.

### Hardening

- Included script metadata, CLI `--with`, CLI `--channel`, automatic Python
  specs, PyPI dependencies, and lock content in cache reuse decisions.
- Treated `requires-python`-only scripts as metadata-backed executions that
  create and validate a Python environment.
- Converted invalid specs, package-not-found errors, and solver failures into
  concise `conda exec:` messages.
- Cleaned up temporary prefixes on creation failures.
- Validated PEP 723 metadata field types before solving.
- Preferred Windows `.exe` launchers over `.bat` and `.cmd` shims while keeping
  `.bat` and `.cmd` supported.
- Added `ty` type checking to CI.

### Completion integration

- Exposed parser completion metadata for `--channel`, `--with`, and the
  context-sensitive `TOOL` positional.
- Registered `ce` as an executable alias for the `conda exec` command tree.
- Declared the cached-tool runtime source from `CONDA_EXEC_HOME/envs`, falling
  back to `~/.conda/exec/envs`.
- conda-completion `>=0.3.0` is recommended for the new completion metadata.
  conda-exec still runs without conda-completion installed.

### Documentation

- Added Diataxis coverage for dependency resolution, cache cleanup, script
  locks, package specs, PyPI dependencies, CI usage, security, ecosystem fit,
  and list JSON output.
- Added demo recordings for quickstart, cache management, extra packages, PyPI
  scripts, script dependencies, and script locks.
- Corrected activation documentation and Windows launcher caveats.
- Updated repository and documentation URLs after the conda-incubator transfer.

## 0.1.1 (2026-05-24)

Initial release of conda-exec: ephemeral package execution for conda.

### Highlights

conda-exec lets you run any conda package without installing it permanently.
It creates a cached, isolated environment, runs the tool, and exits. Cached
environments are reused automatically on subsequent runs. Think `npx` for
Node or `uvx` for Python/uv, but for conda packages.

```bash
conda exec ruff check .
ce ruff check .
```

### Features

#### Ephemeral package execution

- Run any conda package by name: `conda exec ruff check .`
- Version constraints via match specs: `conda exec "ruff>=0.4,<0.5" check .`
- Extra packages with `--with`: `conda exec --with pytest ruff check .`
- Custom channels with `-c`: `conda exec -c bioconda samtools view file.bam`
- Force re-creation with `--refresh`: `conda exec --refresh ruff check .`
- Full conda activation with `--activate` for tools that need `CONDA_PREFIX`

#### Standalone `ce` command

- `ce` is a standalone console script alias for `conda exec`
- Works without conda's plugin system, useful for shell scripts and CI
- Identical CLI interface: `ce ruff check .`

#### PEP 723 inline script execution

- Run Python scripts with inline dependency metadata: `conda exec script.py`
- Parses standard PEP 723 `# /// script` metadata blocks
- Supports `requires-python` constraints with validation
- Supports `[tool.conda]` extension for conda-native dependencies and channels
- PyPI dependencies via conda-pypi integration (optional)
- Scripts without metadata run with the current Python (no environment created)
- Shebang support: `#!/usr/bin/env conda-exec` for directly executable scripts

#### Cache management

- `conda exec --list` shows all cached environments with size, age, and
  package count
- `conda exec --list --json` for machine-readable JSON output
- `conda exec --clean` removes environments unused for 30+ days
- `conda exec --clean --all --yes` removes everything without prompting
- `conda exec --clean --older-than 7 ruff` targets specific tools and ages
- `conda exec --clean --dry-run` previews what would be removed
- Last-used tracking via conda-meta/history mtime

#### Security

- Cache keys use SHA-256 hashing of normalized, sorted specs and channels
- Tool names and cache keys validated against strict regex patterns
- Path traversal protection via `is_relative_to()` checks
- Symlink containment: binaries must resolve within the prefix
- Script file size capped at 10 MB to prevent memory exhaustion
- Atomic environment creation via temp directory + rename
- All subprocess calls use list arguments (no shell=True)

#### Cross-platform support

- Linux (x86_64, aarch64), macOS (x86_64, arm64), Windows (x86_64)
- Platform-correct binary discovery using conda's `BIN_DIRECTORY`
- Windows-specific executable extensions (.exe, .bat, .cmd)
- Windows path fallback via `platformdirs` when `~/.conda` is unavailable

### Infrastructure

- CI testing on Linux, macOS, and Windows across Python 3.10 through 3.14
- Performance benchmarks tracked via bencher.dev with regression detection
- GitHub Actions workflows hardened per zizmor audit (SHA-pinned actions,
  `persist-credentials: false`, minimal permissions)
- Dependabot configured for GitHub Actions, pip, and conda ecosystems
- Documentation built with Sphinx, conda-sphinx-theme, and myst-parser,
  following the Diataxis framework
- Release automation via GitHub Actions with PyPI trusted publishing

### Dependencies

- Requires conda >= 25.1
- Optional: conda-pypi for PyPI dependency support in scripts
- Optional: conda-lockfiles for script lock support
- Runtime: packaging >= 22.0, tomli >= 1.0 (Python < 3.11)

### Test suite

- 194 tests (168 unit, 26 integration/benchmark)
- No mocking libraries: pure pytest fixtures with real fakes
- pytest-subprocess for subprocess call assertions
- time-machine for deterministic time-dependent tests
- pytest-benchmark for performance regression tracking
