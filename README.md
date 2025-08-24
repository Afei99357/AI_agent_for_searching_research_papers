# Research Paper Search Agent

A powerful academic literature search tool that uses LLM-enhanced queries to find peer-reviewed papers from online databases with advanced time filtering and export capabilities.

## Features

- 🔍 **LLM-Enhanced Queries**: Uses Qwen3 model to automatically add relevant academic keywords
- 📅 **Flexible Time Filtering**: Years back, year ranges, or month ranges (mutually exclusive)
- 🌐 **Semantic Scholar**: High-quality academic database with abstracts and author information
- 💾 **Incremental Saves**: Saves progress every 5 papers to prevent data loss
- 📊 **Structured JSON Export**: Clean, parseable output format
- 🔄 **Error Recovery**: Skips problematic papers and continues processing
- 📈 **Real-time Progress**: Shows processing progress and paper counts
- 🎯 **Month-Level Granularity**: Break searches into small chunks to work within API limits
- 📄 **PDF Downloads**: Automatic PDF downloading with open access and university access modes

## Prerequisites

### Required Software
- Python 3.13+
- [Ollama](https://ollama.com/) with qwen2.5:3b model
- UV package manager (or pip)

### Install Ollama

#### On macOS
```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Or with Homebrew
brew install ollama
```

#### On Linux
```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

#### On Windows
1. Download Ollama from https://ollama.com/download/windows
2. Run the installer
3. Open Command Prompt or PowerShell

#### Pull the Required Model
After installing Ollama:
```bash
# Start Ollama service (if not auto-started)
ollama serve

# In a new terminal, pull the required model
ollama pull qwen2.5:3b
```

### Setup Project
```bash
# Clone the repository
git clone https://github.com/Afei99357/AI_agent_for_searching_research_papers.git
cd AI_agent_for_searching_research_papers

# Install dependencies
uv sync
# or with pip
pip install -r requirements.txt
```

## Quick Start

### Basic Usage
```bash
# Simple search (last 10 years, 20 results)
uv run python online_literature_search.py "machine learning healthcare"

# Save to file
uv run python online_literature_search.py "machine learning healthcare" --output results.json

# Download PDFs automatically
uv run python online_literature_search.py "quantum computing" --download-pdfs

# University access with PDFs
uv run python online_literature_search.py "medical imaging AI" \
  --download-pdfs \
  --pdf-mode university_access \
  --output medical_ai.json
```

## Usage Examples

### 1. Time-based Searches (Mutually Exclusive Options)

**Important**: You can only use ONE time filtering option per search.

#### Years Back (Relative - Default)
Used when no other time option is specified.
```bash
# Default: last 10 years (no time option needed)
uv run python online_literature_search.py "west nile virus prediction"

# Last 5 years
uv run python online_literature_search.py "west nile virus prediction" --years-back 5

# Last 15 years with more results
uv run python online_literature_search.py "climate change modeling" --years-back 15 --max-results 100
```

#### Specific Year Ranges (Absolute)
Overrides years-back when specified.
```bash
# Papers from 2018-2020
uv run python online_literature_search.py "COVID-19 treatment" --year-range "2018-2020"

# Papers from only 2019
uv run python online_literature_search.py "quantum computing" --year-range "2019"

# Papers from 2015-2017
uv run python online_literature_search.py "deep learning" --year-range "2015-2017"
```

#### Month-Level Filtering (Most Specific - Recommended for API Limits)
Overrides both other options when specified.
```bash
# Papers from January to June 2025 (perfect for API limits!)
uv run python online_literature_search.py "west nile virus prediction" --month-range "2025-01-2025-06"

# Papers from March 2024 only
uv run python online_literature_search.py "machine learning" --month-range "2024-03-2024-03"

# Papers spanning multiple years by months (2023-12 to 2024-02)
uv run python online_literature_search.py "COVID vaccines" --month-range "2023-12-2024-02"
```

**Error Example**: If you try to use multiple options:
```bash
# This will show an error message
uv run python online_literature_search.py "your query" --years-back 5 --month-range "2025-01-2025-06"
```

### 2. Result Quantity Control

```bash
# Get maximum from Semantic Scholar (100 papers without API key)
uv run python online_literature_search.py "blockchain security" --max-results 100

# Small focused search
uv run python online_literature_search.py "quantum entanglement" --max-results 25

# Default search (20 papers)
uv run python online_literature_search.py "artificial intelligence ethics"
```

### 3. PDF Downloading

#### Open Access Mode (Default - Safe & Legal)
```bash
# Download only open access PDFs (arXiv, PMC, etc.)
uv run python online_literature_search.py "machine learning healthcare" \
  --download-pdfs \
  --max-results 50 \
  --output ml_health.json

# Specify custom PDF directory
uv run python online_literature_search.py "quantum computing" \
  --download-pdfs \
  --pdf-dir "quantum_papers" \
  --max-results 30
```

#### University Access Mode (With Institutional Access)
```bash
# Try all sources including publisher direct downloads
uv run python online_literature_search.py "climate change modeling" \
  --download-pdfs \
  --pdf-mode university_access \
  --max-results 40 \
  --output climate_papers.json

# Combine with time filtering for focused collection
uv run python online_literature_search.py "covid vaccine efficacy" \
  --download-pdfs \
  --pdf-mode university_access \
  --month-range "2023-01-2023-12" \
  --pdf-dir "covid_vaccines_2023"
```

#### PDF Download Sources
**Open Access Mode** (safe, legal, free):
- arXiv preprints
- PubMed Central (PMC) 
- Unpaywall database
- Open access journals

**University Access Mode** (requires institutional access):
- All open access sources above
- Publisher direct downloads (Elsevier, Springer, etc.)
- Institutional repository links
- DOI-based downloads

### 4. Comprehensive Examples (Combining Multiple Options)

#### Basic Research with PDFs
```bash
# Simple search with PDF downloads
uv run python online_literature_search.py "neural networks" \
  --download-pdfs \
  --max-results 30 \
  --output neural_networks.json

# Recent papers with custom PDF directory
uv run python online_literature_search.py "transformer models" \
  --years-back 2 \
  --download-pdfs \
  --pdf-dir "transformer_papers" \
  --max-results 50 \
  --output transformers_2years.json
```

#### University Research (With Institutional Access)
```bash
# Medical research with university access
uv run python online_literature_search.py "cancer immunotherapy" \
  --download-pdfs \
  --pdf-mode university_access \
  --year-range "2022-2024" \
  --max-results 75 \
  --output cancer_immuno.json

# Specific time period with full access
uv run python online_literature_search.py "COVID-19 vaccine efficacy" \
  --download-pdfs \
  --pdf-mode university_access \
  --month-range "2023-01-2023-12" \
  --pdf-dir "covid_vaccines_2023" \
  --output covid_vaccines_2023.json
```

#### Large Scale Research Projects
```bash
# Systematic literature review
uv run python online_literature_search.py "systematic review meta-analysis" \
  --year-range "2020-2024" \
  --download-pdfs \
  --pdf-mode university_access \
  --max-results 100 \
  --pdf-dir "systematic_reviews" \
  --output systematic_review_papers.json

# Comprehensive AI research collection
uv run python online_literature_search.py "artificial intelligence healthcare" \
  --years-back 3 \
  --download-pdfs \
  --max-results 100 \
  --pdf-dir "ai_healthcare_3years" \
  --output ai_healthcare.json
```

#### Working Within API Limits
```bash
# Break large searches into manageable chunks
uv run python online_literature_search.py "climate change modeling" \
  --month-range "2024-01-2024-03" \
  --download-pdfs \
  --max-results 100 \
  --pdf-dir "climate_q1_2024" \
  --output climate_q1_2024.json

uv run python online_literature_search.py "climate change modeling" \
  --month-range "2024-04-2024-06" \
  --download-pdfs \
  --max-results 100 \
  --pdf-dir "climate_q2_2024" \
  --output climate_q2_2024.json

# Single month for very active research areas
uv run python online_literature_search.py "large language models" \
  --month-range "2024-06-2024-06" \
  --download-pdfs \
  --pdf-mode university_access \
  --max-results 100 \
  --pdf-dir "llm_june_2024" \
  --output llm_june_2024.json
```

### 5. Domain-Specific Examples with PDF Downloads

#### Medical Research
```bash
# Clinical studies with university access
uv run python online_literature_search.py "cancer immunotherapy clinical trial" \
  --download-pdfs \
  --pdf-mode university_access \
  --year-range "2022-2024" \
  --max-results 60 \
  --pdf-dir "cancer_trials" \
  --output cancer_trials.json

# Epidemiology papers (open access focus)
uv run python online_literature_search.py "COVID-19 epidemiology transmission" \
  --download-pdfs \
  --month-range "2023-01-2023-12" \
  --max-results 80 \
  --pdf-dir "covid_epidemiology" \
  --output covid_epidemiology.json

# Drug discovery research
uv run python online_literature_search.py "drug discovery artificial intelligence" \
  --download-pdfs \
  --pdf-mode university_access \
  --years-back 3 \
  --max-results 75 \
  --pdf-dir "ai_drug_discovery" \
  --output ai_drug_discovery.json
```

#### Computer Science
```bash
# AI/ML research with PDFs (often on arXiv)
uv run python online_literature_search.py "transformer neural networks attention" \
  --download-pdfs \
  --month-range "2024-01-2024-06" \
  --max-results 100 \
  --pdf-dir "transformer_papers" \
  --output transformers_h1_2024.json

# Cybersecurity research with university access
uv run python online_literature_search.py "zero-day vulnerability detection machine learning" \
  --download-pdfs \
  --pdf-mode university_access \
  --year-range "2022-2024" \
  --max-results 50 \
  --pdf-dir "cybersec_ml" \
  --output cybersecurity_ml.json

# Software engineering research
uv run python online_literature_search.py "code review automation deep learning" \
  --download-pdfs \
  --years-back 4 \
  --max-results 60 \
  --pdf-dir "code_review_ai" \
  --output code_review_automation.json
```

#### Environmental Science
```bash
# Climate modeling research
uv run python online_literature_search.py "climate change modeling machine learning" \
  --download-pdfs \
  --pdf-mode university_access \
  --years-back 5 \
  --max-results 80 \
  --pdf-dir "climate_ml" \
  --output climate_modeling_ml.json

# Conservation biology with recent findings
uv run python online_literature_search.py "species extinction prediction biodiversity" \
  --download-pdfs \
  --month-range "2023-01-2024-06" \
  --max-results 70 \
  --pdf-dir "biodiversity_prediction" \
  --output extinction_prediction.json

# Marine science research
uv run python online_literature_search.py "ocean acidification coral reef impact" \
  --download-pdfs \
  --pdf-mode university_access \
  --year-range "2020-2024" \
  --max-results 65 \
  --pdf-dir "ocean_acidification" \
  --output ocean_acidification.json
```

#### Physics and Engineering
```bash
# Quantum computing research (often on arXiv)
uv run python online_literature_search.py "quantum error correction algorithm" \
  --download-pdfs \
  --years-back 3 \
  --max-results 55 \
  --pdf-dir "quantum_error_correction" \
  --output quantum_ecc.json

# Materials science with university access
uv run python online_literature_search.py "perovskite solar cell efficiency" \
  --download-pdfs \
  --pdf-mode university_access \
  --year-range "2022-2024" \
  --max-results 70 \
  --pdf-dir "perovskite_solar" \
  --output perovskite_solar.json
```

### 6. Practical Workflows

#### Getting Started (No University Access)
```bash
# Start with open access papers only
uv run python online_literature_search.py "machine learning medical diagnosis" \
  --download-pdfs \
  --years-back 2 \
  --max-results 25 \
  --output ml_diagnosis_start.json

# Check what you got, then expand search
uv run python online_literature_search.py "machine learning medical diagnosis" \
  --download-pdfs \
  --month-range "2022-01-2024-12" \
  --max-results 75 \
  --pdf-dir "ml_diagnosis_expanded" \
  --output ml_diagnosis_full.json
```

#### University Research Workflow
```bash
# Step 1: Quick exploration (last year only)
uv run python online_literature_search.py "CRISPR gene editing safety" \
  --download-pdfs \
  --pdf-mode university_access \
  --years-back 1 \
  --max-results 30 \
  --pdf-dir "crispr_recent" \
  --output crispr_2024.json

# Step 2: Comprehensive historical search
uv run python online_literature_search.py "CRISPR gene editing safety" \
  --download-pdfs \
  --pdf-mode university_access \
  --year-range "2020-2023" \
  --max-results 100 \
  --pdf-dir "crispr_historical" \
  --output crispr_2020_2023.json

# Step 3: Very recent developments (month-level)
uv run python online_literature_search.py "CRISPR gene editing safety adverse events" \
  --download-pdfs \
  --pdf-mode university_access \
  --month-range "2024-06-2024-12" \
  --max-results 50 \
  --pdf-dir "crispr_latest" \
  --output crispr_latest_2024.json
```

#### Large Scale Systematic Review
```bash
# Break into manageable chunks by year
for year in 2020 2021 2022 2023 2024; do
  echo "Searching year: $year"
  uv run python online_literature_search.py "systematic review machine learning healthcare" \
    --download-pdfs \
    --pdf-mode university_access \
    --year-range "$year-$year" \
    --max-results 100 \
    --pdf-dir "systematic_review_${year}" \
    --output "systematic_review_${year}.json"
  sleep 10  # Rate limiting
done
```

## Command Line Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `query` | - | Required | Search query/topic |
| `--years-back` | `-y` | 10 | How many years back to search |
| `--year-range` | `-r` | None | Specific years like '2018-2020' or '2019' |
| `--month-range` | `-m` | None | Month ranges like '2025-01-2025-06' (helps with API limits) |
| `--output` | `-o` | None | Output JSON file path |
| `--max-results` | `-n` | 20 | Maximum number of results |

**Time filtering options are mutually exclusive** - use only one per search.

## Output Format

The tool exports results in structured JSON format:

```json
{
  "search_query": "west nile virus prediction",
  "years_back": null,
  "search_period": "2025-01-2025-06",
  "api_source": "semantic_scholar",
  "total_results": 25,
  "search_date": "2025-01-15T10:30:00.123456",
  "papers": [
    {
      "publish_year": "2025",
      "title": "AI for Early Warning of West Nile Virus Outbreaks",
      "journal": "Nature Communications",
      "doi": null,
      "authors": ["Dr. Jane Smith", "Prof. John Doe"],
      "abstract": "This paper presents a machine learning approach...",
      "url": "https://semanticscholar.org/paper/..."
    }
  ],
  "pdf_downloads": {
    "enabled": true,
    "mode": "open_access",
    "directory": "pdfs_west_nile_virus_pre",
    "statistics": {
      "total_attempts": 25,
      "successful_downloads": 12,
      "open_access_found": 12,
      "university_access_used": 0,
      "failed_downloads": 13
    }
  }
}
```

## API Limits and Considerations

### Current Limits
- **Semantic Scholar**: 100 papers per request without API key
- **Rate limiting**: Built-in delays and retry logic

### Getting More Papers
1. **Use month ranges** to break down searches and stay within limits
2. **Multiple searches** with different year ranges
3. **Progressive searches** from recent to historical

### Working with Month Ranges (Recommended for API Limits)
```bash
# Break down 2024 into 6-month chunks
uv run python online_literature_search.py "AI healthcare" --month-range "2024-01-2024-06" --output ai_h1_2024.json
uv run python online_literature_search.py "AI healthcare" --month-range "2024-07-2024-12" --output ai_h2_2024.json

# Search specific quarters
uv run python online_literature_search.py "climate modeling" --month-range "2024-01-2024-03" --output climate_q1.json
uv run python online_literature_search.py "climate modeling" --month-range "2024-04-2024-06" --output climate_q2.json

# Search single months for very active research areas  
uv run python online_literature_search.py "COVID-19" --month-range "2024-01-2024-01" --output covid_jan2024.json
```

### Rate Limiting
- Tool automatically waits 1 second between requests
- Handles 429 rate limit errors with automatic retry
- Saves progress incrementally to prevent data loss

## Advanced Usage

### Batch Processing Multiple Topics
```bash
# Create a script for multiple searches
#!/bin/bash
topics=("machine learning healthcare" "deep learning medical imaging" "AI drug discovery")
for topic in "${topics[@]}"; do
  echo "Searching: $topic"
  uv run python online_literature_search.py "$topic" \
    --month-range "2024-01-2024-06" \
    --max-results 100 \
    --output "${topic// /_}_h1_2024.json"
  sleep 5  # Respect rate limits
done
```

### Python API Usage
```python
from online_literature_search import OnlineLiteratureSearchAgent

# Create agent
agent = OnlineLiteratureSearchAgent()

# Basic search
results = agent.search_literature(
    query="quantum computing algorithms",
    years_back=5,
    max_results=50
)

# Search with specific years
results = agent.search_literature(
    query="climate change prediction",
    start_year=2020,
    end_year=2024,
    max_results=100
)

# Export to JSON
json_output = agent.search_and_export_json(
    query="renewable energy storage",
    years_back=3,
    output_file="energy_storage.json",
    max_results=75
)

# Search with PDF downloads
json_output = agent.search_and_export_json(
    query="machine learning medical imaging",
    years_back=2,
    max_results=30,
    download_pdfs=True,
    pdf_mode="university_access",
    pdf_dir="ml_medical_papers"
)
```

## Progress Tracking

The tool shows real-time progress during searches:

```
Searching for papers from 2025 to 2025...
Enhanced query with academic keywords
Enhanced query: west nile virus prediction forecasting epidemiology surveillance modeling
Searching Semantic Scholar database...
Processing 20 papers from Semantic Scholar...
Processed 1/20 papers
Processed 2/20 papers
Processed 3/20 papers
Processed 4/20 papers
Processed 5/20 papers
✓ Saved 5 papers to file
...
Found 20 papers from Semantic Scholar
Results saved to: results.json
```

## Command Line Reference

### Basic Options
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `query` | - | - | Search query (required) |
| `--years-back` | `-y` | 10 | Years back from current year |
| `--year-range` | `-r` | None | Specific years like '2020-2024' |
| `--month-range` | `-m` | None | Month ranges like '2025-01-2025-06' |
| `--max-results` | `-n` | 20 | Maximum number of results (up to 100) |
| `--output` | `-o` | None | Output JSON file path |

### PDF Download Options
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--download-pdfs` | - | False | Enable PDF downloading |
| `--pdf-mode` | - | open_access | Mode: open_access or university_access |
| `--pdf-dir` | - | Auto | Directory for PDF downloads |

**Time filtering options are mutually exclusive** - use only one per search.

## Troubleshooting

### Common Issues

#### Ollama/LLM Enhancement Problems
```bash
# Check if Ollama is running
ollama list

# If model is not found, pull it
ollama pull qwen2.5:3b

# If Ollama service is not running
ollama serve

# Test the model directly
ollama run qwen2.5:3b "Hello, how are you?"

# Check Ollama logs (Linux/macOS)
journalctl -u ollama -f
# Or check ~/.ollama/logs/
```

**Common Ollama Issues:**
- **Model not found**: Run `ollama pull qwen2.5:3b`
- **Connection refused**: Start Ollama service with `ollama serve`
- **Slow responses**: Model is loading, wait a few minutes
- **Memory issues**: qwen2.5:3b requires ~2GB RAM

#### API Rate Limits
```bash
# Use month ranges to stay under Semantic Scholar limits (100 papers max)
uv run python online_literature_search.py "your query" --month-range "2024-01-2024-06"

# Break large searches into smaller time periods
uv run python online_literature_search.py "your query" --month-range "2024-01-2024-03"
uv run python online_literature_search.py "your query" --month-range "2024-04-2024-06"
```

#### Empty Results
- Try broader search terms
- Check year/month ranges are valid
- Verify internet connection
- Check if LLM query enhancement is working

#### Month Range Format Issues
```bash
# Correct format
--month-range "2025-01-2025-06"

# Incorrect formats
--month-range "2025-1-2025-6"     # Missing leading zeros
--month-range "2025/01/2025/06"   # Wrong separators
--month-range "Jan-2025-Jun-2025" # Use numbers, not names
```

### Error Recovery
- Tool automatically skips problematic papers
- Incremental saves prevent data loss
- Progress indicators show real-time status
- Detailed error messages for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Citation

If you use this tool in your research, please cite:
```bibtex
@software{research_paper_search_agent,
  title={Research Paper Search Agent},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/research_paper_search_agent}
}
```

## Support

- Check the troubleshooting section above
- Review command line options with `--help`
- Ensure all prerequisites are installed
- Verify Ollama and qwen3 model are working

For issues or feature requests, please open a GitHub issue.