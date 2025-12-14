# DeepGene Web - Client-Side Gene Research Tool

AI-powered gene research application that runs entirely in the browser with internet access. Combines deterministic gene data from MyGene.info with AI analysis using Google's Gemini 2.5 Flash.

## Features

- **Client-side only** - Runs entirely in your browser, no backend required
- **Model-agnostic AI** - Uses Vercel AI SDK with structured outputs (Zod schemas like DSPy signatures)
- **Default model** - Gemini 2.0 Flash Exp (easily switchable to OpenAI, Anthropic, etc.)
- **Database integration** - Fetches deterministic gene data from MyGene.info
- **Literature mining** - Extracts mutations from PubMed papers using NER
- **Comprehensive reporting** - Gene functions, diseases, SNPs, and literature references

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Get a Google AI Studio API key:
   - Visit https://aistudio.google.com/apikey
   - Create a new API key
   - You'll be prompted to enter it when you first open the app

## Development

Start the development server:
```bash
npm run dev
```

Open http://localhost:5173 in your browser.

## Building for Production

Build a single standalone HTML file:
```bash
npm run build
```

This creates a self-contained `dist/index.html` file with all JavaScript and CSS inlined. The file can be opened directly in a browser or deployed to any static hosting service.

Preview the build locally:
```bash
npm run preview
```

Or open `dist/index.html` directly in your browser.

## Testing

Run tests:
```bash
npm test
```

Run tests with UI:
```bash
npm run test:ui
```

Run tests with coverage:
```bash
npm run test:coverage
```

## Deployment

### GitHub Pages (Automatic)

This repository includes a GitHub Actions workflow at `../.github/workflows/deploy.yml` that automatically builds and deploys to GitHub Pages.

**Setup:**
1. Go to your repository **Settings → Pages**
2. Under **Source**, select **GitHub Actions**
3. Push to the `main` branch
4. The workflow will automatically build `js/dist/index.html` and deploy
5. Your app will be available at `https://<username>.github.io/<repo-name>/`

The workflow runs on every push to `main` and can also be triggered manually via the Actions tab.

### Manual Deployment

Since the build produces a single `dist/index.html` file, you can deploy to any static hosting:

- **Netlify**: Drag and drop `dist/` folder
- **Vercel**: `vercel deploy`
- **Cloudflare Pages**: Connect repository or upload `dist/`
- **GitHub Gist**: Upload `index.html` as a gist and use [bl.ocks.org](https://bl.ocks.org)
- **Any web server**: Just upload `dist/index.html`

No server-side processing required!

## Usage

1. **Enter API Key**: When you first open the app, enter your Google AI Studio API key
2. **Fill in the form**:
   - **rsID**: Reference SNP ID (e.g., `rs116515942`)
   - **Annotation**: Genomic annotation type (intronic, downstream, etc.)
   - **Positional Gene**: Gene name with optional description (e.g., `CTNND2 (delta catenin-2)`)
3. **Submit**: Click "Lookup Gene" to start the analysis
4. **View Results**: The app will display:
   - Gene database information from MyGene.info
   - AI-generated functional analysis
   - Associated diseases
   - Related SNPs
   - Literature references with extracted mutations

## Architecture

### Tech Stack
- **React** - UI framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **vite-plugin-singlefile** - Bundles everything into one HTML file
- **Vercel AI SDK** - Model-agnostic AI framework with structured outputs (replaces DSPy from Python version)
- **Zod** - Schema validation for structured AI outputs (like DSPy signatures)
- **Vitest** - Testing framework

### Model Agnosticism

The app uses the Vercel AI SDK which supports multiple AI providers:
- **Google Gemini** (default) - via `@ai-sdk/google`
- **OpenAI** - via `@ai-sdk/openai`
- **Anthropic Claude** - via `@ai-sdk/anthropic`
- **Cohere** - via `@ai-sdk/cohere`
- **Mistral** - via `@ai-sdk/mistral`

To switch models, simply:
1. Install the provider package (e.g., `npm install @ai-sdk/openai`)
2. Import and use it instead of `google` in `gene_lookup.ts` and `mutant_extractor.ts`
3. Update the model name (e.g., `openai('gpt-4-turbo')`)

### File Structure
```
js/
├── src/
│   ├── components/          # React components
│   │   ├── LookupForm.tsx   # Gene lookup form
│   │   └── ResultDisplay.tsx # Results display
│   ├── lib/                 # Core libraries
│   │   ├── gene_parser.ts   # Gene symbol extraction
│   │   ├── gene_data.ts     # MyGene.info API client
│   │   ├── literature_fetcher.ts # PubMed paper fetching
│   │   ├── mutant_extractor.ts   # NER extraction
│   │   └── gene_lookup.ts   # Main AI lookup logic
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   ├── types.ts             # TypeScript types
│   └── index.css            # Global styles
├── index.html               # HTML entry point
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
└── vitest.config.ts         # Test config
```

### Data Flow

1. User inputs rsID, annotation, and positional gene
2. Extract gene symbol from positional gene string
3. Fetch deterministic data from MyGene.info (if symbol found)
4. Query Gemini AI for comprehensive gene analysis
5. For each literature reference:
   - Fetch paper abstract from PubMed or via web scraping
   - Extract mutations using NER (powered by Gemini)
   - Merge AI-generated and extracted mutations
6. Display results to user

## Converting from Python

This TypeScript/React app is a direct conversion of the Python CLI version. Key changes:

| Python | TypeScript/React |
|--------|-----------------|
| DSPy | Vercel AI SDK (model-agnostic) |
| DSPy Signatures | Zod schemas |
| cmd + rich | React components |
| Python requests | Browser fetch API |
| Pydantic models | TypeScript interfaces + Zod |
| Python types | TypeScript types |
| pytest | Vitest + Testing Library |

## API Keys and Security

- API keys are **never** stored on disk
- API keys are requested from the user on first use
- API keys are stored in React state (memory only)
- Closing the browser tab clears the API key

## CORS Considerations

The app makes requests to:
- MyGene.info API - CORS enabled
- PubMed E-utilities API - CORS enabled
- Google Gemini API - CORS enabled

If you encounter CORS issues with journal websites when fetching literature, those papers will be skipped and only PubMed papers will be processed.

## License

Same as parent DeepGene project.
