import streamlit as st
import pandas as pd
import re

# Load US cities from the static file
@st.cache_data
def load_us_cities():
    us_cities_path = 'us_cities.csv'  # Adjust the path to match the location in the repo
    us_cities = pd.read_csv(us_cities_path)['city'].str.lower().tolist()
    return us_cities

# Helper function to detect US cities in a URL
def contains_us_city(url_slug, us_cities):
    for city in us_cities:
        if city in url_slug:
            return True
    return False

# Categorization logic
def categorize_urls(urls, us_cities):
    categories = []
    for url in urls:
        url_slug = url.lower()

        # Rule: Homepage
        if url_slug in ['/', '/index', '/home']:
            categories.append("CMS Pages")
            continue

        # Rule: Properties
        if any(keyword in url_slug for keyword in ['/rentals', '/properties', '/homes-for-sale']):
            categories.append("Property Pages")
            continue

        # Rule: MLS Pages
        if len(url_slug.strip('/').split('/')) <= 2 and any(keyword in url_slug for keyword in ['/listings', '/search', '/homes']):
            categories.append("MLS Pages")
            continue

        # Rule: Pagination
        if 'page' in url_slug and re.search(r'page/[\d]+', url_slug):
            categories.append("Pagination")
            continue

        # Rule: Blog Filters
        if any(keyword in url_slug for keyword in ['/tag', '/category']):
            categories.append("Blog Filters")
            continue

        # Rule: Author Pages
        if 'blog' in url_slug and 'author' in url_slug:
            categories.append("Author Pages")
            continue

        # Rule: Blog Pages
        if '/blog' in url_slug:
            categories.append("Blog Pages")
            continue

        # Rule: Neighborhoods
        if contains_us_city(url_slug, us_cities) or '/neighborhoods' in url_slug or '/areas' in url_slug:
            categories.append("Neighborhood Pages")
            continue

        # Default: CMS Pages
        categories.append("CMS Pages")
    return categories


# Streamlit app
def main():
    st.title("URL Categorizer ⚡")
    st.write("Upload your CSV containing a `URL` column, and this tool will categorize each URL.")

    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'URL' not in df.columns:
            st.error("The uploaded CSV must contain a `URL` column.")
            return

        # Load US cities
        us_cities = load_us_cities()

        # Categorize URLs
        df['Category'] = categorize_urls(df['URL'].tolist(), us_cities)

        # Display and download results
        st.write("Categorized URLs:")
        st.dataframe(df)

        st.download_button(
            label="Download Categorized CSV",
            data=df.to_csv(index=False),
            file_name='categorized_urls.csv',
            mime='text/csv'
        )


if __name__ == "__main__":
    main()
