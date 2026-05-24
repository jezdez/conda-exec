# Manage the cache

conda-exec caches environments for fast re-use. Over time, these caches can accumulate.

```{tip}
Run `conda exec --list` periodically to see how much disk space cached
environments are using. Each unique combination of tool, version spec, and
channels creates a separate cached environment.
```

## List cached environments

```bash
conda exec --list
```

Shows all cached environments with their size, last-used timestamp, and package count.

## Clean old caches

Remove environments not used in 30 days:

```bash
conda exec --clean
```

Preview what would be removed:

```bash
conda exec --clean --dry-run
```

Remove all caches:

```bash
conda exec --clean --all
```

Remove caches for a specific tool:

```bash
conda exec --clean ruff
```

## Force re-creation

```{note}
The `--refresh` flag only affects the specific tool and spec combination
you pass. Other cached environments are left untouched.
```

If a cached environment is stale or broken, force re-creation:

```bash
conda exec --refresh ruff check .
```
