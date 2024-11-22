import pandas as pd
import re
import streamlit as st

# Load US cities as a static resource
@st.cache_data
def load_us_cities():
    us_cities_path = "us_cities.csv"
    us_cities = pd.read_csv(us_cities_path)['CITY'].str.lower().tolist()
    return us_cities

# Flexible CSV loader
def load_csv(uploaded_file):
    try:
        # Try loading with default encoding
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        # Fallback for alternative encoding
        return pd.read_csv(uploaded_file, encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Define the categorization function
def categorize_url(url, us_cities):
    if not isinstance(url, str):
        return "Invalid URL"
    url = url.lower()

    # 1. Blog Filters
    if re.search(r'/tag|/category', url):
        return "Blog Filters"

    # 2. Blog Pages
    if re.search(r'/blog', url) and not re.search(r'/page|/author', url):
        return "Blog Pages"

    # 3. Property Pages
    if re.search(r'/properties|/property|/homes-for-sale|/rent|/listings|/rentals', url) and not re.search(r'/page', url):
        return "Property Pages"

    # 4. Pagination
    if re.search(r'/page/\d+', url):
        return "Pagination"

    # 5. CMS Pages
    if re.search(r'/contact|/about|/testimonials|/privacy|/tos|/terms|/resources|/sell|/purchase|/films', url):
        return "CMS Pages"

    # 6. Agent Pages
    if re.search(r'/agent|/team', url):
        return "Agent Pages"

    # 7. Neighborhood Pages
    if (
        any(city in url for city in us_cities) and
        not re.search(r'/blog|/properties|/property|/listings|/agent|/team|/contact|/about|/testimonials', url)
    ):
        return "Neighborhood Pages"

    # Fallback
    return "CMS Pages"

# Main function
def main():
    st.title("Categorizer 2.0")

    # Upload the file
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df = load_csv(uploaded_file)

        if df is None or df.empty:
            st.error("No data found in the file. Please upload a valid CSV.")
            return

        st.write("Preview of the uploaded file:")
        st.dataframe(df.head())

        # Ensure correct column mapping
        if len(df.columns) < 3:
            st.warning("File must have at least 3 columns: URL, Title, and Meta Description.")
            return

        # Rename columns for consistency
        df.columns = ["url", "title", "meta_description"]

        us_cities = load_us_cities()

        # Categorize URLs
        df["category"] = df["url"].apply(lambda url: categorize_url(url, us_cities))

        # Output results
        st.write("Categorized URLs:")
        st.dataframe(df[["url", "category"]])

        # Download button
        st.download_button(
            label="Download Categorized CSV",
            data=df[["url", "category"]].to_csv(index=False),
            file_name="categorized_urls.csv",
            mime="text/csv",
        )

# Run the app
if __name__ == "__main__":
    main()
