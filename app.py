import pandas as pd
import streamlit as st
import re

# Cache the function to load the US cities CSV file
@st.cache_data
def load_us_cities():
    us_cities_path = 'us_cities.csv'  # Path to the file in the repo
    try:
        us_cities = pd.read_csv(us_cities_path)
        # Convert all headers to lowercase
        us_cities.columns = us_cities.columns.str.lower()
        if 'city' not in us_cities.columns:
            raise KeyError("The 'city' column is missing in the CSV file.")
        return us_cities['city'].str.lower().tolist()
    except Exception as e:
        st.error(f"Error loading US cities: {e}")
        return []

# Load US cities
us_cities = load_us_cities()

# Categorization function
def categorize_url(url, us_cities):
    # Categorize based on URL patterns
    if '/about' in url or '/contact' in url or '/resources' in url:
        return 'CMS Pages'
    elif '/blog' in url and '/author' in url:
        return 'Blog Author Pages'
    elif '/blog' in url and 'page/' in url:
        return 'Pagination'
    elif '/property' in url and 'page/' in url:
        return 'Pagination'
    elif '/properties' in url or '/rentals' in url:
        return 'Property Pages'
    elif any(city in url.lower() for city in us_cities):
        return 'Neighborhood Pages'
    elif 'page/' in url:
        return 'Pagination'
    elif '/search' in url or '/listings' in url:
        return 'MLS Pages'
    elif '/category' in url or '/tag' in url:
        return 'Blog Filters'
    elif re.match(r'https?://[^/]+$', url):  # Match homepage URL
        return 'CMS Pages'
    else:
        return 'CMS Pages'  # Default fallback

# Streamlit app
def main():
    st.title("URL Categorization Tool ⚡")
    st.write("Upload your CSV file with a `URL` column to categorize pages.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            # Load the input file
            df = pd.read_csv(uploaded_file)
            if 'URL' not in df.columns:
                st.error("The CSV file must contain a 'URL' column.")
                return

            # Categorize URLs
            df['Category'] = df['URL'].apply(lambda x: categorize_url(x, us_cities))

            # Display results
            st.write("Categorization complete!")
            st.dataframe(df)

            # Download button for categorized file
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Categorized CSV",
                data=csv,
                file_name="categorized_pages.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
