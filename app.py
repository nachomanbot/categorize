import pandas as pd
import re
import streamlit as st

# Load US cities (static file)
@st.cache_data
def load_us_cities():
    return pd.read_csv("us_cities.csv")["CITY"].str.lower().tolist()

# Function to categorize URLs
def categorize_url(url, us_cities):
    url = url.lower()

    # 1. Homepages
    if re.match(r'^https?://[^/]+/?$', url):
        return "CMS Pages"

    # 2. Blogs
    if re.search(r'/blog/[^/]+$', url) and not re.search(r'/page/', url):
        return "Blog Pages"

    # 3. Blog Filters (e.g., tag pages, category pages, authors)
    if re.search(r'/blog/(tag|category|author)', url):
        return "Blog Filters"

    # 4. Agents
    if re.search(r'/agent|/agents|/team|/meet', url):
        return "Agent Pages"

    # 5. Properties
    if re.search(r'/properties|/rentals|/homes-for-sale', url) and not re.search(r'/page/', url):
        return "Property Pages"

    # 6. MLS Pages
    if re.search(r'/mls|/property-search|/search|/listings', url) and not re.search(r'/page/', url):
        return "MLS Pages"

    # 7. Pagination
    if re.search(r'/page/\d+', url):
        return "Pagination"

    # 8. CMS Pages (Contact, Testimonials, About, etc.)
    if re.search(r'/contact|/about|/testimonials|/resources|/privacy|/terms|/sellyourhouse', url):
        return "CMS Pages"

    # 9. Pages with Parameters
    if "?" in url:
        return "Parameters"

    # 10. Neighborhood Pages (second-to-last priority)
    if any(city in url for city in us_cities) or re.search(r'/neighborhoods|/areas', url):
        return "Neighborhood Pages"

    # 11. CMS Pages (Fallback)
    return "CMS Pages"

# Main Streamlit app
def main():
    st.title("URL Categorization Tool")
    st.write("Upload a CSV file containing a column named 'URL' for categorization.")

    # File upload
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    us_cities = load_us_cities()

    if uploaded_file:
        # Load the data
        df = pd.read_csv(uploaded_file)
        if "URL" not in df.columns:
            st.error("The uploaded file must contain a 'URL' column.")
            return

        # Categorize each URL
        st.write("Processing URLs...")
        df["Category"] = df["URL"].apply(lambda x: categorize_url(x, us_cities))

        # Display the categorized data
        st.write("Categorized URLs:")
        st.dataframe(df)

        # Download the result
        csv = df.to_csv(index=False)
        st.download_button("Download Categorized CSV", csv, "categorized_urls.csv", "text/csv")

if __name__ == "__main__":
    main()
