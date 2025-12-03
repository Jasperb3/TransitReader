# TransitReader

AI-assisted transit analysis that blends astronomical calculations, research tools, and structured writing crews to deliver polished astrological reports.

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/Jasperb3/TransitReader)
[![Python](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-1.3.0-green.svg)](https://www.crewai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

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

- Python **3.12.9**
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

## Environment

Create a `.env` file in the project root with the credentials you need:

```env
# OpenAI models for core analysis
OPENAI_API_KEY=...

# Gemini embeddings & summarization
GEMINI_API_KEY=...

# Google Custom Search
GOOGLE_SEARCH_API_KEY=...
SEARCH_ENGINE_ID=...

# Google Maps Geocoding/Timezone (interactive prompts)
GMAPS_API_KEY=...

# Vector store (optional but recommended)
QDRANT_CLUSTER_URL=...
QDRANT_API_KEY=...
QDRANT_COLLECTION_NAME=...

# Gmail draft delivery (optional)
SENDER_EMAIL=you@example.com
CLIENT_EMAIL=recipient@example.com
```

Notes:

- The Qdrant setup ingests any markdown files placed in `astro_docs/` at runtime.
- Gmail OAuth tokens are stored in `src/transit_reader/utils/token.json`; the flow will prompt for re-authentication if the token expires.

---

## Usage

1. **Prepare a subject profile** (or create one interactively)
   - Subject files live in `src/transit_reader/subjects/*.json` and store birth data, current location, email, and optional biographical context.
   - The CLI can create new subjects and fetch latitude/longitude/timezone via Google Maps when `GMAPS_API_KEY` is set.

2. **Start the pipeline**
   ```bash
   uv run kickoff
   ```
   - Choose a subject or create one.
   - Select transit timing: use “now” or enter a custom date/time and location.
   - Answer optional context questions to enrich interpretations.

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

TransitReader uses a CrewAI `Flow` defined in `src/transit_reader/main.py`:

1. **Data & chart setup** – loads vector docs into Qdrant (when configured) and generates transit, natal, and transit-to-natal charts in parallel.
2. **Analysis crews** – three specialized crews run concurrently for transit, natal, and transit-to-natal readings.
3. **Review crews** – each analysis is critiqued and enhanced in parallel.
4. **Appendices** – aggregates technical appendices from all analyses.
5. **Report writing & interrogation** – synthesizes a full report, then critiques and improves it.
6. **Chart rendering & export** – renders a Kerykeion chart, replaces placeholders, writes Markdown, and converts to PDF.
7. **Email drafting** – optionally prepares a Gmail draft with the PDF attached.

### Crews at a Glance

- `transit_analysis_crew` / `transit_analysis_review_crew`
- `natal_analysis_crew` / `natal_analysis_review_crew`
- `transit_to_natal_analysis_crew` / `transit_to_natal_review_crew`
- `chart_appendices_crew`
- `report_writing_crew`
- `review_crew` (final interrogation)
- `gmail_crew` (draft delivery)

### Key Utilities

- `utils/immanuel_*` – chart calculations
- `utils/kerykeion_chart_utils.py` – transit chart rendering
- `utils/qdrant_setup.py` – markdown ingestion and Gemini embeddings for Qdrant
- `utils/convert_to_pdf.py` & `utils/astro_styling.css` – Markdown → PDF
- `utils/subject_selection.py` & `utils/transit_selection.py` – interactive CLI prompts

---

## Troubleshooting

- **API keys not found** – ensure `.env` is loaded and values match the variables above.
- **Qdrant unavailable** – the flow logs a warning and continues without retrieval; verify `QDRANT_CLUSTER_URL`, `QDRANT_API_KEY`, and `QDRANT_COLLECTION_NAME`.
- **WeasyPrint errors** – install system dependencies per WeasyPrint documentation if PDF generation fails.
- **Gmail draft errors** – remove `src/transit_reader/utils/token.json` to re-authorize if the stored token is expired or corrupt.

---

## Contributing

Contributions are welcome! Please use Conventional Commits (`docs:`, `fix:`, `feat:`, etc.) and open a pull request with a clear description of the change.

---

**Built with ❤️ using CrewAI, Immanuel, Kerykeion, and Qdrant**
