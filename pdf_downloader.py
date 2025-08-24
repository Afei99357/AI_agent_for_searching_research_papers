import os
import re
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm
import json


class PDFDownloader:
    """
    PDF downloader with support for open access and university-access modes
    """
    
    def __init__(self, download_dir: str = "downloaded_papers", mode: str = "open_access"):
        """
        Initialize PDF downloader
        
        Args:
            download_dir: Directory to save PDFs
            mode: "open_access" (only free papers) or "university_access" (try all sources)
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.mode = mode
        self.session = requests.Session()
        
        # Set reasonable headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Track download statistics
        self.stats = {
            "total_attempts": 0,
            "successful_downloads": 0,
            "open_access_found": 0,
            "university_access_used": 0,
            "failed_downloads": 0
        }
    
    def download_papers(self, papers: List[Dict], progress_callback=None) -> Dict:
        """
        Download PDFs for a list of papers
        
        Args:
            papers: List of paper dictionaries from search results
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary with download results and statistics
        """
        results = []
        
        with tqdm(total=len(papers), desc="Downloading PDFs") as pbar:
            for i, paper in enumerate(papers):
                self.stats["total_attempts"] += 1
                
                # Create safe filename from title
                safe_title = self._create_safe_filename(paper.get("title", "unknown"))
                year = paper.get("publish_year", "unknown")
                filename = f"{year}_{safe_title}.pdf"
                filepath = self.download_dir / filename
                
                # Skip if already downloaded
                if filepath.exists():
                    results.append({
                        "paper": paper,
                        "status": "already_exists",
                        "filepath": str(filepath),
                        "source": "local"
                    })
                    pbar.update(1)
                    continue
                
                # Try to download
                download_result = self._download_single_paper(paper, filepath)
                results.append(download_result)
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, len(papers), download_result)
                
                pbar.set_description(f"Downloaded: {self.stats['successful_downloads']}/{self.stats['total_attempts']}")
                pbar.update(1)
                
                # Rate limiting
                time.sleep(1)
        
        return {
            "results": results,
            "statistics": self.stats,
            "download_directory": str(self.download_dir)
        }
    
    def _download_single_paper(self, paper: Dict, filepath: Path) -> Dict:
        """Download a single paper PDF"""
        
        # Extract identifiers
        title = paper.get("title", "")
        doi = paper.get("doi")
        url = paper.get("url")
        
        # Try different download strategies
        download_sources = []
        
        # 1. Check arXiv first (always free)
        arxiv_url = self._check_arxiv(title)
        if arxiv_url:
            download_sources.append(("arxiv", arxiv_url))
        
        # 2. Check Unpaywall for open access
        if doi:
            unpaywall_url = self._check_unpaywall(doi)
            if unpaywall_url:
                download_sources.append(("unpaywall", unpaywall_url))
        
        # 3. Try PubMed Central
        pmc_url = self._check_pubmed_central(title, doi)
        if pmc_url:
            download_sources.append(("pmc", pmc_url))
        
        # 4. If university access mode, try publisher direct
        if self.mode == "university_access":
            if doi:
                publisher_url = f"https://doi.org/{doi}"
                download_sources.append(("publisher", publisher_url))
            elif url:
                download_sources.append(("direct", url))
        
        # Try each source
        for source_name, source_url in download_sources:
            try:
                success = self._download_from_url(source_url, filepath, source_name)
                if success:
                    self.stats["successful_downloads"] += 1
                    if source_name in ["arxiv", "unpaywall", "pmc"]:
                        self.stats["open_access_found"] += 1
                    else:
                        self.stats["university_access_used"] += 1
                    
                    return {
                        "paper": paper,
                        "status": "downloaded",
                        "filepath": str(filepath),
                        "source": source_name,
                        "url": source_url
                    }
            except Exception as e:
                continue
        
        # No successful download
        self.stats["failed_downloads"] += 1
        return {
            "paper": paper,
            "status": "failed",
            "filepath": None,
            "source": None,
            "attempted_sources": [s[0] for s in download_sources]
        }
    
    def _download_from_url(self, url: str, filepath: Path, source: str) -> bool:
        """Download PDF from URL with different strategies based on source"""
        
        if source == "arxiv":
            return self._download_arxiv_pdf(url, filepath)
        elif source == "publisher":
            return self._download_publisher_pdf(url, filepath)
        else:
            return self._download_direct_pdf(url, filepath)
    
    def _download_direct_pdf(self, url: str, filepath: Path) -> bool:
        """Direct PDF download"""
        try:
            response = self.session.get(url, timeout=30)
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' not in content_type and not url.endswith('.pdf'):
                # Try to find PDF link on page
                soup = BeautifulSoup(response.content, 'html.parser')
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))
                if pdf_links:
                    pdf_url = urljoin(url, pdf_links[0]['href'])
                    response = self.session.get(pdf_url, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # Verify it's a valid PDF
                if self._is_valid_pdf(filepath):
                    return True
                else:
                    filepath.unlink()  # Delete invalid file
                    return False
            
        except Exception as e:
            return False
        
        return False
    
    def _download_arxiv_pdf(self, url: str, filepath: Path) -> bool:
        """Download PDF from arXiv"""
        try:
            # Convert arXiv URL to PDF URL if needed
            if 'arxiv.org/abs/' in url:
                pdf_url = url.replace('/abs/', '/pdf/') + '.pdf'
            else:
                pdf_url = url
            
            response = self.session.get(pdf_url, timeout=30)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                if self._is_valid_pdf(filepath):
                    return True
                else:
                    filepath.unlink()
                    return False
        except Exception:
            return False
        
        return False
    
    def _download_publisher_pdf(self, url: str, filepath: Path) -> bool:
        """Download from publisher (works with university access)"""
        try:
            # First get the page
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for PDF download links (common patterns)
            pdf_selectors = [
                'a[href*=".pdf"]',
                'a[href*="pdf"]',
                'a.pdf-download',
                'a.download-pdf',
                '.pdf-link a',
                '[data-testid="pdf-link"]'
            ]
            
            for selector in pdf_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href:
                        pdf_url = urljoin(url, href)
                        try:
                            pdf_response = self.session.get(pdf_url, timeout=30)
                            if pdf_response.status_code == 200 and 'application/pdf' in pdf_response.headers.get('content-type', ''):
                                with open(filepath, 'wb') as f:
                                    f.write(pdf_response.content)
                                
                                if self._is_valid_pdf(filepath):
                                    return True
                                else:
                                    filepath.unlink()
                        except Exception:
                            continue
            
        except Exception:
            return False
        
        return False
    
    def _check_arxiv(self, title: str) -> Optional[str]:
        """Check if paper is available on arXiv"""
        try:
            # Search arXiv API
            search_url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'ti:"{title}"',
                'start': 0,
                'max_results': 5
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                # Parse XML response
                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.content)
                
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    entry_title = entry.find('{http://www.w3.org/2005/Atom}title')
                    if entry_title is not None and self._titles_similar(title, entry_title.text):
                        id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                        if id_elem is not None:
                            return id_elem.text.replace('/abs/', '/pdf/') + '.pdf'
        except Exception:
            pass
        
        return None
    
    def _check_unpaywall(self, doi: str) -> Optional[str]:
        """Check Unpaywall API for open access version"""
        try:
            url = f"https://api.unpaywall.org/v2/{doi}?email=researcher@university.edu"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('is_oa', False):
                    best_location = data.get('best_oa_location', {})
                    pdf_url = best_location.get('url_for_pdf')
                    if pdf_url:
                        return pdf_url
        except Exception:
            pass
        
        return None
    
    def _check_pubmed_central(self, title: str, doi: str = None) -> Optional[str]:
        """Check PubMed Central for free full text"""
        try:
            # Search PMC API
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'pmc',
                'term': title,
                'retmode': 'json',
                'retmax': 5
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                id_list = data.get('esearchresult', {}).get('idlist', [])
                
                if id_list:
                    # Get details for first result
                    pmc_id = id_list[0]
                    return f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/"
        except Exception:
            pass
        
        return None
    
    def _is_valid_pdf(self, filepath: Path) -> bool:
        """Check if downloaded file is a valid PDF"""
        try:
            if filepath.stat().st_size < 1024:  # Too small
                return False
            
            with open(filepath, 'rb') as f:
                header = f.read(4)
                return header == b'%PDF'
        except Exception:
            return False
    
    def _titles_similar(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar (simple comparison)"""
        # Normalize titles
        t1 = re.sub(r'[^\w\s]', '', title1.lower()).strip()
        t2 = re.sub(r'[^\w\s]', '', title2.lower()).strip()
        
        # Simple similarity check
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        intersection = words1.intersection(words2)
        similarity = len(intersection) / min(len(words1), len(words2))
        
        return similarity > 0.6
    
    def _create_safe_filename(self, title: str) -> str:
        """Create filesystem-safe filename from title"""
        # Remove/replace problematic characters
        safe = re.sub(r'[^\w\s-]', '', title)
        safe = re.sub(r'[-\s]+', '_', safe)
        
        # Limit length
        if len(safe) > 100:
            safe = safe[:100]
        
        return safe.strip('_')
    
    def get_statistics(self) -> Dict:
        """Get download statistics"""
        return self.stats.copy()
    
    def save_download_report(self, results: Dict, output_file: str):
        """Save detailed download report"""
        report = {
            "download_summary": results["statistics"],
            "download_directory": results["download_directory"],
            "detailed_results": results["results"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)