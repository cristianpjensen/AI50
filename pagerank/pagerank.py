import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = {}

    # Add all the pages in corpus to the distribution.
    for p in corpus:
        distribution[p] = 0

    links = corpus[page]
    num_links = len(links)
    num_pages = len(distribution)

    # Distribute the damping factor over the links that the page links to.
    for p in links:
        distribution[p] += (damping_factor / num_links)

    # Distribute 1 - damping_factor over all pages.
    for p in distribution:
        # If page doesn't link to any other pages, distribute 1 over all
        # pages, since damping_factor hasn't been distributed yet.
        if num_links == 0:
            distribution[p] += (1 / num_pages) 
        else:
            distribution[p] += ((1 - damping_factor) / num_pages)

    return distribution
     

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {}
    samples = []
    num_pages = len(corpus)

    # Generate first sample.
    page = random.choice(list(corpus.keys()))
    samples.append(page)

    # The remaining samples, based on the probability distrubition of the
    # previous sample.
    while len(samples) <= n:
        distribution = transition_model(corpus, page, damping_factor)
        page = choice(distribution)
        samples.append(page)

    # Add the pagerank to each page by dividing the count in samples by n.
    for p in corpus:
        pagerank[p] = samples.count(p) / n

    return pagerank


def choice(distribution):
    population = []
    weights = []

    # Add all the possible choices to the population.
    for page in distribution:
        population.append(page)

    # Add the probabilities to the weights.
    for probability in distribution.values():
        weights.append(probability)

    # Generate a page, based on the probability distribution.
    page = random.choices(population, weights, k=1).pop()

    return page


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {}
    N = len(corpus)

    # Set the initial ranks; 1 distributed over all pages.
    for p in corpus:
        pagerank[p] = 1 / N

    while True:
        # Keep the previous pagerank, which won't update.
        prev_pagerank = pagerank.copy()

        for p in pagerank:
            changes = []
            i = []
            sum_i = 0

            # Check for which pages, p is in the links.
            for key, links in corpus.items():
                if p in links:
                    i.append(key)

            # Compute the sum of PR(i) / NumLinks(i).
            for page in i:
                sum_i += prev_pagerank[page] / len(corpus[page])

            pagerank[p] = ((1 - damping_factor) / N) + (damping_factor * sum_i)
            changes.append(abs(prev_pagerank[p] - pagerank[p]))

        # Check if the threshold is met.
        if all(change < 0.001 for change in changes):
            return pagerank


if __name__ == "__main__":
    main()
