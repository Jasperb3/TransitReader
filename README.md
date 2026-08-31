# TransitReader

AI-assisted transit analysis that blends astronomical calculations, research tools, and structured writing crews to deliver polished astrological reports.

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/Jasperb3/TransitReader)
[![Python](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.15.18-green.svg)](https://www.crewai.com/)

---

## Overview

TransitReader orchestrates multiple CrewAI agents to read charts, research supporting material, and produce an end-to-end transit report. The `kickoff` entry point prompts for a subject, captures timing and location data, runs parallel analyses, assembles appendices, and exports both Markdown and PDF files (with an optional Gmail draft).

The pipeline relies on:

- **Deterministic chart data** from Immanuel and Kerykeion utilities
- **LLM-backed crews** for reading, interpreting, reviewing, and writing
- **Vector search** (Qdrant + Gemini embeddings) for grounded references
- **Optional email delivery** via Gmail draft creation with attachments

---

## Key Features

- **Parallel multi-crew flow** – transit, natal, and transit-to-natal analyses run concurrently, followed by parallel review crews and appendices generation.
- **Chart production** – Immanuel utilities calculate transits and aspects; Kerykeion renders transit charts saved to `outputs/<date>/charts`.
- **Grounded research** – markdown files in `astro_docs/` are embedded to Qdrant for retrieval during interpretation.
- **Biographical context** – interactive prompts store per-subject context in `src/transit_reader/subjects/*.json`.
- **Polished outputs** – Markdown reports include chart images and appendices, then convert to PDF with WeasyPrint and custom CSS.
- **Optional Gmail draft** – creates a draft email with the PDF attachment when credentials are available.

---

## Requirements

- Python **3.12.9** (3.13 is not supported — see `requires-python` in `pyproject.toml`)
- `uv` (recommended) or `pip` for dependency management
- Access to required API keys (see **Environment** below)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Jasperb3/TransitReader.git
cd TransitReader

# Install dependencies with uv (preferred)
uv sync

# Or install in editable mode with pip
pip install -e .
```

---

## Project Structure

```text
transit_reader/
├── src/transit_reader/
│   ├── crews/
│   │   ├── transit_analysis_crew/            # Reads + interprets current transits
│   │   ├── transit_analysis_review_crew/     # Critiques & enhances the transit analysis
│   │   ├── natal_analysis_crew/              # Reads + interprets the natal chart
│   │   ├── natal_analysis_review_crew/       # Critiques & enhances the natal analysis
│   │   ├── transit_to_natal_analysis_crew/   # Reads + interprets transit-to-natal aspects
│   │   ├── transit_to_natal_review_crew/     # Critiques & enhances that analysis
│   │   ├── chart_appendices_crew/            # Structured technical appendices (optional)
│   │   ├── report_writing_crew/              # Synthesizes the final report
│   │   ├── review_crew/                      # Final report interrogation/critique
│   │   └── gmail_crew/                       # Email drafting & delivery
│   ├── tools/
│   │   ├── qdrant_search_tool.py      # RAG retrieval from astro_docs/
│   │   ├── google_search_tool.py      # Google Custom Search
│   │   ├── gemini_search_tool.py      # Gemini-backed search
│   │   ├── linkup_search_tool.py      # Linkup web search
│   │   └── gmail_tool_with_attachment.py
│   ├── utils/
│   │   ├── immanuel_transit_chart.py         # Current transit chart calculation
│   │   ├── immanuel_natal_chart.py           # Natal chart calculation
│   │   ├── immanuel_natal_to_transit_chart.py # Transit-to-natal aspect calculation
│   │   ├── kerykeion_chart_utils.py          # Chart wheel/transit chart rendering
│   │   ├── qdrant_setup.py                   # Markdown ingestion & Gemini embeddings
│   │   ├── convert_to_pdf.py & astro_styling.css  # Markdown → PDF
│   │   ├── subject_selection.py              # Interactive subject selection/creation
│   │   ├── transit_selection.py              # Custom transit date/time/location prompts
│   │   ├── biographical_questionnaire.py     # Biographical context gathering
│   │   ├── gmail_utility_with_attachment.py  # Gmail draft creation
│   │   ├── llm_manager.py                    # LLM provider/temperature resolution
│   │   └── models.py                         # Pydantic `TransitState` management
│   ├── config/
│   │   └── llm_config.yaml            # LLM provider & agent-model assignments
│   ├── subjects/                      # Birth data + current-location JSON files
│   └── main.py                        # `TransitFlow` pipeline definition
├── astro_docs/                        # Astrology reference material (RAG source)
├── docs/                              # Project/engineering documentation (changelogs,
│                                       #   audits, plans) — not astrology reference material
├── outputs/                            # Generated reports (Markdown + PDF) & charts
├── crew_outputs/                       # Intermediate crew task outputs
└── .env                                # Environment configuration
```

---

## Environment

Copy `.env.example` to `.env` in the project root and fill in the credentials you need:

```bash
cp .env.example .env
```

```env
# OpenAI models for core analysis (GPT-5.6 Terra/Luna reasoning models by default)
OPENAI_API_KEY=...

# Gemini embeddings & summarization
GEMINI_API_KEY=...

# Anthropic Claude models (only if a llm_config.yaml provider uses claude-haiku/claude-sonnet)
ANTHROPIC_API_KEY=...

# Mistral models (only if a llm_config.yaml provider uses mistral)
MISTRAL_API_KEY=...

# Google Custom Search
GOOGLE_SEARCH_API_KEY=...
SEARCH_ENGINE_ID=...

# Linkup web search tool (only if a Linkup-based tool is assigned to an agent)
LINKUP_API_KEY=...

# Google Maps Geocoding/Timezone (interactive prompts)
GMAPS_API_KEY=...

# Vector store (optional but recommended)
QDRANT_LOCAL_URL=...
QDRANT_LOCAL_API_KEY=...
QDRANT_COLLECTION_NAME=...

# Gmail draft delivery (optional)
SENDER_EMAIL=you@example.com
CLIENT_EMAIL=recipient@example.com
REPORT_SENDER_NAME=Your Name
```

Notes:

- `ANTHROPIC_API_KEY` and `MISTRAL_API_KEY` are only required if `src/transit_reader/config/llm_config.yaml` assigns an agent to the `claude-haiku`/`claude-sonnet` or `mistral` provider, respectively.
- The default `gpt5_6_terra`/`gpt5_6_luna` providers are reasoning-effort models: they use a `reasoning_effort` setting (`low`/`medium`/etc.) instead of a temperature preset, since these models reject the `temperature` parameter unless `reasoning.effort="none"`.
- `LINKUP_API_KEY` is only required if a Linkup-based search tool is enabled for an agent.
- The Qdrant setup ingests any markdown files placed in `astro_docs/` at runtime — drop your own astrology reference material there and it will be automatically chunked and embedded on the next run.
- Gmail OAuth tokens are stored in `src/transit_reader/utils/token.json`; the flow will prompt for re-authentication if the token expires.

### Setting up Qdrant

For local use, run Qdrant via Docker and point `QDRANT_LOCAL_URL` at it:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

```env
QDRANT_LOCAL_URL=http://localhost:6333
QDRANT_LOCAL_API_KEY=...  # optional if no auth configured
QDRANT_COLLECTION_NAME=astro_knowledge
```

On first run, `Setup.process_new_markdown_files()` automatically chunks and embeds any markdown files in `astro_docs/` into the collection.

### Setting up Gmail OAuth (optional)

For the Gmail draft delivery step:

1. Enable the Gmail API in [Google Cloud Console](https://console.cloud.google.com/).
2. Create OAuth 2.0 credentials.
3. Run the flow once (triggered automatically on first `kickoff` if Gmail credentials are configured) to generate `src/transit_reader/utils/token.json`.

---

## Usage

1. **Prepare a subject profile** (or create one interactively)
   - Subject files live in `src/transit_reader/subjects/*.json` and store birth data, current location, email, and optional biographical context.
   - The CLI can create new subjects and fetch latitude/longitude/timezone via Google Maps when `GMAPS_API_KEY` is set.
   - Example subject JSON:

     ```json
     {
       "name": "Jane Doe",
       "date_of_birth": "1990-01-01 12:00:00",
       "birthplace": {
         "longitude": -0.1276,
         "latitude": 51.5072,
         "place": "London",
         "country": "UK",
         "timezone": "Europe/London"
       },
       "current_location": {
         "longitude": -0.1276,
         "latitude": 51.5072,
         "place": "London",
         "country": "UK",
         "timezone": "Europe/London"
       },
       "username": "jane.doe",
       "email": "jane.doe@example.com"
     }
     ```

     `timezone` must be a full IANA zone name (e.g. `Europe/London`), not a fixed-offset abbreviation (`GMT`/`CET`) — the latter lacks DST rules and will produce times that drift an hour off in summer.

2. **Start the pipeline**

   ```bash
   uv run kickoff
   ```

   - Choose a subject or create one.
   - Opt in or out of generating chart appendices (detailed technical tables appended to the report).
   - Select transit timing — one of four options:
     1. Current date/time + saved location (default — press Enter)
     2. Custom date/time + saved location
     3. Current date/time + custom location
     4. Custom date/time + custom location
   - Optional biographical context stored in the subject profile is automatically included to enrich interpretations.

3. **Outputs**
   - Markdown: `outputs/<YYYY-MM-DD>/<Name>_<timestamp>.md`
   - PDF: same folder as the markdown (generated via WeasyPrint)
   - Charts: `outputs/<YYYY-MM-DD>/charts/`
   - Intermediate artifacts from crews live under `crew_outputs/<timestamp>/`.

4. **Plot the flow graph (optional)**

   ```bash
   uv run plot
   ```

---

## Architecture

TransitReader uses a CrewAI `Flow` defined in `src/transit_reader/main.py`, maximizing parallelism at each stage via `and_()`:

```text
┌────────────────┐
│ 1. setup_qdrant│ ─── Index astro_docs/ into Qdrant (if configured)
└───────┬────────┘
        │
        ▼
┌──────────────────────┬──────────────────────┬──────────────────────────┐
│ 2a. current_transits  │ 2b. natal_chart      │ 2c. transit_to_natal      │
│    (Immanuel)         │    (Immanuel)        │    (Immanuel)             │  ─ parallel
└───────────┬───────────┴───────────┬──────────┴────────────┬─────────────┘
            │                       │                        │
            ▼                       ▼                        ▼
┌──────────────────────┬──────────────────────┬──────────────────────────┐
│ 3a. transit_analysis  │ 3b. natal_analysis   │ 3c. transit_to_natal      │
│    crew (and_ 2a-2c)  │    crew              │    analysis crew          │  ─ parallel
└───────────┬───────────┴───────────┬──────────┴────────────┬─────────────┘
            │                       │                        │
            ▼                       ▼                        ▼
┌──────────────────────┬──────────────────────┬──────────────────────────┐
│ 4a. transit review    │ 4b. natal review     │ 4c. transit-to-natal      │
│    crew               │    crew              │    review crew            │  ─ parallel
└───────────┬───────────┴───────────┬──────────┴────────────┬─────────────┘
            └───────────────────────┼────────────────────────┘
                                     ▼
                        ┌────────────────────────┐
                        │ 5. chart_appendices     │ ─ optional (user opt-in)
                        │    crew                 │
                        └────────────┬────────────┘
                                     ▼
                        ┌────────────────────────┐
                        │ 6. report_writing_crew  │ ─ waits on all reviews + appendices
                        └────────────┬────────────┘
                                     ▼
                        ┌────────────────────────┐
                        │ 7. review_crew          │ ─ final report interrogation
                        └────────────┬────────────┘
                                     ▼
                        ┌────────────────────────┐
                        │ 8. Kerykeion chart      │ ─ chart image rendering
                        └────────────┬────────────┘
                                     ▼
                        ┌────────────────────────┐
                        │ 9. save (MD → PDF)      │
                        └────────────┬────────────┘
                                     ▼
                        ┌────────────────────────┐
                        │ 10. gmail_crew          │ ─ optional draft delivery
                        └────────────────────────┘
```

### Crews at a Glance

| Crew | Model(s) | Agents | Purpose |
| --- | --- | --- | --- |
| `transit_analysis_crew` | Luna (reader) / Terra (interpreter) | current_transits_reader, current_transits_interpreter | Reads and interprets current transits |
| `transit_analysis_review_crew` | Terra (`review` reasoning_effort) | transits_interpretation_critic, transits_interpretation_enhancer | Critiques & enhances the transit analysis |
| `natal_analysis_crew` | Luna (reader) / Terra (interpreter) | natal_chart_reader, natal_chart_interpreter | Reads and interprets the natal chart |
| `natal_analysis_review_crew` | Terra (`review`) | natal_interpretation_critic, natal_interpretation_enhancer | Critiques & enhances the natal analysis |
| `transit_to_natal_analysis_crew` | Luna (reader) / Terra (interpreter) | transits_to_natal_chart_reader, transits_to_natal_chart_interpreter | Reads and interprets transit-to-natal aspects |
| `transit_to_natal_review_crew` | Terra (`review`) | transits_to_natal_interpretation_critic, transits_to_natal_interpretation_enhancer | Critiques & enhances that analysis |
| `chart_appendices_crew` | Luna (`synthesis`) | chart_data_synthesizer | Structured technical appendices (optional) |
| `report_writing_crew` | Terra (`creative`) | astrological_data_interpreter, astrological_report_writer | Synthesizes the final report from all analyses/reviews/appendices |
| `review_crew` | Terra (`review`) | report_critic, report_enhancer | Final report interrogation before export |
| `gmail_crew` | Terra (`creative`) | email_writer, email_drafter | Composes and drafts the delivery email |

"Luna"/"Terra" refer to the `gpt5_6_luna`/`gpt5_6_terra` providers in `config/llm_config.yaml` — see [Key Utilities](#key-utilities) below for the reasoning_effort-vs-temperature behavior.

### Key Utilities

- `utils/immanuel_*` – chart calculations
- `utils/kerykeion_chart_utils.py` – transit chart rendering
- `utils/qdrant_setup.py` – markdown ingestion and Gemini embeddings for Qdrant
- `utils/convert_to_pdf.py` & `utils/astro_styling.css` – Markdown → PDF
- `utils/subject_selection.py` & `utils/transit_selection.py` – interactive CLI prompts
- `utils/biographical_questionnaire.py` – biographical context gathering and formatting
- `utils/llm_manager.py` + `config/llm_config.yaml` – centralized LLM provider and temperature configuration; swap models by editing the YAML, no code changes needed. Providers can define `reasoning_effort` instead of a temperature preset for reasoning models like GPT-5.6.

---

## Testing

```bash
# Run the full test suite
uv run pytest

# Run a specific test file
uv run pytest tests/test_transit_selection.py
```

The suite covers chart calculations, transit timing/DST edge cases, biographical questionnaire formatting, and crew retry logic.

---

## Dependencies

Key libraries (see `pyproject.toml` for the full, versioned list):

| Package | Purpose |
| --- | --- |
| `crewai[tools]` | Multi-agent orchestration framework |
| `immanuel` | Chart calculation (Swiss Ephemeris) — transits, natal, transit-to-natal |
| `kerykeion` | Chart wheel/transit chart visualization |
| `qdrant-client` | Vector database for RAG |
| `weasyprint` | Markdown/HTML → PDF conversion |
| `google-genai` | Gemini embeddings & search |
| `googlemaps` | Geocoding & timezone lookup for subjects/custom transits |
| `google-auth-oauthlib` / `google-api-python-client` | Gmail OAuth & API access |
| `boto3` / `botocore` | AWS SDK (used by select tools) |
| `linkup-sdk` | Linkup web search tool |
| `selenium` | Browser automation (screenshot utility) |
| `md2pdf` | Markdown → PDF fallback path |
| `html2text` / `trafilatura` | Web content extraction for search tools |

---

## Troubleshooting

- **API keys not found** – ensure `.env` is loaded and values match the variables above. Verify a specific key is set with e.g. `echo $OPENAI_API_KEY`.
- **Qdrant unavailable** – the flow logs a warning and continues without retrieval; verify `QDRANT_LOCAL_URL`, `QDRANT_LOCAL_API_KEY`, and `QDRANT_COLLECTION_NAME`, and that `docker run -p 6333:6333 qdrant/qdrant` (or your hosted instance) is reachable (`curl http://localhost:6333`).
- **WeasyPrint errors** – install system dependencies per WeasyPrint documentation if PDF generation fails.
- **Gmail draft errors** – remove `src/transit_reader/utils/token.json` and re-run the OAuth flow (see [Setting up Gmail OAuth](#setting-up-gmail-oauth-optional)) if the stored token is expired or corrupt.

---

## Contributing

Contributions are welcome! Please use Conventional Commits (`docs:`, `fix:`, `feat:`, etc.) and open a pull request with a clear description of the change.

---

## License

This project is for personal and research use.

---

Built with ❤️ using CrewAI, Immanuel, Kerykeion, and Qdrant.
