# Migrate from classic conda-exec

The `conda-forge::conda-exec` package name existed before this project. Version
`0.2.1` was a 2020 package for executing commands inside a conda environment.
Version `0.3.0` and later provide the modern conda-exec tool described in this
documentation.

Treat the upgrade as a package replacement, not as a compatible command-line
upgrade.

## Check what is installed

Check the environment where `conda` itself is installed. This is usually
`base`:

```bash
conda list -n base conda-exec
```

If you installed the old package into another environment, check that
environment instead:

```bash
conda list -n my-env conda-exec
```

## Install the modern package

Install `conda-exec >=0.3.0` into the environment that provides your `conda`
command:

```bash
conda install -n base -c conda-forge "conda-exec>=0.3.0"
```

The version constraint matters. Without it, an environment with old pins or old
repodata can keep selecting the historical `0.2.1` package.

## Update completion support

Shell completion is optional, but the new completion metadata needs
`conda-completion >=0.3.0`:

```bash
conda install -n base -c conda-forge "conda-completion>=0.3.0"
```

After updating completion support, reinstall or refresh your shell hooks using
the conda-completion documentation for your shell.

## Verify the new command

Check that the conda plugin and standalone alias are available:

```bash
conda exec --help
ce --help
```

Then run a small tool:

```bash
conda exec ruff --version
```

The first run creates a cached environment. Later runs reuse it.

## Adjust old usage

The historical conda-forge package and the modern conda-exec package do not
share a command-line contract. Replace old invocations with one of the modern
forms:

```bash
conda exec ruff check .
conda exec --with pytest ruff check .
conda exec -c bioconda samtools view file.bam
conda exec script.py
```

Use `conda run -n ENV COMMAND ...` when you want to run a command inside an
existing named environment. Use `conda exec COMMAND ...` when you want
conda-exec to create or reuse an ephemeral cached environment for the requested
package.

## What happened to the old conda-exec command?

The historical conda-forge package installed a `conda-exec` shell command.
That command activated an existing environment and then ran another command
inside it. It did not install the `ce` command, register a `conda exec` plugin
subcommand, solve package specs, create cached environments, or read script
metadata.

The modern package keeps the `conda-exec` package name but exposes a different
interface:

- `conda exec ...` for the conda plugin subcommand
- `ce ...` for the standalone console command

It deliberately does not provide a `conda-exec ENV COMMAND ...` compatibility
entry point. That spelling would look compatible while doing something
substantially different. For the old "run this command inside an existing
environment" use case, use conda's native command instead:

```bash
conda run -n ENV COMMAND ...
```

For ephemeral tool execution, use:

```bash
conda exec TOOL ...
ce TOOL ...
```

## Clean up old assumptions

- The modern cache lives under `~/.conda/exec` by default.
- Old cache or configuration from the historical package is not reused.
- The standalone `ce` command is equivalent to `conda exec`.
- Script execution uses PEP 723 metadata and can be made reproducible with
  `--lock`.
