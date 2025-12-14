# DeepGene

Gene research tool with interactive shell for looking up rsID information using DSPy and Google Gemini.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create a `.env` file with your Google AI Studio API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Usage

Launch the interactive shell:
```bash
uv run deepgene
```

Available commands:
- `lookup <rsID> <annotation> <positional_gene>` - Look up gene information for the given rsID
- `help` - Show available commands
- `exit` or `quit` - Exit the shell

## Example

```
deepgene> lookup rs116515942 intronic CTNND2 (delta catenin-2)
```

This will query Gemini and display a formatted research report including:
- Annotation (intronic, downstream, etc.)
- Positional gene
- Function (bulleted list)
- Associated diseases (bulleted list)
- Associated SNPs with genes and phenotypes
- Literature references with:
  - Functional relevance
  - Mutants studied
  - URLs to publications

## Features

- Tab completion for rsID history
- Rich terminal output with formatted tables
- Powered by DSPy with Google Gemini 2.5 Flash
- GNU readline support for command line editing
