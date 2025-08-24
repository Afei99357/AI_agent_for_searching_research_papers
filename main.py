from online_literature_search import OnlineLiteratureSearchAgent
import sys


def main():
    """Main entry point for research paper search agent"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <search_query> [options]")
        print("Or run: python online_literature_search.py --help for detailed options")
        return
    
    # Simple interface - pass all args to the literature search tool
    query = " ".join(sys.argv[1:])
    
    agent = OnlineLiteratureSearchAgent()
    json_results = agent.search_and_export_json(query)
    
    print("\n" + "="*50)
    print("SEARCH RESULTS")
    print("="*50)
    print(json_results)


if __name__ == "__main__":
    main()
