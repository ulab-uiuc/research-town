import feedparser
from urllib.parse import urlencode, quote
from tqdm import tqdm

def search_arxiv(categories, query=None, max_results=50):
    """
    Search arXiv for papers in specified categories and an optional query.

    Args:
        categories (list): List of categories to filter papers (e.g., ['cs', 'econ']).
        query (str): Optional search query for additional filtering.
        max_results (int): Maximum number of results to fetch.

    Returns:
        list: List of papers with title, authors, summary, and link.
    """
    base_url = "http://export.arxiv.org/api/query?"

    # Construct the category filter
    category_filter = " AND ".join([f"cat:{cat}" for cat in categories])
    search_query = f"({category_filter})"
    if query:
        search_query += f" AND ({query})"

    # URL encode the query parameters
    encoded_query = urlencode({"search_query": search_query, "start": 0, "max_results": max_results, 
                                "sortBy": "submittedDate", "sortOrder": "descending"})

    # Construct the full URL
    url = f"{base_url}{encoded_query}"

    # Parse the response
    feed = feedparser.parse(url)
    papers = []
    for entry in feed.entries:
        paper = {
            "title": entry.title,
            "authors": [author.name for author in entry.authors],
            "summary": entry.summary,
            "link": entry.link,
            "published": entry.published,
        }
        papers.append(paper)
    return papers

arxiv_categories = [
    # Physics
    "astro-ph", "astro-ph.GA", "astro-ph.CO", "astro-ph.EP", "astro-ph.HE", "astro-ph.IM", "astro-ph.SR",
    "cond-mat", "cond-mat.dis-nn", "cond-mat.mes-hall", "cond-mat.mtrl-sci", "cond-mat.other",
    "cond-mat.quant-gas", "cond-mat.soft", "cond-mat.stat-mech", "cond-mat.str-el", "cond-mat.supr-con",
    "gr-qc", "hep-ex", "hep-lat", "hep-ph", "hep-th", "math-ph", "nlin.AO", "nlin.CG", "nlin.CD",
    "nlin.SI", "nlin.PS", "nucl-ex", "nucl-th", "physics.acc-ph", "physics.ao-ph", "physics.app-ph",
    "physics.atm-clus", "physics.atom-ph", "physics.bio-ph", "physics.chem-ph", "physics.class-ph",
    "physics.comp-ph", "physics.data-an", "physics.flu-dyn", "physics.gen-ph", "physics.geo-ph",
    "physics.hist-ph", "physics.ins-det", "physics.med-ph", "physics.optics", "physics.ed-ph",
    "physics.soc-ph", "physics.plasm-ph", "physics.pop-ph", "physics.space-ph",

    # Quantitative Biology
    "q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.OT", "q-bio.PE", "q-bio.QM",
    "q-bio.SC", "q-bio.TO",

    # Quantitative Finance
    "q-fin.CP", "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR", "q-fin.RM", "q-fin.ST",
    "q-fin.TR",

    # Economics
    "econ.EM", "econ.GN", "econ.TH"
]

links = []
for category in tqdm(arxiv_categories):
    # Example usage
    categories = ["cs.CL", category]
    query = "machine learning"  # Optional; use None if you don't have a specific query
    max_results = 20

    papers = search_arxiv(categories, query, max_results)

    # Display the papers
    for idx, paper in enumerate(papers):
        print(f"Paper {idx + 1}:")
        print(f"Title: {paper['title']}")
        links.append(paper['link'])

with open('cross_domain_arxiv_links.txt', 'a') as f:
    for link in links:
        f.write(f"{link}\n")