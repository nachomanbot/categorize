import pandas as pd
import re
import streamlit as st

# Load US cities as a static resource
@st.cache_data
def load_us_cities():
    us_cities_path = "us_cities.csv"
    us_cities = pd.read_csv(us_cities_path)['CITY'].str.lower().tolist()
    return us_cities

# Define the categorization function
def categorize_url(url, us_cities, title="", meta_description=""):
    url = str(url).lower() if pd.notna(url) else ""
    title = str(title).lower() if pd.notna(title) else ""
    meta_description = str(meta_description).lower() if pd.notna(meta_description) else ""

    # 0. Homepage (Prioritized)
    if url.endswith("/") or re.fullmatch(r"https?://[^/]+/?", url):
        return "CMS Pages"

    # 1. Blog Filters
    if re.search(r'/tag|/category', url):
        return "Blog Filters"

    # 2. Blog Pages
    if re.search(r'/blog', url) and not re.search(r'/page|/author', url):
        return "Blog Pages"
    if "blog" in title or "article" in title:
        return "Blog Pages"
    if "blog" in meta_description or "article" in meta_description:
        return "Blog Pages"

    # 3. Pagination
    if re.search(r'/page/\d+', url):
        return "Pagination"

    # 4. Agent Pages
    if re.search(r'/agent|/team', url):
        return "Agent Pages"

    # 5. Property Pages
    if re.search(r'/properties|/property|/homes-for-sale|/rent|/listings|/rentals', url) and not re.search(r'/page', url):
        return "Property Pages"
    if "home for sale" in title or "property" in title:
        return "Property Pages"
    if "find your home" in meta_description or "real estate" in meta_description:
        return "Property Pages"

    # 6. Parameters
    if re.search(r'\?.+=', url):
        return "Parameters"

    # 7. CMS Pages (Contact, Testimonials, About, etc.)
    if re.search(r'/contact|/about|/testimonials|/privacy|/tos|/terms|/resources|/sell|/purchase|/films', url):
        return "CMS Pages"
    if "about" in title or "contact" in title:
        return "CMS Pages"
    if "about us" in meta_description or "contact us" in meta_description:
        return "CMS Pages"

    # 8. Neighborhood Pages (Detect City Names)
    if (
        any(city in url for city in us_cities) and
        not re.search(r'/blog|/properties|/property|/listings|/agent|/team|/contact|/about|/testimonials|/privacy|/tos|/terms|/resources|/sell|/purchase|/films', url)
    ):
        return "Neighborhood Pages"

    # Fallback to CMS Pages if uncategorized
    return "CMS Pages"

# Main function
def main():
    st.title("Categorizer 2.0")
    st.write("Upload a CSV file. If no headers, the first column will be treated as URLs, second as Title, and third as Meta Description.")

    # File uploader
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            # Attempt to read the file with utf-8 encoding, fallback to iso-8859-1 if it fails
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8", header=None)
            except UnicodeDecodeError:
                df = pd.read_csv(uploaded_file, encoding="iso-8859-1", header=None)

            # If headers are not present, assume first column is URL, second is Title, third is Meta Description
            if len(df.columns) >= 3:
                df.columns = ["url", "title", "meta_description"]
            elif len(df.columns) == 2:
                df.columns = ["url", "title"]
                df["meta_description"] = ""
            elif len(df.columns) == 1:
                df.columns = ["url"]
                df["title"] = ""
                df["meta_description"] = ""

            us_cities = load_us_cities()

            # Categorize URLs
            df["Category"] = df.apply(
                lambda row: categorize_url(row["url"], us_cities, row.get("title", ""), row.get("meta_description", "")),
                axis=1
            )

            # Filter only URL and Category columns for output
            output_df = df[["url", "Category"]]

            # Show results and allow download
            st.write("Categorized URLs:", output_df)
            st.download_button(
                label="Download Categorized CSV",
                data=output_df.to_csv(index=False),
                file_name="categorized_urls.csv",
                mime="text/csv"
            )
        except pd.errors.EmptyDataError:
            st.error("No data found in the file. Please upload a valid CSV.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Run the app
if __name__ == "__main__":
    main()
