import streamlit as st
import pandas as pd
import re


# Load US Cities CSV from static resource
@st.cache_data
def load_us_cities():
    us_cities_path = 'us_cities.csv'  # Ensure this file is in your GitHub repo
    us_cities = pd.read_csv(us_cities_path)['CITY'].str.lower().tolist()
    return us_cities


# Define categorization rules
def categorize_url(url, us_cities):
    url = url.lower()

    # 1. Homepages
    if re.match(r'^https?://[^/]+/?$', url):
        return "CMS Pages"

    # 2. Neighborhood Pages
    if any(city in url for city in us_cities) or re.search(r'/neighborhoods|/areas', url):
        return "Neighborhood Pages"

    # 3. Property Pages
    if re.search(r'/properties|/rentals|/homes-for-sale', url) and not re.search(r'/page/', url):
        return "Property Pages"

    # 4. MLS Pages
    if re.search(r'/mls|/property-search|/search|/listings', url) and not re.search(r'/page/', url):
        return "MLS Pages"

    # 5. Blog Pages
    if re.search(r'/blog/[^/]+$', url) and not re.search(r'/page/', url):
        return "Blog Pages"

    # 6. Blog Filters (e.g., tag pages, category pages)
    if re.search(r'/blog/(tag|category|author)', url):
        return "Blog Filters"

    # 7. Pagination
    if re.search(r'/page/\d+', url):
        return "Pagination"

    # 8. Pages with Parameters
    if "?" in url:
        return "Parameters"

    # 9. CMS Pages (Fallback)
    return "CMS Pages"


# Main Streamlit App
def main():
    st.title("URL Categorization Tool")
    st.write("Upload your CSV file with a column named 'URL' to categorize the pages.")

    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

    if uploaded_file is not None:
        # Load the file
        pages_df = pd.read_csv(uploaded_file)

        if 'URL' not in pages_df.columns:
            st.error("The uploaded CSV must contain a column named 'URL'.")
            return

        # Load US cities
        us_cities = load_us_cities()

        # Apply categorization
        st.write("Categorizing URLs...")
        pages_df['Category'] = pages_df['URL'].apply(lambda x: categorize_url(x, us_cities))

        # Display results
        st.write(pages_df)

        # Download option
        csv = pages_df.to_csv(index=False)
        st.download_button(
            label="Download Categorized CSV",
            data=csv,
            file_name="categorized_pages.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
