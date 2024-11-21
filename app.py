def categorize_url(url, us_cities):
    url = url.lower()

    # 0. Homepage
    if url.endswith("/") or re.fullmatch(r"https?://[^/]+/?", url):
        return "CMS Pages"

    # 1. Blog Filters
    if re.search(r'/tag|/category', url):
        return "Blog Filters"

    # 2. Blog Pages
    if re.search(r'/blog', url) and not re.search(r'/page|/author', url):
        return "Blog Pages"

    # 3. Pagination
    if re.search(r'/page/\d+', url):
        return "Pagination"

    # 4. Agent Pages
    if re.search(r'/agent|/team', url):
        return "Agent Pages"

    # 5. Property Pages
    if re.search(r'/properties|/property|/listings|/rentals', url) and not re.search(r'/page', url):
        return "Property Pages"

    # 6. Parameters
    if re.search(r'\?.+=', url):
        return "Parameters"

    # 7. CMS Pages (Contact, Testimonials, About, etc.)
    if re.search(r'/contact|/about|/testimonials|/privacy|/tos|/terms|/resources|/sell|/purchase|/films', url):
        return "CMS Pages"

    # 8. Neighborhood Pages (Detect City Names)
    if (
        any(city in url for city in us_cities) and
        not re.search(r'/blog|/properties|/property|/listings|/agent|/team|/contact|/about|/testimonials|/privacy|/tos|/terms|/resources|/sell|/purchase|/films', url)
    ):
        return "Neighborhood Pages"

    # Fallback to CMS Pages if uncategorized
    return "CMS Pages"
