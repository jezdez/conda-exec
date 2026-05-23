# Architecture

## Overview

conda-exec is a conda plugin that enables ephemeral package execution. It creates cached, isolated environments and runs tools from them without modifying the user's PATH or global state.

## Flow

```{mermaid}
flowchart TD
    A["conda exec ruff check ."] --> B["plugin.py\nRegister exec and x subcommands"]
    B --> C["cli/main.py\nParse args: tool, --spec, --with, --channel"]
    C --> D["specs.py\nNormalize specs, compute cache key hash"]
    D --> E{"cache.py\nCached env exists?"}
    E -- "cache hit" --> F["binaries.py\nFind binary in prefix\nTouch conda-meta/history"]
    E -- "cache miss" --> G["Solver + transaction via conda APIs\nWrite env to ~/.conda/exec/envs/tool--hash/"]
    G --> F
    F --> H["run.py\nsubprocess.run with PATH prepend"]
    H --> I["Exit code forwarded from subprocess"]
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
