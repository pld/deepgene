# DeepGene

AI-powered gene research tool that combines deterministic database data with AI analysis for comprehensive genetic variant investigation.

## Overview

DeepGene helps researchers analyze genetic variants by:
- Fetching curated gene data from MyGene.info
- Performing AI-powered functional and disease analysis
- Mining scientific literature from PubMed
- Extracting mutation mentions using NER
- Providing comprehensive, structured reports

Available in two implementations:
- **Python CLI** - Command-line tool for terminal use
- **TypeScript/React Web** - Browser-based single-page application

## Quick Start

### Web Version (Recommended for Most Users)

**Try it now:** [https://github.io/your-username/deepgene](https://github.io/your-username/deepgene) *(update after deployment)*

Or run locally:
```bash
cd js
npm install
npm run dev
```

Open http://localhost:5173 and enter your Google AI Studio API key when prompted.

### Python CLI Version

```bash
cd py
uv sync
uv run deepgene
```

Follow the interactive prompts to set up your API key and perform lookups.

## Project Structure

```
deepgene/
├── js/          # TypeScript/React web application
│   ├── src/
│   │   ├── components/     # React UI components
│   │   ├── lib/            # Core functionality
│   │   └── types.ts        # TypeScript interfaces
│   ├── dist/               # Built single HTML file
│   └── README.md           # Web app documentation
│
└── py/          # Python CLI application
    ├── deepgene/
    │   ├── gene_lookup.py      # AI-powered lookup
    │   ├── gene_data.py        # MyGene.info client
    │   ├── literature_fetcher.py  # PubMed integration
    │   ├── mutant_extractor.py    # NER extraction
    │   └── shell.py            # Interactive CLI
    ├── tests/              # Test suite
    └── README.md           # Python app documentation

```

## Features

### Both Versions

- ✅ MyGene.info integration for curated gene data
- ✅ AI-powered functional and disease analysis
- ✅ PubMed literature fetching
- ✅ Mutation extraction from papers (NER)
- ✅ Model-agnostic AI framework (easy provider swapping)
- ✅ Comprehensive test coverage
- ✅ Structured output schemas

### Python CLI Specific

- Rich terminal UI with color-coded output
- Persistent API key storage (encrypted)
- History of lookups
- Batch processing support
- Offline mode with cached data

### Web App Specific

- Single standalone HTML file (no server needed)
- In-browser execution (client-side only)
- Real-time progress tracking
- Memory-only API key storage (privacy-first)
- GitHub Pages deployment ready
- Works offline after initial load

## Technology Stack

### Python Version

| Component | Technology |
|-----------|-----------|
| AI Framework | DSPy (model-agnostic) |
| Default Model | Gemini 2.5 Flash |
| Database Client | mygene Python library |
| CLI Framework | cmd + rich |
| HTTP Client | requests + urllib |
| Schema Validation | Pydantic |
| Testing | pytest |
| Package Manager | uv |

### TypeScript Version

| Component | Technology |
|-----------|-----------|
| AI Framework | Vercel AI SDK (model-agnostic) |
| Default Model | Gemini 2.5 Flash Lite |
| UI Framework | React 18 |
| Build Tool | Vite + vite-plugin-singlefile |
| Schema Validation | Zod |
| Testing | Vitest + Testing Library |
| Package Manager | npm |

## Architecture

Both versions follow the same data flow:

```
1. User Input
   ↓
2. Parse gene symbol from positional gene
   ↓
3. Fetch MyGene.info data (optional, deterministic)
   ↓
4. AI Analysis (Gemini by default)
   - Gene function
   - Associated diseases
   - Related SNPs
   - Literature references
   ↓
5. Literature Enhancement
   - Fetch paper content from PubMed
   - Extract mutations using NER
   - Merge with AI-generated mutations
   ↓
6. Display structured results
```

### DSPy → Vercel AI SDK Mapping

The TypeScript version uses Vercel AI SDK with Zod schemas to achieve the same model-agnostic structured outputs as DSPy:

| Python (DSPy) | TypeScript (Vercel AI SDK) |
|---------------|---------------------------|
| `dspy.Signature` | Zod schema (`z.object()`) |
| `InputField` | Prompt string |
| `OutputField` | Zod schema field |
| `dspy.ChainOfThought` | `generateObject()` |
| `.desc("...")` | `.describe("...")` |

Both guarantee typed, structured responses from LLMs.

## Model Agnosticism

Both versions support multiple AI providers:

**Python (DSPy):**
```python
import dspy
# Google
lm = dspy.LM("google/gemini-2.5-flash-exp", api_key=key)
# OpenAI
lm = dspy.LM("openai/gpt-4-turbo", api_key=key)
# Anthropic
lm = dspy.LM("anthropic/claude-3-5-sonnet", api_key=key)
```

**TypeScript (Vercel AI SDK):**
```typescript
// Google
const provider = createGoogleGenerativeAI({ apiKey });
// OpenAI
const provider = createOpenAI({ apiKey });
// Anthropic
const provider = createAnthropic({ apiKey });
```

## API Keys

### Google AI Studio (Default)

1. Visit https://aistudio.google.com/apikey
2. Create a new API key
3. Enter it when prompted by the app

**Python CLI:** Stores encrypted key locally
**Web App:** Stores in memory only (never persisted)

### Other Providers

Both versions can be configured to use OpenAI, Anthropic, Cohere, or any other supported provider. See individual README files for details.

## Development

### Python

```bash
cd py
uv sync                    # Install dependencies
uv run pytest              # Run tests
uv run deepgene            # Run application
```

### TypeScript

```bash
cd js
npm install                # Install dependencies
npm test                   # Run tests
npm run dev                # Development server
npm run build              # Production build
```

## Deployment

### Python CLI

Distribute as a Python package or standalone executable:
```bash
cd py
uv build
```

### Web App

**GitHub Pages (automatic):**

The repository includes a workflow at `.github/workflows/deploy.yml` that builds the web app from the `js/` directory.

1. Push to `main` branch
2. Go to repository Settings → Pages
3. Under Source, select "GitHub Actions"
4. The workflow automatically builds `js/dist/index.html` and deploys it
5. App will be available at `https://<username>.github.io/<repo-name>/`

**Manual:**
- Upload `js/dist/index.html` to any static host
- Works on Netlify, Vercel, Cloudflare Pages, etc.
- No server-side processing required

## Testing

Both versions have comprehensive test suites:

**Python:**
```bash
cd py
uv run pytest                    # All tests
uv run pytest --cov              # With coverage
uv run pytest tests/test_gene_parser.py  # Specific test
```

**TypeScript:**
```bash
cd js
npm test                         # All tests
npm run test:ui                  # Interactive UI
npm run test:coverage            # With coverage
```

## Use Cases

- **Academic Research**: Investigate genetic variants and their associations
- **Clinical Genomics**: Analyze patient variants for disease connections
- **Literature Review**: Extract mutation mentions from papers
- **Drug Discovery**: Identify genes related to specific diseases
- **Bioinformatics**: Integrate with genomic pipelines

## Example Usage

### Input
- rsID: `rs116515942`
- Annotation: `intronic`
- Positional Gene: `CTNND2 (delta catenin-2)`

### Output
- Gene database info (GO terms, pathways, OMIM diseases)
- AI-generated functions (detailed biological roles)
- Associated diseases (comprehensive list)
- Related SNPs (with genes and phenotypes)
- Literature (PubMed papers with extracted mutations)

## Contributing

Both implementations follow the same architecture and should be kept in sync when adding features.

### Adding a New Feature

1. Implement in Python version first (`py/`)
2. Add tests
3. Port to TypeScript version (`js/`)
4. Add tests
5. Update both README files
6. Submit pull request

## License

MIT

## Citation

If you use DeepGene in your research, please cite:

```
[Add citation information when available]
```

## Support

- **Issues**: https://github.com/your-username/deepgene/issues
- **Discussions**: https://github.com/your-username/deepgene/discussions
- **Documentation**: See `py/README.md` and `js/README.md`

## Acknowledgments

- **MyGene.info** - Gene database API
- **PubMed/NCBI** - Literature database and E-utilities API
- **Google AI Studio** - Gemini API access
- **DSPy** - Python AI framework
- **Vercel AI SDK** - TypeScript AI framework
