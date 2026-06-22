# Use custom channels

By default, conda-exec searches the channels from your conda configuration.
You can specify alternative or additional
[conda channels](https://docs.conda.io/projects/conda/en/stable/user-guide/concepts/channels.html)
from the CLI or inside script metadata.

## Specify a channel from the CLI

Use `-c` or `--channel` to add a channel before the configured channels:

```bash
conda exec -c bioconda samtools view input.bam
```

## Use multiple channels

Repeat `-c` to add multiple channels. CLI channels are searched in the
order given, followed by the configured channels, subject to conda's configured
[channel priority](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-channels.html#strict-channel-priority):

```bash
conda exec -c bioconda -c defaults samtools view input.bam
```

To search only the channels you pass on the command line, add
`--override-channels`.

Include support channels explicitly when they are not already in your conda
configuration:

```bash
conda exec -c conda-forge -c bioconda samtools view input.bam
```

## Bioinformatics example

Many bioinformatics tools live in the `bioconda` channel and depend on
packages from `conda-forge`. Specify both:

```bash
conda exec -c conda-forge -c bioconda minimap2 -a ref.fa reads.fq > out.sam
```

## Declare channels in script metadata

For Python scripts with [PEP 723](https://peps.python.org/pep-0723/)
inline metadata, declare channels in the `[tool.conda]` table:

```python
# /// script
# [tool.conda]
# channels = ["conda-forge", "bioconda"]
# dependencies = ["samtools>=1.19", "pysam"]
# ///

import pysam
print(pysam.__version__)
```

```bash
conda exec script.py
```

## Combine script channels with CLI channels

```{tip}
Channels are searched in order. Channels declared in script metadata come
first, followed by any CLI channels. Put your preferred channel first to
give it higher priority.
```

CLI channels (`-c`) are appended after channels declared in script metadata.
Given a script that declares `channels = ["conda-forge"]`, running:

```bash
conda exec -c bioconda script.py
```

resolves packages using `["conda-forge", "bioconda"]` in that order.

If neither the script metadata nor the CLI provides channels, conda-exec uses
the channels from your conda configuration.

## How channels affect caching

Different channel combinations produce different cache keys. Running the
same tool with different `-c` flags creates separate cached environments:

```bash
conda exec ruff check .                 # cached as ruff--<hash1>
conda exec -c defaults ruff check .     # cached as ruff--<hash2>
```

The cache key treats channel order as the same channel set. On a cache miss,
the order you pass is used for the solve. If you change only the order of
the same channels and need conda to solve again with that order, use
`--refresh`.
