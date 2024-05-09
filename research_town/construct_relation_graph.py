import arxiv
from tqdm import tqdm

from utils import *


def author_position(author, author_list):
    for ind, i in enumerate(author_list):
        if author.lower() == i.lower():
            return ind + 1

    return "NULL"


def co_author_frequency(author, author_list, co_authors):
    for ind, i in enumerate(author_list):
        if author.lower() == i.lower():
            continue
        if i in co_authors:
            co_authors[i] += 1
        else:
            co_authors[i] = 1

    return co_authors


def co_author_filter(co_authors, limit=5):
    co_author_list = []
    for k, v in co_authors.items():
        co_author_list.append([k, v])

    co_author_list.sort(reverse=True, key=lambda p: p[1])
    co_author_list = co_author_list[:limit]
    co_author_list = [c[0] for c in co_author_list]

    return co_author_list


def fetch_author_info(author):
    client = arxiv.Client()
    papers_info = []
    co_authors = dict()
    print("{} Fetching Author Info: {}".format(show_time(), author))
    search = arxiv.Search(query="au:{}".format(author), max_results=10)
    for result in tqdm(
        client.results(search), desc="Processing Author Papers", unit="Paper"
    ):
        if author not in ", ".join(author.name for author in result.authors):
            continue
        author_list = [author.name for author in result.authors]
        # author_pos = author_position(author, author_list)
        co_authors = co_author_frequency(author, author_list, co_authors)
        paper_info = {
            "url": result.entry_id,
            "title": result.title,
            "abstract": result.summary,
            "authors": ", ".join(author.name for author in result.authors),
            "published": str(result.published).split(" ")[0],
            "updated": str(result.updated).split(" ")[0],
            "primary_cat": result.primary_category,
            "cats": result.categories,
            # "author_pos": author_pos
        }
        # print(json.dumps(paper_info, indent=4))
        papers_info.append(paper_info)

    # papers_info.sort(reverse=False, key=lambda p: p["author_pos"])
    co_authors = co_author_filter(co_authors, limit=5)
    print(text_wrap("Num of Papers:"), len(papers_info))
    print(text_wrap("Num of Co-authors:"), len(co_authors))

    return papers_info, co_authors


def bfs(author_list, node_limit=20):
    graph = []
    node_feat = dict()
    edge_feat = dict()
    visit = []
    for author in author_list:
        if author in visit:
            continue
        papers_info, co_authors = fetch_author_info(author)
        if len(node_feat) <= node_limit:
            author_list.extend(co_authors)
            for co_au in co_authors:
                if (author, co_au) in graph or (co_au, author) in graph:
                    continue
                graph.append((author, co_au))

        visit.append(author)
        node_feat[author] = papers_info

    return graph, node_feat, edge_feat


if __name__ == "__main__":
    start_author = ["Jiaxuan You"]
    bfs(author_list=start_author, node_limit=20)
