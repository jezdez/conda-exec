# Ecosystem fit

conda-exec is shaped around a common conda user experience problem: you
often need a tool once, or repeatedly but not permanently, and installing it
into `base` or a project environment is the wrong amount of commitment.

It gives conda a workflow similar to `npx`, `uvx`, or `pipx run`, while
keeping conda's solver, channels, package metadata, and platform model as
the source of truth.

## The workflow it optimizes

conda-exec is optimized for commands like these:

```bash
conda exec ruff check .
conda exec -c conda-forge -c bioconda samtools flagstat reads.bam
conda exec scripts/report.py --output report.json
```

The user intent is:

- get the command from trusted conda channels
- keep the current environment untouched
- avoid editing `environment.yml` for temporary tooling
- reuse the result when the same tool is run again
- remove the environment later without affecting anything else

That is different from managing an application environment, a production
service environment, or a shared research environment.

## Choosing the right conda workflow

| Tool | Best fit | Pros | Cons |
| ---- | -------- | ---- | ---- |
| [`conda run`](https://docs.conda.io/projects/conda/en/stable/commands/run.html) | Run a command inside an environment you already created with `conda create`, `conda env create`, or another project workflow. | Built into conda. Works with named and prefix environments. Good when the environment is meant to be inspected, activated, exported, updated, or shared as an environment. | The environment lifecycle is yours. `conda run` does not solve and install the requested command. Combining many unrelated commands in one environment can recreate the same compatibility pressure as a large shared environment. |
| `conda exec` | Run a command or script whose environment should be declared at the invocation or in the script metadata. | Creates isolated cached environments without touching `base` or the current project. Keys reuse by specs, channels, or lock content. Supports `--with`, channel selection, PEP 723 script metadata, and locked script handoffs. | First run pays the solve/install cost. Cached prefixes are not intended for manual editing or activation. Commands do not become available on `PATH`. |
| [`conda global`](https://conda-incubator.github.io/conda-global/) | Install command-line tools that should be available from any shell. | Gives each tool its own persistent environment. Exposes binaries on `PATH` through trampolines. Supports listing, updating, uninstalling, and syncing from a manifest. | It is a persistent tool manager, not a per-command dependency declaration. Less natural for one-off commands, script-local dependencies, and reproducible script locks. |

The important distinction is ownership. conda-exec owns disposable cached
prefixes. Project tools own project environments.
[conda run](https://docs.conda.io/projects/conda/en/stable/commands/run.html)
owns the "execute inside an existing environment" path.

If you are replacing an Anaconda Project-style catalog of commands, the
choice depends on who owns each environment:

- Use `conda exec` when each command should carry its own specs, channels,
  or script metadata. This is the closest fit for breaking one oversized
  R-plus-Python environment into smaller command-specific environments.
- Use `conda global` when the customer wants a stable set of everyday CLI
  tools available on `PATH`.
- Use `conda run` when the customer already has named environments and the
  catalog only needs to dispatch commands into them.

## Why caches are not project environments

A conda-exec cache entry is a performance optimization, not a user-managed
environment. It has a prefix, package records, and binaries, but it is not
meant to be activated, edited by hand, or treated as an environment spec.

This lets conda-exec be aggressive about reuse and cleanup:

- cache keys are derived from specs, channels, or lock content
- each spec combination gets an isolated prefix
- `--refresh` can remove and recreate one entry
- `--clean` can prune old entries without project coordination

If you need to inspect, modify, or share an environment as an environment,
create a named conda environment instead.

## Why `ce` exists

`conda exec` is the conda-native spelling. It reads clearly and fits the
plugin model.

`ce` exists for the moments where process startup and typing overhead
matter:

```bash
ce ruff check .
```

It calls the same parser and execution code but bypasses conda's plugin
subcommand loading. It is also the portable shebang target:

```python
#!/usr/bin/env ce
```

That mirrors a broader ecosystem pattern: keep the full command discoverable
and provide a short executable for frequent use.

## How channels shape the UX

conda users expect channels to be explicit and meaningful. conda-exec keeps
that model:

- default channels from conda configuration
- explicit channels via repeated `-c/--channel`
- script channels in `[tool.conda].channels`
- solver behavior delegated to conda's
  [context](https://docs.conda.io/projects/conda/en/stable/dev-guide/deep-dives/context.html)
  and
  [channel priority](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-channels.html#strict-channel-priority)

For domain channels such as `bioconda`, users should include the support
channels they rely on:

```bash
conda exec -c conda-forge -c bioconda samtools view input.bam
```

This is more verbose than a global package manager, but it matches conda's
core model: package identity includes channel context.

## How scripts fit

Python scripts are often shared as small files before they become packages.
PEP 723 gives those files a standard place to declare Python dependencies.
conda-exec extends that pattern with `[tool.conda]` so scripts can also
declare native conda packages and channels.

This makes the script itself the user interface:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["rich"]
#
# [tool.conda]
# channels = ["conda-forge", "bioconda"]
# dependencies = ["samtools>=1.19"]
# ///
```

For exploratory work, metadata is enough. For CI, papers, notebooks,
reports, or handoffs between machines, generated lock data records the
resolved environment while keeping the human-authored metadata readable.

## Where conda-exec should stay small

conda-exec deliberately does not try to become a project manager, a lockfile
standard, or a replacement for conda environments.

It delegates:

- solving to conda's configured solver backend
- package metadata to channels
- lock import and export to conda's environment plugins
- activation environment variables to conda's activator
- cleanup confirmation to conda's reporter system

That keeps the feature focused: ephemeral execution with conda semantics.
