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
def categorize_url(row, us_cities):
    url = str(row["URL"]).lower() if "URL" in row and pd.notnull(row["URL"]) else ""
    title = str(row["Title"]).lower() if "Title" in row and pd.notnull(row["Title"]) else ""
    meta_description = str(row["Meta Description"]).lower() if "Meta Description" in row and pd.notnull(row["Meta Description"]) else ""

    # 0. Homepage (Prioritized)
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

    # 4. Agent Pages (Prioritized Above CMS)
    if re.search(r'/agent|/team', url):
        return "Agent Pages"

    # 5. Property Pages
    if re.search(r'/properties|/property|/homes-for-sale|/rent|/listings|/rentals', url) and not re.search(r'/page', url):
        return "Property Pages"

    # 6. Parameters
    if re.search(r'\?.+=', url):
        return "Parameters"

    # 7. Neighborhood Pages (Detect City Names)
    if (
        any(city in url for city in us_cities) and
        not re.search(r'/blog|/properties|/property|/listings|/agent|/team|/contact|/about|/testimonials|/privacy|/tos|/terms|/resources|/sell|/purchase|/films', url)
    ):
        return "Neighborhood Pages"

    # 8. CMS Pages (Exclude /agent and /team)
    if re.search(r'/contact|/about|/testimonials|/privacy|/tos|/terms|/resources|/sell|/purchase|/films', url) and not re.search(r'/agent|/team', url):
        return "CMS Pages"

    # Fallback to CMS Pages if uncategorized
    return "CMS Pages"

# Function to load the uploaded CSV file
def load_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
        if df.empty:
            st.error("Uploaded file is empty. Please upload a valid CSV.")
            st.stop()
        return df
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()

# Main function
def main():
    st.title("Categorizer 2.0")
    st.write("Upload a CSV file with at least a URL column. Additional columns like Title and Meta Description are optional.")

    # File uploader
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df = load_csv(uploaded_file)

        # Flexible column handling
        if "URL" not in df.columns:
            st.error("The uploaded file must have a 'URL' column.")
            return

        us_cities = load_us_cities()

        # Categorize URLs
        df["Category"] = df.apply(lambda row: categorize_url(row, us_cities), axis=1)

        # Show results and allow download
        st.write("Categorized URLs:")
        st.write(df[["URL", "Category"]])  # Only show URL and Category columns
        st.download_button(
            label="Download Results as CSV",
            data=df[["URL", "Category"]].to_csv(index=False),
            file_name="categorized_urls.csv",
            mime="text/csv"
        )

# Run the app
if __name__ == "__main__":
    main()
