from utils import *



class tools:
    def __init__(self):
        a=1

    def get_user_profile(self,author_name):

        author_query = author_name.replace(" ", "+")
        url = f"http://export.arxiv.org/api/query?search_query=au:{author_query}&start=0&max_results=300"  # Adjust max_results if needed

        response = requests.get(url)
        papers_list = []

        if response.status_code == 200:
            root = ElementTree.fromstring(response.content)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')

            total_papers = 0
            data_to_save = []

            papers_by_year = {}

            for entry in entries:

                title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
                published = entry.find('{http://www.w3.org/2005/Atom}published').text.strip()
                abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                authors_elements = entry.findall('{http://www.w3.org/2005/Atom}author')
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors_elements]
                link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()  # Get the paper link

                # Check if the specified author is exactly in the authors list
                if author_name in authors:
                    # Remove the specified author from the coauthors list for display
                    coauthors = [author for author in authors if author != author_name]
                    coauthors_str = ", ".join(coauthors)

                    papers_list.append({
                        "date": published,
                        "Title & Abstract": f"{title}; {abstract}",
                        "coauthors": coauthors_str,
                        "link": link  # Add the paper link to the dictionary
                    })
                authors_elements = entry.findall('{http://www.w3.org/2005/Atom}author')
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors_elements]

                if author_name in authors:
                    # print(author_name)
                    # print(authors)
                    total_papers += 1
                    published_date = entry.find('{http://www.w3.org/2005/Atom}published').text.strip()
                    date_obj = datetime.datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ')

                    year = date_obj.year
                    if year not in papers_by_year:
                        papers_by_year[year] = []
                    papers_by_year[year].append(entry)

            if total_papers > 40:
                for cycle_start in range(min(papers_by_year), max(papers_by_year) + 1, 5):
                    cycle_end = cycle_start + 4
                    for year in range(cycle_start, cycle_end + 1):
                        if year in papers_by_year:
                            selected_papers = papers_by_year[year][:2]
                            for paper in selected_papers:
                                title = paper.find('{http://www.w3.org/2005/Atom}title').text.strip()
                                abstract = paper.find('{http://www.w3.org/2005/Atom}summary').text.strip()
                                authors_elements = paper.findall('{http://www.w3.org/2005/Atom}author')
                                co_authors = [author.find('{http://www.w3.org/2005/Atom}name').text for author in
                                              authors_elements if
                                              author.find('{http://www.w3.org/2005/Atom}name').text != author_name]

                                papers_list.append({
                                    "Author": author_name,
                                    "Title & Abstract": f"{title}; {abstract}",
                                    "Date Period": f"{year}",
                                    "Cycle": f"{cycle_start}-{cycle_end}",
                                    "Co_author": ", ".join(co_authors)
                                })

            # Trim the list to the 10 most recent papers
            papers_list = papers_list[:10]

            personal_info = "; ".join([f"{details['Title & Abstract']}" for details in papers_list])

            info = summarize_research_direction(personal_info)

            return info

            # data = {author_name: {"paper_{}".format(i+1): paper for i, paper in enumerate(papers_list)}}

        else:
            print("Failed to fetch data from arXiv.")
            return ""




    def get_recent_paper(self,num,domain):
        data_collector = []
        keywords = dict()
        keywords[domain] = domain

        for topic, keyword in keywords.items():
            # print("Keyword: " + topic)
            data, _ = get_daily_papers(topic, query=keyword, max_results=num)
            data_collector.append(data)
        data_dict={}
        for data in data_collector:
            for time in data.keys():
                papers = data[time]
                # print(papers.published)
                data_dict[time.strftime("%m/%d/%Y")] = papers

        return data_dict

    def idea_generation(self, profile,papers,domain):

        time_chunks_embed = {}
        dataset = papers
        for time in dataset.keys():
            papers = dataset[time]['abstract']
            papers_embedding = get_bert_embedding(papers)
            time_chunks_embed[time] = papers_embedding

        self.trend, paper_link = summarize_research_field(profile, domain, dataset,
                                                          time_chunks_embed)  # trend
        self.idea = generate_ideas(self.trend)  # idea


        return self.idea