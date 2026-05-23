# CLI reference

## conda exec / conda x

Run a command from a conda package without installing it permanently.

### Synopsis

```
conda exec [OPTIONS] TOOL [TOOL_ARGS...]
conda x [OPTIONS] TOOL [TOOL_ARGS...]
```

### Options

`-c, --channel CHANNEL`
: Additional channel to search (repeatable). Default: `conda-forge`.

`--spec MATCHSPEC`
: Full match spec for the tool package (e.g. `ruff>=0.4`). Overrides the implicit spec from TOOL.

`--with MATCHSPEC`
: Additional package to install in the ephemeral environment (repeatable). Values are full match specs. Example: `--with pytest --with "python=3.12"`.

`--refresh`
: Force re-creation of the cached environment.

### Arguments

`TOOL`
: Package name (and default binary name) to run.

`TOOL_ARGS`
: Arguments passed through to the tool. Use `--` to separate conda-exec options from tool options.

### Examples

```bash
# Basic usage
conda exec ruff check .
conda x ruff check .

# Version constraint
conda exec --spec "ruff>=0.4,<0.5" ruff check .

# Extra packages
conda exec --with pytest ruff check .

# Custom channel
conda exec -c bioconda samtools view file.bam

# Force re-creation
conda exec --refresh ruff check .

# Separate tool args with --
conda exec ruff -- --config pyproject.toml check .
```
