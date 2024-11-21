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
    if re.search(r'/contact|/about|/testimonials|/privacy|/tos|/terms|/resources', url):
        return "CMS Pages"

    # 9. Neighborhood Pages (second-to-last priority)
    if not re.search(r'/blog|/properties|/property|/listings|/agent|/team|/contact|/about|/testimonials|/search|/mls', url) and (
        any(city in url for city in us_cities) or re.search(r'/neighborhoods|/areas', url)):
        return "Neighborhood Pages"

    # 10. Default fallback
    return "CMS Pages"

# Main function
def main():
    st.title("URL Categorizer")
    
    # Load US cities
    us_cities = load_us_cities()

    # File upload
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        if "URL" not in df.columns:
            st.error("The uploaded file must contain a column named 'URL'.")
            return
        
        df["Category"] = df["URL"].apply(lambda url: categorize_url(url, us_cities))
        
        st.write("Categorized Data:")
        st.dataframe(df)

        # Download button for the categorized data
        csv = df.to_csv(index=False)
        st.download_button("Download Categorized Data", data=csv, file_name="categorized_pages.csv", mime="text/csv")

# Run the app
if __name__ == "__main__":
    main()
