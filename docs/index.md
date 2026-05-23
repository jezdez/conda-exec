# conda-exec

Ephemeral package execution for conda. Run any conda package without installing it permanently.

```bash
conda exec ruff check .
conda x ruff check .
```

conda-exec creates a cached, isolated environment for the tool, runs it, and exits. The environment is cached for fast re-use but is not on PATH and is fully disposable.

```{toctree}
:maxdepth: 2
:caption: Getting started

quickstart
```

```{toctree}
:maxdepth: 2
:caption: Tutorials

tutorials/index
```

```{toctree}
:maxdepth: 2
:caption: How-to guides

how-to/index
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/index
```

```{toctree}
:maxdepth: 2
:caption: Explanation

explanation/index
```
