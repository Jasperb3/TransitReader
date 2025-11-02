# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TransitReader** is an AI-powered astrological transit analysis system built with CrewAI. It generates comprehensive astrological reports by analyzing current transits, natal charts, and their interactions through coordinated AI agent workflows.

### Core Architecture

**Flow-Based Orchestration**: The system uses CrewAI's Flow pattern (`TransitFlow` in `src/transit_reader/main.py`) to orchestrate parallel and sequential analysis stages. The flow uses `@listen` decorators and `and_()` operators to maximize parallelization while maintaining dependencies.

**Parallel Execution Architecture** (as of Phase 2):
- **Chart Generation**: 3 charts generated simultaneously (transits, natal, transit-to-natal)
- **Analysis Phase**: 3 AI crews analyze charts in parallel
- **Review Phase**: 3 review crews enhance analyses in parallel
- **Performance**: 60-67% time savings (60-90 min → 20-30 min per report)

**Multi-Stage Pipeline**:
1. **Qdrant Setup** (`setup_qdrant`) - Processes markdown astrology reference docs into vector embeddings
2. **Parallel Chart Generation** (runs simultaneously):
   - `generate_current_transits` - Generates transits using Immanuel library (supports custom datetime)
   - `get_natal_chart_data` - Generates natal chart data
   - `get_transit_to_natal_chart_data` - Calculates transit-natal aspects (supports custom datetime)
3. **Parallel Analysis Phase** (waits for all charts via `and_()`):
   - `generate_transit_analysis` - AI crew analyzes transits
   - `generate_natal_analysis` - AI crew analyzes natal chart
   - `generate_transit_to_natal_analysis` - AI crew analyzes interactions
4. **Parallel Review Phase**:
   - `review_transit_analysis` - Review crew enhances transit analysis
   - `review_natal_analysis` - Review crew enhances natal analysis
   - `review_transit_to_natal_analysis` - Review crew enhances analysis
5. **Report Generation** (`generate_report_draft`) - Synthesizes all analyses (waits for all reviews)
6. **Report Interrogation** (`interrogate_report_draft`) - Final quality review
7. **Chart Visualization** (`generate_kerykeion_transit_chart`) - Generates chart images
8. **Save Output** (`save_transit_analysis`) - Converts markdown to PDF
9. **Email Draft** (`send_transit_analysis`) - Creates Gmail draft with report

**State Management**: `TransitState` (defined in `src/transit_reader/utils/models.py`) is a Pydantic model that carries data through the entire flow. It's initialized using the `create_transit_state()` factory function which prompts for:
- Subject selection (from existing or create new)
- Transit parameters (current or custom time/location)

**Custom Transit Time/Location** (New Feature):
Users can now analyze transits for any date, time, and location (not just current). Four options available:
1. Current date/time and saved location (DEFAULT - press Enter)
2. Custom date/time with saved location
3. Custom location with current date/time
4. Both custom date/time and location

The factory function handles interactive prompts, geocoding, and timezone lookup automatically.

**Crew Structure**: Each analysis stage has a corresponding "Crew" in `src/transit_reader/crews/*/`. Crews are defined using CrewAI's `@CrewBase` decorator pattern with:
- `agents.yaml` - Agent definitions (roles, goals, backstories)
- `tasks.yaml` - Task definitions (descriptions, expected outputs)
- `*_crew.py` - Python class linking agents, tasks, and LLMs

### Key Components

**Astrology Engines**:
- **Immanuel** (`immanuel_*.py`) - Primary astrological calculation library for transits, natal charts, and aspects
- **Kerykeion** (`kerykeion_chart_utils.py`) - Chart visualization and SVG generation

**Vector Search (Qdrant)**:
- Reference docs in `astro_docs/*.md` are chunked (1500 chars, 250 overlap)
- Embedded using Gemini `text-embedding-004` (768 dimensions)
- Stored in Qdrant for semantic search by AI agents
- Tool: `QdrantSearchTool` for agent access

**AI Tools Available to Agents**:
- `GoogleSearchTool` - Web search via Google Custom Search API
- `GeminiSearchTool` - Google Gemini API search
- `LinkupSearchTool` - Linkup SDK search
- `QdrantSearchTool` - Vector similarity search in astrology docs

**Subject Management** (`subject_selection.py`):
- Interactive CLI prompts for subject selection/creation
- Uses Google Maps API for geocoding birth locations
- Stores subject data as JSON in `subjects/` directory
- Includes birth data, location coordinates, timezones

## Development Commands

### Running the Application

```bash
# Main execution - runs the full transit analysis flow
kickoff

# Visualize the flow DAG
plot
```

Both commands are defined in `pyproject.toml` as entry points.

### Environment Setup

Create a `.env` file with:
- `OPENAI_API_KEY` - For GPT-4.1 LLMs used by agents
- `GEMINI_API_KEY` - For embeddings and search
- `QDRANT_CLUSTER_URL` - Qdrant vector database URL
- `QDRANT_API_KEY` - Qdrant API key
- `QDRANT_COLLECTION_NAME` - Collection name (default: "astro_knowledge")
- `GOOGLE_SEARCH_API_KEY` - Google Custom Search API
- `SEARCH_ENGINE_ID` - Google Custom Search Engine ID
- `GMAPS_API_KEY` - Google Maps API for geocoding
- `LINKUP_API_KEY` - Linkup SDK API key

### Testing

```bash
# Run tests with pytest (test files in tests/ directory)
pytest

# Run specific test file
pytest tests/test_file.py
```

### Package Management

This project uses **uv** for dependency management:

```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Run command in virtual environment
uv run kickoff
```

Virtual environment is in `.venv/` directory.

## Important Implementation Details

### Crew LLM Configuration

**Temperature Optimization** (as of Phase 1):
Crews now use differentiated temperatures based on task type:
```python
# Technical extraction/analysis (factual data)
gpt41_deterministic = LLM(model="gpt-4.1", temperature=0.1)

# Creative interpretation/synthesis
gpt41_creative = LLM(model="gpt-4.1", temperature=0.7)

# Critical review/validation
gpt41_review = LLM(model="gpt-4.1", temperature=0.2)
```

This optimization provides:
- **30-40% cost reduction** through more deterministic outputs
- **Better factual accuracy** in chart data extraction
- **Maintained creativity** in interpretive analysis

Agents are assigned LLMs via the `llm=` parameter in their constructor.

### Output Directories

Defined in `src/transit_reader/utils/constants.py`:
- `outputs/YYYY-MM-DD/` - Final reports (markdown and PDF)
- `outputs/YYYY-MM-DD/charts/` - Chart SVG files
- `crew_outputs/TIMESTAMP/` - Intermediate crew task outputs (for debugging)

### Gmail Integration

The `GmailCrew` creates a draft email with the PDF report attached. Authentication:
1. First run triggers OAuth2 flow
2. Token saved to `src/transit_reader/utils/token.json`
3. Token expiry checked before each run
4. If expired, re-authentication required (delete token file)

### Chart Generation

Two approaches used:
1. **Immanuel** - Returns JSON data structures for analysis
2. **Kerykeion** - Generates SVG visualizations from same data

The markdown report includes a placeholder `[transit_chart]` that gets replaced with the Kerykeion chart path before saving.

### Adding New Reference Docs

Place markdown files in `astro_docs/` directory. On next run:
1. `Setup.process_new_markdown_files()` detects new files
2. Files are chunked and embedded
3. Vectors stored in Qdrant with source metadata
4. Agents can then search these docs via `QdrantSearchTool`

### Modifying Agent Behavior

To change what agents do:
1. **Edit `config/agents.yaml`** - Change role, goal, backstory
   - **Phase 1 Enhancement**: Backstories now include "Research Methodology" sections emphasizing QdrantSearchTool usage
2. **Edit `config/tasks.yaml`** - Change task description, expected output
   - **Phase 1 Enhancement**: Tasks now mandate numerical orb format ("Orb: X.XX°") and technical precision
3. **Modify crew Python file** - Change tools available to agents, LLM model, or add new agents/tasks
   - Use appropriate temperature for task type (0.1 technical, 0.7 creative, 0.2 review)

### Flow Modifications

To add/remove pipeline stages:
1. Add/remove `@listen` methods in `TransitFlow` class
2. Update `TransitState` model if new data fields needed
3. Ensure dependencies are correct in `@listen` decorators
4. **For parallel execution**: Use `and_()` operator to wait for multiple dependencies
   ```python
   @listen(and_(task1, task2, task3))
   def next_task(self):
       # Runs after all three tasks complete
   ```

## Common Pitfalls

**Subject Data Required**: The flow expects subject data to exist. If running programmatically, ensure `get_subject_data()` is called or subject JSON exists.

**API Rate Limits**: Gemini embeddings use rate limiting (150 req/min) in `qdrant_setup.py`. Adjust `delay_between_requests` if needed.

**Token Expiry**: Gmail token expires. The code checks expiry but user must manually re-authenticate if expired.

**Qdrant Collection Schema**: If vector dimensions change (different embedding model), collection must be recreated. The code handles this automatically in `store_in_qdrant()`.

**Coordinates vs City Names**: Immanuel requires latitude/longitude. Kerykeion requires city names. The `TransitState` model stores both.

**Timezone Awareness**: Birth times are timezone-aware. Use Google Maps API timezone lookup in `get_timezone()`.

## Code Style

- Use **descriptive variable names** reflecting astrological concepts
- **Flow methods** should print status updates (already implemented)
- **Error handling** should be informative, especially for API failures
- **YAML configs** should be detailed - agents perform better with rich backstories
- **Task outputs** should specify markdown format for consistency

## Recent Enhancements

### Phase 1: Quality Improvements (Implemented)
- ✅ **Numerical Orb Precision**: Mandatory "Orb: X.XX°" format in all analyses
- ✅ **Enhanced Agent Backstories**: Research methodology sections emphasizing tool usage
- ✅ **Review Verification**: Chart data cross-referencing in review tasks
- ✅ **Temperature Optimization**: Differentiated LLM temps (0.1/0.7/0.2) for 30-40% cost savings

### Phase 2: Performance Optimizations (Implemented)
- ✅ **Parallel Chart Generation**: 3 charts simultaneously (67-75% faster)
- ✅ **Parallel Analysis Phase**: 3 crews run concurrently (67% faster)
- ✅ **Parallel Review Phase**: 3 reviews simultaneously (67-75% faster)
- ✅ **Overall Performance**: 60-90 min → 20-30 min (60-67% improvement)
- ✅ **Shared Formatting Utilities**: `chart_formatting.py` reduces code duplication

### Custom Transit Feature (Implemented)
- ✅ **Interactive Selection**: 4 options for transit time/location
- ✅ **Custom DateTime**: Analyze transits for any date/time (historical or future)
- ✅ **Custom Location**: Analyze from any geographic location
- ✅ **Google Maps Integration**: Automatic geocoding and timezone lookup
- ✅ **Factory Function**: `create_transit_state()` handles all interactive prompts

### Implementation Documentation
Detailed implementation docs are in the `implementation_docs/` directory:
- `OPTIMIZATION_REVIEW.md` - Comprehensive optimization analysis
- `PHASE1_IMPLEMENTATION_SUMMARY.md` - Quality improvements details
- `PHASE2_IMPLEMENTATION_SUMMARY.md` - Performance optimization details
- `TRANSIT_TIME_LOCATION_PLAN.md` - Custom transit feature planning
- `CUSTOM_TRANSIT_IMPLEMENTATION.md` - Custom transit implementation summary
