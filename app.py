import streamlit as st
import pandas as pd
import re

# Set the page title
st.title("Improved URL-Based Page Categorization Tool")

st.markdown("""
⚡ **What It Does**  
This tool categorizes pages solely based on URL patterns, with enhanced distinction between Property Pages and MLS Pages, and expanded CMS rules.

⚡ **How to Use It:**  
1. Prepare your URLs by removing duplicates (e.g., www vs Non-www, http vs https).  
2. Upload `pages.csv` containing a single column: `URL`.  
3. Click **"Categorize Pages"** to start the process.  
4. Download the categorized results as a CSV.

⚡ **Predefined Categories**  
- **Property Pages**: Specific listings (e.g., `/property/123`, `/listings/single`).  
- **MLS Pages**: Broader search patterns (e.g., `/homes-for-sale`, `/listings`).  
- **Agent Pages**: URLs with `/agents`, `/team`, or names (e.g., `/john-doe`).  
- **Blog Pages**: URLs with `/blog`.  
- **CMS Pages**: Generic or non-duplicate root-level pages (e.g., `/about`, `/contact`, `/careers`, `/our-listing-process`).  
- **Neighborhood Pages**: URLs referencing locations or communities.  
- **Pagination**: URLs indicating `page=2` or `/page/2`.  
- **Parameters**: URLs with query parameters (e.g., `?city=`).  
- **Fallback**: Uncategorized if no rules match.  
""")

# Step 1: Upload Pages File
uploaded_file = st.file_uploader("Upload your pages.csv file (must contain a 'URL' column)", type="csv")

if uploaded_file:
    # Step 2: Load Pages Data
    pages_df = pd.read_csv(uploaded_file)
    if 'URL' not in pages_df.columns:
        st.error("The uploaded file must have a 'URL' column.")
    else:
        st.success("File uploaded successfully!")

        # Step 3: Define Categorization Rules
        def categorize_url(url):
            # Step 3.1: Primary Categories
            if re.search(r"/property/\d+|/listings/\w+", url):
                return "Property Pages"
            elif re.search(r"/homes-for-sale|/listings|/by-price|/by-property-type", url):
                return "MLS Pages"
            elif "/agents" in url or "/team" in url or re.search(r"/[a-zA-Z-]+$", url):
                return "Agent Pages"
            elif "/blog" in url:
                return "Blog Pages"
            elif re.search(r"/about|/contact|/testimonials|/careers|/compare|/our-listing-process", url) or re.match(r"^https?://[^/]+/?$", url):
                return "CMS Pages"
            elif "/neighborhoods" in url or re.search(r"/[a-zA-Z-]+$", url):
                return "Neighborhood Pages"
            elif re.search(r"page=[0-9]+", url) or "/page/" in url:
                return "Pagination"
            elif "?" in url:
                return "Parameters"
            elif len(url) > 100:
                return "Long URLs"
            else:
                return "Uncategorized"

        # Apply rules to the URL column
        pages_df['Assigned Category'] = pages_df['URL'].apply(categorize_url)

        # Display Results
        st.header("Categorized Pages")
        st.write(pages_df[['URL', 'Assigned Category']])

        # Step 4: Download the Results
        st.download_button(
            label="Download Categorized Pages as CSV",
            data=pages_df.to_csv(index=False),
            file_name="categorized_pages.csv",
            mime="text/csv",
        )
