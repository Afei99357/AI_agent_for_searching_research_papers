import json
import requests
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import argparse
import ollama
from pdf_downloader import PDFDownloader


@dataclass
class OnlineLiteratureResult:
    """Structure for online literature search result"""
    publish_year: Optional[str]
    title: str
    journal: Optional[str]
    doi: Optional[str] = None
    authors: Optional[List[str]] = None
    abstract: Optional[str] = None
    url: Optional[str] = None


class OnlineLiteratureSearchAgent:
    """Agent for searching online peer-reviewed literature using Semantic Scholar"""
    
    def __init__(self):
        self.semantic_scholar_base = "https://api.semanticscholar.org/graph/v1"
        self.llm_model = "qwen3:latest"
    
    def _save_incremental_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save incremental results to prevent data loss"""
        search_info = {
            "search_query": "Incremental save",
            "years_back": 0,
            "search_period": "ongoing",
            "api_source": "semantic_scholar",
            "total_results": len(results),
            "search_date": datetime.now().isoformat(),
            "papers": results
        }
        
        json_output = json.dumps(search_info, indent=2, ensure_ascii=False)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        
    def search_literature(
        self, 
        query: str, 
        years_back: int = 10, 
        max_results: int = 20,
        output_file: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for peer-reviewed literature using Semantic Scholar
        
        Args:
            query: Search query/context
            years_back: How many years back to search (default: 10)
            max_results: Maximum number of results (up to 100 without API key)
            output_file: Output file for incremental saves
            start_year: Specific start year (overrides years_back)
            end_year: Specific end year (overrides years_back)
            
        Returns:
            List of dictionaries with publication metadata
        """
        # Use specific years if provided, otherwise calculate from years_back
        if start_year is not None and end_year is not None:
            search_start = start_year
            search_end = end_year
        else:
            current_year = datetime.now().year
            search_start = current_year - years_back
            search_end = current_year
        
        print(f"Searching for papers from {search_start} to {search_end}...")
        
        # Use qwen3 to enhance the search query
        enhanced_query = self._enhance_query_with_llm(query)
        
        return self._search_semantic_scholar(enhanced_query, search_start, search_end, max_results, output_file)
    
    def _enhance_query_with_llm(self, query: str) -> str:
        """Use qwen3 to enhance the search query for better academic search results"""
        try:
            prompt = f"""Create a precise academic search query for scientific databases.

Original query: "{query}"

Generate a focused search query by:
1. Keep main scientific concepts from the original
2. Add 2-3 specific technical terms from peer-reviewed literature  
3. Include research methodology keywords (modeling, analysis, epidemiology, surveillance)
4. Use academic terminology found in paper titles/abstracts
5. Avoid broad common words that match irrelevant content

Examples:
"west nile virus prediction" → "west nile virus epidemic modeling forecasting surveillance"
"cancer treatment efficacy" → "cancer therapy treatment outcomes clinical efficacy"
"climate modeling" → "climate modeling atmospheric simulation weather prediction"

Return only the enhanced search query (under 80 characters):"""
            
            response = ollama.generate(
                model=self.llm_model,
                prompt=prompt,
                options={"temperature": 0.1}  # Very low temperature for consistency
            )
            
            enhanced = response['response'].strip().strip('"').strip("'")
            
            # Clean up any thinking tags or extra text
            if '<think>' in enhanced or '</think>' in enhanced:
                print("LLM returned thinking process, using original query")
                return query
            
            # If response is too long or contains unusual characters, use original
            if len(enhanced) > 100 or any(char in enhanced for char in ['<', '>', '\n\n']):
                print("LLM response too long or malformed, using original query")
                return query
            
            # If enhanced query is significantly different or empty, use original
            if not enhanced or len(enhanced) < len(query):
                print("LLM response invalid, using original query")
                return query
            
            print(f"Enhanced query: {enhanced}")
            return enhanced
            
        except Exception as e:
            print(f"Error enhancing query with LLM: {e}")
            return query
    
    def _search_semantic_scholar(
        self, 
        query: str,
        start_year: int,
        end_year: int, 
        max_results: int,
        output_file: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search using Semantic Scholar API"""
        
        params = {
            "query": query,
            "year": f"{start_year}:{end_year}",
            "limit": min(max_results, 100),  # API limit without key
            "fields": "title,year,authors,journal,abstract,url"
        }
        
        try:
            print(f"Searching Semantic Scholar database...")
            print(f"Note: Using free access - up to {min(max_results, 100)} papers per search")
            
            response = requests.get(f"{self.semantic_scholar_base}/paper/search", 
                                    params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            papers = data.get("data", [])
            
            results = []
            for i, paper in enumerate(papers):
                try:
                    # Extract authors
                    authors = []
                    if paper.get("authors"):
                        authors = [author.get("name", "") for author in paper["authors"]]
                    
                    # Extract journal name
                    journal = ""
                    if paper.get("journal"):
                        journal = paper["journal"].get("name", "")
                    
                    result = {
                        "publish_year": str(paper.get("year", "")),
                        "title": paper.get("title", ""),
                        "journal": journal,
                        "doi": None,  # DOI not available from Semantic Scholar API
                        "authors": authors,
                        "abstract": paper.get("abstract"),
                        "url": paper.get("url")
                    }
                    
                    results.append(result)
                    
                    # Show progress every paper
                    print(f"Processed {len(results)}/{len(papers)} papers")
                    
                    # Save incrementally every 5 papers
                    if output_file and len(results) % 5 == 0:
                        self._save_incremental_results(results, output_file)
                        print(f"✓ Saved {len(results)} papers to file")
                        
                except Exception as e:
                    print(f"✗ Error processing paper {i+1}: {e}, skipping...")
                    continue
            
            print(f"Found {len(results)} papers from Semantic Scholar")
            return results
            
        except requests.RequestException as e:
            print(f"Error querying Semantic Scholar: {e}")
            return []
        except Exception as e:
            print(f"Error processing Semantic Scholar response: {e}")
            return []
    
    def search_and_export_json(
        self, 
        query: str, 
        years_back: int = 10,
        output_file: Optional[str] = None, 
        max_results: int = 20,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        download_pdfs: bool = False,
        pdf_mode: str = "open_access",
        pdf_dir: Optional[str] = None
    ) -> str:
        """
        Search literature and export results to JSON format
        
        Args:
            query: Search query
            years_back: How many years back to search
            output_file: Output file path
            max_results: Maximum number of results
            start_year: Specific start year
            end_year: Specific end year
            download_pdfs: Whether to download PDFs
            pdf_mode: "open_access" or "university_access"
            pdf_dir: Directory for PDF downloads
            
        Returns:
            JSON string with search results and metadata
        """
        results = self.search_literature(query, years_back, max_results, output_file, start_year, end_year)
        
        # Download PDFs if requested
        pdf_results = None
        if download_pdfs and results:
            print(f"\nDownloading PDFs using {pdf_mode} mode...")
            
            # Set up PDF directory
            if pdf_dir is None:
                pdf_dir = f"pdfs_{query.replace(' ', '_')[:20]}"
            
            downloader = PDFDownloader(download_dir=pdf_dir, mode=pdf_mode)
            pdf_results = downloader.download_papers(results)
            
            print(f"\nPDF Download Summary:")
            print(f"  Total attempts: {pdf_results['statistics']['total_attempts']}")
            print(f"  Successful: {pdf_results['statistics']['successful_downloads']}")
            print(f"  Open access: {pdf_results['statistics']['open_access_found']}")
            if pdf_mode == "university_access":
                print(f"  University access: {pdf_results['statistics']['university_access_used']}")
            print(f"  Failed: {pdf_results['statistics']['failed_downloads']}")
            print(f"  PDFs saved to: {pdf_results['download_directory']}")
            
            # Show common failure reasons if there are failures
            if pdf_results['statistics']['failed_downloads'] > 0:
                failed_papers = [r for r in pdf_results['results'] if r['status'] == 'failed']
                if failed_papers:
                    failure_reasons = {}
                    for paper in failed_papers:
                        reasons = paper.get('failure_reasons', 'Unknown error')
                        # Group similar errors
                        for reason in reasons.split(';'):
                            reason = reason.strip()
                            if reason:
                                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                    
                    print(f"\nCommon failure reasons:")
                    for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True):
                        print(f"  • {reason}: {count} papers")
            
            # Save detailed PDF report
            if output_file:
                pdf_report_file = output_file.replace('.json', '_pdf_report.json')
                downloader.save_download_report(pdf_results, pdf_report_file)
                print(f"  PDF report saved to: {pdf_report_file}")
        
        # Calculate search period for metadata
        if start_year is not None and end_year is not None:
            search_period = f"{start_year}-{end_year}"
            years_back_used = None
        else:
            current_year = datetime.now().year
            search_period = f"{current_year - years_back}-{current_year}"
            years_back_used = years_back
        
        # Add search metadata
        search_info = {
            "search_query": query,
            "years_back": years_back_used,
            "search_period": search_period,
            "api_source": "semantic_scholar",
            "total_results": len(results),
            "search_date": datetime.now().isoformat(),
            "papers": results
        }
        
        # Add PDF information if PDFs were downloaded
        if pdf_results:
            search_info["pdf_downloads"] = {
                "enabled": True,
                "mode": pdf_mode,
                "directory": pdf_results["download_directory"],
                "statistics": pdf_results["statistics"]
            }
        
        # Convert to JSON
        json_output = json.dumps(search_info, indent=2, ensure_ascii=False)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"Results saved to: {output_file}")
        
        return json_output


def main():
    """Command line interface for online literature search"""
    parser = argparse.ArgumentParser(description="Search online peer-reviewed literature using Semantic Scholar")
    parser.add_argument("query", help="Search query/context")
    parser.add_argument("--years-back", "-y", type=int, default=10, 
                       help="How many years back to search (default: 10, used if no other time option specified)")
    parser.add_argument("--year-range", "-r", type=str, 
                       help="Specific year range like '2020-2025'")
    parser.add_argument("--month-range", "-m", type=str, 
                       help="Specific month range like '2025-01-2025-06'")
    parser.add_argument("--max-results", "-n", type=int, default=20, 
                       help="Maximum results (default: 20, up to 100 without API key)")
    parser.add_argument("--output", "-o", type=str, 
                       help="Output file (saves JSON results)")
    
    # PDF downloading options
    parser.add_argument("--download-pdfs", action="store_true",
                       help="Download PDFs of found papers")
    parser.add_argument("--pdf-mode", choices=["open_access", "university_access"], 
                       default="open_access",
                       help="PDF download mode: open_access (free only) or university_access (try all sources)")
    parser.add_argument("--pdf-dir", type=str,
                       help="Directory for PDF downloads (auto-generated if not specified)")
    
    args = parser.parse_args()
    
    # Parse time range - only one option allowed
    start_year = None
    end_year = None
    
    # Check for conflicting options
    options_provided = sum([
        bool(args.month_range),
        bool(args.year_range),
        args.years_back != 10  # Only count if user explicitly changed from default
    ])
    
    if options_provided > 1:
        print("Error: Please specify only one time filtering option:")
        print("  --years-back (-y) for relative time")
        print("  --year-range (-r) for specific years")
        print("  --month-range (-m) for specific months")
        return
    
    if args.month_range:
        # Parse month range like "2025-01-2025-06" or "2024-03-2024-03"
        try:
            parts = args.month_range.split('-')
            if len(parts) == 4:  # YYYY-MM-YYYY-MM format splits into 4 parts
                start_year = int(parts[0])
                start_month = int(parts[1])
                end_year = int(parts[2])
                end_month = int(parts[3])
                
                # Validate month values
                if not (1 <= start_month <= 12) or not (1 <= end_month <= 12):
                    print(f"Invalid month values: months must be 01-12")
                    return
                
                print(f"Searching papers from {start_year}-{start_month:02d} to {end_year}-{end_month:02d}")
            else:
                print(f"Invalid month range format: {args.month_range}. Use format like '2025-01-2025-06'")
                return
        except ValueError:
            print(f"Invalid month range format: {args.month_range}. Use format like '2025-01-2025-06'")
            return
    elif args.year_range:
        # Parse year range like "2020-2025"
        try:
            start_year, end_year = map(int, args.year_range.split('-'))
            print(f"Searching papers from {start_year} to {end_year}")
        except ValueError:
            print(f"Invalid year range format: {args.year_range}. Use format like '2020-2025'")
            return
    else:
        # Use years_back (default behavior)
        print(f"Searching papers from last {args.years_back} years")
    
    # Create search agent and perform search
    agent = OnlineLiteratureSearchAgent()
    
    try:
        result_json = agent.search_and_export_json(
            query=args.query,
            years_back=args.years_back,
            output_file=args.output,
            max_results=args.max_results,
            start_year=start_year,
            end_year=end_year,
            download_pdfs=args.download_pdfs,
            pdf_mode=args.pdf_mode,
            pdf_dir=args.pdf_dir
        )
        
        # Print summary if no output file specified
        if not args.output:
            print("\n--- Search Results Summary ---")
            data = json.loads(result_json)
            print(f"Query: {data['search_query']}")
            print(f"Period: {data['search_period']}")
            print(f"Papers found: {data['total_results']}")
            
    except Exception as e:
        print(f"Error during search: {e}")


if __name__ == "__main__":
    main()