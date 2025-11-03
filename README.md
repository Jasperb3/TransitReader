# TransitReader

**AI-Powered Astrological Transit Analysis System**

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/Jasperb3/TransitReader)
[![Python](https://img.shields.io/badge/python-3.12.9-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.126.0-green.svg)](https://www.crewai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

TransitReader is a sophisticated astrological analysis system that combines astronomical precision with deep psychological interpretation. Using CrewAI's multi-agent orchestration, it generates comprehensive, publication-quality transit reports that integrate technical accuracy, symbolic richness, and practical life guidance.

---

## ✨ Features

### 🔮 **Multi-Layered Analysis**
- **Transit Climate Analysis** - Collective energetic patterns and psychological themes
- **Natal Chart Foundations** - Individual predispositions and archetypal blueprints
- **Transit-to-Natal Activations** - Personalized developmental themes and timing arcs
- **Parallel Execution** - ~60% faster processing with intelligent crew orchestration

### 📅 **Flexible Transit Modes**
Choose from 4 analysis modes:
1. **Current time, current location** (real-time analysis)
2. **Custom time, current location** (historical/future analysis)
3. **Current time, custom location** (location-based forecasting)
4. **Custom time, custom location** (full flexibility for relocations, events)

### 📊 **Professional Report Structure**
- **Executive Summary** - Plain-language essence with key dates and emotional weather forecast
- **Real-World Signals** - Concrete scenarios and decision-making guidance per theme
- **Questions for Reflection** - Self-inquiry prompts for active engagement
- **Working With This Energy** - Quick-start practices and emergency protocols
- **Technical Overview** - Degree-accurate data with orb measurements (always 2 decimals)
- **Actionable Life Guidance** - Psychologically grounded recommendations tied to timing

### 🎯 **Quality Assurance**
- **Review & Enhancement Crews** - Automated critique and refinement cycles
- **Language Precision Standards** - Direct psychological terms, active voice, professional authority
- **Technical Formatting** - Standardized orb/degree/planet syntax throughout
- **Grounded Interpretation** - QdrantSearchTool vector search against astrological literature

### 📄 **Professional PDF Output**
- Optimized CSS for WeasyPrint rendering
- Print-friendly formatting with smart page breaks
- Clean typography and visual hierarchy
- Chart wheel integration (via Kerykeion)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12.9** (required)
- **API Keys:**
  - OpenAI (GPT-4.1 for analysis)
  - Google Search API + Custom Search Engine ID (for Gemini search)
  - Google Gemini API (for large context analysis)
  - Qdrant Cloud (for vector search)

### Installation

```bash
# Clone the repository
git clone https://github.com/Jasperb3/TransitReader.git
cd TransitReader

# Install dependencies with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Environment Setup

Create a `.env` file in the project root:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Google Search (for Gemini search tool)
GOOGLE_SEARCH_API_KEY=your_google_api_key_here
SEARCH_ENGINE_ID=your_custom_search_engine_id_here

# Google Gemini (for large context analysis)
GOOGLE_API_KEY=your_gemini_api_key_here

# Qdrant Cloud (for vector search)
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_cluster_url_here
QDRANT_COLLECTION_NAME=your_collection_name_here
```

### Subject Configuration

Create subject files in `src/transit_reader/subjects/`:

**Example: `john_doe.json`**
```json
{
  "name": "John Doe",
  "date_of_birth": "1990-01-15 14:30",
  "birthplace": {
    "city": "London",
    "country": "UK"
  },
  "current_location": {
    "city": "New York",
    "country": "USA"
  },
  "email": "john.doe@example.com"
}
```

**Optional:** `email` field for automated Gmail delivery (requires Gmail API setup)

### Running Analysis

```bash
# Run the analysis
uv run kickoff

# Select subject from available profiles
# Choose transit analysis mode (current/custom time & location)
# Wait for multi-crew analysis pipeline to complete (~5-10 minutes)
```

**Output Locations:**
- **Markdown Report:** `crew_outputs/{timestamp}/final_report.md`
- **PDF Report:** `crew_outputs/{timestamp}/final_report.pdf`
- **Intermediate Outputs:** All crew analysis stages saved for review

---

## 🏗️ Architecture

### Multi-Agent Crew System

TransitReader uses **7 specialized crews** orchestrated via CrewAI Flow:

```
┌─────────────────────────────────────────────────────────────┐
│                    TransitFlow Pipeline                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Transit   │  │   Natal     │  │  Transit-   │         │
│  │  Analysis   │  │  Analysis   │  │  to-Natal   │ ────▶   │
│  │    Crew     │  │    Crew     │  │   Crew      │ Parallel│
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Transit   │  │   Natal     │  │  Transit-   │         │
│  │   Review    │  │   Review    │  │  to-Natal   │ ────▶   │
│  │    Crew     │  │    Crew     │  │   Review    │ Parallel│
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                  │
│         └────────────────┴────────────────┘                  │
│                       │                                      │
│                       ▼                                      │
│              ┌─────────────────┐                             │
│              │  Report Writing │                             │
│              │      Crew       │ ────▶ Sequential            │
│              └─────────────────┘                             │
│                       │                                      │
│                       ▼                                      │
│              ┌─────────────────┐                             │
│              │  Report Review  │                             │
│              │      Crew       │ ────▶ Sequential            │
│              └─────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### Crew Responsibilities

| Crew | Purpose | Agents | Temperature |
|------|---------|--------|-------------|
| **Transit Analysis** | Extract current transit data and themes | Reader (0.1), Interpreter (0.9) | Strategic split |
| **Natal Analysis** | Extract natal chart structure and themes | Reader (0.1), Interpreter (0.9) | Strategic split |
| **Transit-to-Natal** | Identify personal activations and arcs | Reader (0.1), Interpreter (0.9) | Strategic split |
| **Transit Review** | Critique and enhance transit analysis | Critic (0.7), Enhancer (0.7) | Moderate |
| **Natal Review** | Critique and enhance natal analysis | Critic (0.7), Enhancer (0.7) | Moderate |
| **Transit-to-Natal Review** | Critique and enhance activation analysis | Critic (0.7), Enhancer (0.7) | Moderate |
| **Report Writing** | Synthesize and structure final report | Interpreter (0.7), Writer (0.7) | Moderate |
| **Report Review** | Final quality assurance and polish | Critic (0.7), Enhancer (0.7) | Moderate |

**Temperature Strategy:**
- **0.1** (Deterministic) - Technical data extraction, chart reading
- **0.7** (Moderate) - Report writing, synthesis, reviews
- **0.9** (Creative) - Psychological interpretation, symbolic analysis

### Tools & Libraries

**Astronomical Calculations:**
- **Immanuel** - Ephemeris calculations, chart generation
- **Kerykeion** - Chart wheel visualization

**AI & Search:**
- **OpenAI GPT-4.1** - Multi-agent reasoning and analysis
- **Google Gemini** - Large context codebase analysis
- **Qdrant** - Vector similarity search for grounded interpretations
- **Google Search API** - Web search for research

**PDF Generation:**
- **WeasyPrint** - HTML/CSS to PDF rendering
- **Custom CSS** - 756-line optimized stylesheet

---

## 📖 Configuration

### LLM Temperature Settings

Located in crew Python files (`*_crew.py`):

```python
# Deterministic models (technical extraction)
gpt41_deterministic = LLM(
    model="gpt-4.1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.1
)

# Creative models (psychological interpretation)
gpt41_creative = LLM(
    model="gpt-4.1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.9
)

# Moderate models (synthesis, writing)
gpt41 = LLM(
    model="gpt-4.1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7
)
```

### Agent & Task Customization

All agents and tasks are configured via YAML in `src/transit_reader/crews/*/config/`:
- **`agents.yaml`** - Agent roles, goals, backstories
- **`tasks.yaml`** - Task descriptions, expected outputs

**Example customization:**
```yaml
# src/transit_reader/crews/natal_analysis_crew/config/agents.yaml
natal_chart_interpreter:
  role: >
    Natal Psychological Theme Interpreter
  goal: >
    To synthesize the subject's natal chart structure into core psychological themes
  backstory: >
    You are a professional natal chart interpreter with deep grounding in psychological astrology...
```

### QdrantSearchTool Query Strategy

Optimized for vector search accuracy:
- **Use SHORT queries** (2-4 words)
- **Core astrological terms only** (planet, sign, house, aspect)
- **Omit interpretive words** ("meaning", "interpretation", "natal")

**Good queries:**
- "Saturn square Sun"
- "Yod configuration"
- "Mars combust"

**Bad queries:**
- "Saturn square natal Sun meaning"
- "Yod configuration natal interpretation"

---

## 🛠️ Development

### Project Structure

```
transit_reader/
├── src/transit_reader/
│   ├── crews/                      # All crew definitions
│   │   ├── natal_analysis_crew/
│   │   ├── transit_analysis_crew/
│   │   ├── transit_to_natal_analysis_crew/
│   │   ├── natal_analysis_review_crew/
│   │   ├── transit_analysis_review_crew/
│   │   ├── transit_to_natal_review_crew/
│   │   ├── report_writing_crew/
│   │   └── review_crew/
│   ├── tools/                      # Custom tools
│   │   ├── gemini_search_tool.py
│   │   ├── google_search_tool.py
│   │   └── qdrant_search_tool.py
│   ├── utils/                      # Utilities
│   │   ├── immanuel_natal_chart.py
│   │   ├── immanuel_transit_chart.py
│   │   ├── immanuel_natal_to_transit_chart.py
│   │   ├── kerykeion_chart.py
│   │   ├── models.py               # Pydantic state models
│   │   ├── embeddings_fn.py        # Qdrant embeddings
│   │   └── astro_styling.css       # PDF styling
│   ├── subjects/                   # Subject JSON files
│   ├── main.py                     # Flow orchestration
│   └── __init__.py
├── crew_outputs/                   # Generated reports
├── pyproject.toml                  # Project configuration
├── uv.lock                         # Dependency lock file
└── README.md                       # This file
```

### Adding New Subjects

1. Create JSON file in `src/transit_reader/subjects/`
2. Include required fields: `name`, `date_of_birth`, `birthplace`
3. Optional: `current_location`, `email`
4. Run `uv run kickoff` and select from list

### Custom Transit Scenarios

The interactive prompt supports:
- **Historical analysis** - Past transits (e.g., "2020-03-15 12:00" for COVID-19 lockdown)
- **Future forecasting** - Upcoming transits (e.g., "2025-12-31 23:59" for New Year)
- **Relocation analysis** - Different locations (e.g., "Paris, France" for travel)
- **Event charts** - Specific moments (e.g., "2024-06-21 14:30" for solstice)

---

## 🔧 Troubleshooting

### Common Issues

**1. API Key Errors**
```bash
# Error: OpenAI API key not found
# Solution: Check .env file has OPENAI_API_KEY set correctly
```

**2. Qdrant Connection Issues**
```bash
# Error: Could not connect to Qdrant
# Solution: Verify QDRANT_URL and QDRANT_API_KEY in .env
# Ensure collection exists with correct dimensions (1536 for text-embedding-3-small)
```

**3. Chart Generation Failures**
```bash
# Error: Immanuel chart generation failed
# Solution: Verify date format is "YYYY-MM-DD HH:MM" in subject JSON
# Check location has valid city and country
```

**4. PDF Rendering Issues**
```bash
# Error: WeasyPrint failed to generate PDF
# Solution: Ensure WeasyPrint dependencies installed (see WeasyPrint docs)
# On Linux: sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

**5. Template Variable Errors**
```bash
# Error: Template variable not found
# Solution: Ensure all crew YAML files use correct variable names:
#   - transit_date (not today)
#   - transit_location (not current_location)
#   - birthplace (not birth_location)
```

### Debug Mode

Enable verbose logging in crew files:
```python
return Crew(
    agents=self.agents,
    tasks=self.tasks,
    process=Process.sequential,
    verbose=True  # Enable detailed logging
)
```

---

## 📊 Performance

### Execution Time

**Before Optimization:**
- Sequential execution: ~15-20 minutes
- Single-threaded processing

**After Phase 2 Optimization:**
- Parallel execution: ~6-8 minutes
- **60% faster** with intelligent crew orchestration
- Analysis crews run in parallel (3x speed)
- Review crews run in parallel (2x speed)

### Resource Usage

- **Memory:** ~2-4 GB peak (during parallel execution)
- **API Calls:** ~40-60 GPT-4.1 calls per report
- **Tokens:** ~150,000-250,000 total tokens (varies by chart complexity)

---

## 🎯 Roadmap

### Planned Features

- [ ] Solar Return Reports
- [ ] Lunar Return Reports
- [ ] Synastry Analysis (relationship compatibility)
- [ ] Progressive Charts (Secondary Progressions)
- [ ] Composite Charts
- [ ] Transit Calendar (upcoming activations)
- [ ] Multi-language Support
- [ ] API Endpoint (REST/GraphQL)
- [ ] Web Interface
- [ ] Custom Report Templates

### Quality Improvements

- [ ] Expanded Qdrant vector database (more reference material)
- [ ] Chart pattern recognition enhancement
- [ ] Timing arc precision refinement
- [ ] Multi-model LLM support (Anthropic Claude, etc.)

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

**Astrological Libraries:**
- [Immanuel](https://github.com/theriftlab/immanuel-python) - Swiss Ephemeris wrapper
- [Kerykeion](https://github.com/g-battaglia/kerykeion) - Chart visualization

**AI & Tools:**
- [CrewAI](https://www.crewai.com/) - Multi-agent orchestration framework
- [OpenAI](https://openai.com/) - GPT-4.1 language models
- [Qdrant](https://qdrant.tech/) - Vector similarity search

**Development:**
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- [WeasyPrint](https://weasyprint.org/) - PDF rendering

---

## 📧 Contact

**Author:** Benjamin Jasper
**Email:** ben.j.jasper@gmail.com
**GitHub:** [@Jasperb3](https://github.com/Jasperb3)

---

## 🌟 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Conventional Commits Format:**
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `chore:` Maintenance tasks
- `refactor:` Code restructuring

---

**Built with ❤️ using CrewAI and Astrological Wisdom**
