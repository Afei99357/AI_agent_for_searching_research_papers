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

## Prerequisites

### Required Software
- Python 3.13+
- [Ollama](https://ollama.com/) with qwen3:latest model
- UV package manager (or pip)

### Setup
```bash
# Install Ollama and pull the model
ollama pull qwen3:latest

# Install dependencies
uv sync
# or with pip
pip install requests ollama
```

## Quick Start

### Basic Usage
```bash
# Simple search (last 10 years, 20 results)
uv run python online_literature_search.py "machine learning healthcare"

# Save to file
uv run python online_literature_search.py "machine learning healthcare" --output results.json
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

### 3. Complex Research Scenarios

#### Systematic Literature Review
```bash
# Comprehensive search across multiple years
uv run python online_literature_search.py "systematic review meta-analysis" \
  --year-range "2020-2024" \
  --max-results 200 \
  --api crossref \
  --output systematic_review_papers.json
```

#### Trend Analysis Over Time
```bash
# Historical perspective (2000-2010)
uv run python online_literature_search.py "social media impact" \
  --year-range "2000-2010" \
  --output social_media_2000s.json

# Recent developments (2020-2024)
uv run python online_literature_search.py "social media impact" \
  --year-range "2020-2024" \
  --output social_media_2020s.json
```

#### Working Within API Limits Using Month Ranges
```bash
# Break down 2024 into quarters to stay under 100-paper limit
uv run python online_literature_search.py "AI healthcare" \
  --month-range "2024-01-2024-03" \
  --output ai_q1_2024.json

uv run python online_literature_search.py "AI healthcare" \
  --month-range "2024-04-2024-06" \
  --output ai_q2_2024.json

uv run python online_literature_search.py "AI healthcare" \
  --month-range "2024-07-2024-09" \
  --output ai_q3_2024.json

uv run python online_literature_search.py "AI healthcare" \
  --month-range "2024-10-2024-12" \
  --output ai_q4_2024.json
```

### 5. Domain-Specific Examples

#### Medical Research
```bash
# Epidemiological studies with month-level precision
uv run python online_literature_search.py "infectious disease modeling" \
  --month-range "2023-01-2023-12" \
  --max-results 100 \
  --output epidemiology.json

# Clinical trials from recent years
uv run python online_literature_search.py "randomized controlled trial diabetes" \
  --year-range "2020-2024" \
  --api crossref \
  --max-results 200 \
  --output diabetes_trials.json
```

#### Computer Science
```bash
# AI/ML research - recent developments
uv run python online_literature_search.py "transformer neural networks" \
  --month-range "2024-01-2024-06" \
  --max-results 100 \
  --output transformers_h1_2024.json

# Cybersecurity research
uv run python online_literature_search.py "zero-day vulnerability detection" \
  --year-range "2022-2024" \
  --max-results 75 \
  --output cybersecurity.json
```

#### Environmental Science
```bash
# Climate research with large dataset
uv run python online_literature_search.py "carbon sequestration forest" \
  --years-back 8 \
  --api crossref \
  --max-results 250 \
  --output carbon_sequestration.json

# Conservation biology - recent findings
uv run python online_literature_search.py "species extinction prediction" \
  --month-range "2024-01-2024-06" \
  --max-results 100 \
  --output extinction_prediction.json
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
  ]
}
```

## API Limits and Considerations

### Current Limits
- **Semantic Scholar**: 100 papers per request, 100 requests per 5 minutes
- **CrossRef**: 1000 papers per request, higher rate limits

### Getting More Papers
1. **Use CrossRef** for larger batches (up to 1000 papers)
2. **Use month ranges** to break down searches and stay within limits
3. **Multiple searches** with different year ranges

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

## Troubleshooting

### Common Issues

#### LLM Enhancement Problems
```bash
# If LLM enhancement fails, check Ollama status
ollama list
ollama pull qwen3:latest
```

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