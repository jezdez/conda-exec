# Architecture

## Overview

conda-exec is a conda plugin that enables ephemeral package execution. It creates cached, isolated environments and runs tools from them without modifying the user's PATH or global state.

## Flow

```
conda exec ruff check .
    |
    v
plugin.py              Register "exec" and "x" subcommands
    |
    v
cli/main.py            Parse args: tool name, extra args, --spec, --with, --channel
    |
    v
specs.py               Normalize specs, compute cache key hash
    |
    v
cache.py               Check if cached env exists (fast stat-only)
    |
    +--[cache hit]------> binaries.py: find binary in prefix
    |                       touch conda-meta/history for staleness tracking
    |
    +--[cache miss]-----> solver + transaction (via conda APIs)
    |                       write env to ~/.conda/exec/envs/<tool>--<hash>/
    |
    v
run.py                 subprocess.run(binary_path, *extra_args)
    |                     direct execution, no activation wrapper
    v
exit code              forwarded from subprocess
```

## Why not conda run?

`conda run` uses `wrap_subprocess_call()` which generates activation shell scripts, captures output by default, and adds overhead. Most CLI tools don't need full conda activation. Direct `subprocess.run` with PATH prepended is simpler, faster, and avoids output-capture pitfalls.

## Why not extend conda-global?

conda-global manages persistent, user-facing tool installations with PATH integration via trampolines. conda-exec manages ephemeral cached environments for one-shot execution. They are two distinct models that should not share state or environment prefixes.

## Why require conda-rattler-solver?

Ephemeral execution must be fast. The rattler solver (via resolvo) is significantly faster than classic libmamba for cold solves. Since conda-express (cx) already ships conda-rattler-solver as the default, and conda-exec is designed to ship as part of that distribution, this is a natural requirement.

## Part of the conda-express ecosystem

conda-exec is one of several plugins that ship with conda-express (cx), a single-binary conda distribution:

| Plugin | Purpose |
|--------|---------|
| conda-rattler-solver | Modern solver backend |
| conda-spawn | Subshell-based activation |
| conda-self | Self-update |
| conda-workspaces | Multi-environment workspaces |
| conda-global | Persistent global tools |
| conda-completion | Shell tab completion |
| conda-exec | Ephemeral package execution |
