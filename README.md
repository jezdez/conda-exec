# conda-exec

[![Tests](https://github.com/conda-incubator/conda-exec/actions/workflows/tests.yml/badge.svg)](https://github.com/conda-incubator/conda-exec/actions/workflows/tests.yml)
[![Documentation](https://github.com/conda-incubator/conda-exec/actions/workflows/docs.yml/badge.svg)](https://conda-incubator.github.io/conda-exec/)
[![License: BSD-3-Clause](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](https://github.com/conda-incubator/conda-exec/blob/main/LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Benchmarks](https://img.shields.io/badge/benchmarks-bencher.dev-blue)](https://bencher.dev/perf/conda-exec)
[![zizmor](https://img.shields.io/badge/%F0%9F%8C%88-zizmor-white?labelColor=white)](https://github.com/conda-incubator/conda-exec/actions/workflows/zizmor.yml)

Ephemeral package execution for conda. Run commands from conda packages
without installing them permanently.

```bash
conda exec ruff check .
ce ruff check .
```

conda-exec creates a cached, isolated environment for the tool, runs it,
and exits. The environment is reused on later runs but is not added to
`PATH` permanently.

![conda-exec quickstart demo](demos/quickstart.gif)

## conda run, conda exec, or conda global?

| Tool | Use it when | Pros | Tradeoffs |
| ---- | ----------- | ---- | --------- |
| [`conda run`](https://docs.conda.io/projects/conda/en/stable/commands/run.html) | You already have a named or prefix environment and want to run a command inside it. | Built into conda. Works with user-managed project environments. Best fit when an environment is meant to be inspected, activated, exported, or maintained. | You must create and maintain the environment yourself. It does not install the requested command for you. One environment can still become a compatibility bottleneck. |
| `conda exec` | You want the command or script invocation to declare the environment it needs. | Keeps `base` and project environments untouched. Caches isolated environments by spec. Supports extra packages, channels, PEP 723 script metadata, and script locks. | First run solves and installs. Cached environments are an implementation detail, not environments to edit by hand. Commands are not exposed on `PATH`. |
| [`conda global`](https://conda-incubator.github.io/conda-global/) | You want a CLI tool permanently available from your shell. | Installs each tool into an isolated persistent environment. Exposes commands on `PATH` through trampolines. Records tools in a manifest for update and sync. | It is a tool-install lifecycle, not a per-invocation dependency declaration. Less direct for one-off commands, inline script dependencies, or locked script handoffs. |

For Anaconda Project-style command catalogs, use `conda exec` when each
command should carry its own dependency specs, use `conda global` when a
tool should feel installed everywhere, and use `conda run` when the
customer already owns named environments.

## Installation

```bash
conda install -c conda-forge conda-exec
```

Install `conda-pypi` for scripts with PyPI dependencies, and
`conda-lockfiles` for script lock support.

## Usage

```bash
# Run a tool (creates cached environment on first use)
conda exec ruff check .
ce ruff check .               # standalone alias

# Pin a version
conda exec "ruff>=0.4,<0.5" check .

# Add extra packages
conda exec --with pytest ruff check .
conda exec --with "python=3.12" jupyter lab

# Use a specific channel
conda exec -c bioconda samtools view file.bam

# Run a script with inline dependencies (PEP 723)
conda exec script.py

# Record a repeatable script environment
conda exec --lock script.py

# Force re-creation of cached environment
conda exec --refresh ruff check .
```

## How it works

1. Computes a cache key from the tool name, specs, and channels
2. Checks `~/.conda/exec/envs/` for a cached environment
3. On cache miss: solves and installs via conda's configured solver backend
4. Finds the binary in the environment's `bin/` directory
5. Runs it directly via `subprocess.run` with PATH prepended
6. Forwards the tool's exit code

## Documentation

Full documentation at [conda-incubator.github.io/conda-exec](https://conda-incubator.github.io/conda-exec/).

## Contributing

```bash
pixi install
pixi run check          # lint + format + typecheck
pixi run -e test test   # run tests
```

## License

BSD-3-Clause
