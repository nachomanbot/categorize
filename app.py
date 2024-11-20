import streamlit as st
import pandas as pd
import re

# Set the page title
st.title("Refined URL-Based Page Categorization Tool")

st.markdown("""
⚡ **What It Does**  
This tool categorizes pages solely based on URL patterns, with enhanced distinction between Property Pages and MLS Pages, and expanded CMS rules.

⚡ **How to Use It:**  
1. Prepare your URLs by removing duplicates (e.g., www vs Non-www, http vs https).  
2. Upload `pages.csv` containing a single column: `URL`.  
3. Click **"Categorize Pages"** to start the process.  
4. Download the categorized results as a CSV.

⚡ **Predefined Categories**  
- **Property Pages**: Specific listings or area-focused URLs (e.g., `/property/123`, `/homes-for-sale/southlake`).  
- **MLS Pages**: Broader search patterns (e.g., `/homes-for-sale`, `/listings`).  
- **Agent Pages**: URLs with `/agents`, `/team`, or names (e.g., `/john-doe`).  
- **Blog Pages**: URLs with `/blog`.  
- **CMS Pages**: Generic or root-level pages (e.g., `/about`, `/contact`, `/careers`).  
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
            elif re.search(r"/homes-for-sale/[a-zA-Z0-9-]+", url):
                return "Property Pages"  # Area-specific homes-for-sale URLs
            elif re.search(r"/homes-for-sale|/listings|/by-price|/by-property-type", url):
                return "MLS Pages"  # Broader search categories
            elif "/agents" in url or "/team" in url or re.search(r"/[a-zA-Z-]+$", url):
                return "Agent Pages"
            elif "/blog" in url:
                return "Blog Pages"
            elif re.search(r"/about|/contact|/testimonials|/careers|/compare|/our-listing-process", url) or re.match(r"^https?://[^/]+/?$", url):
                return "CMS Pages"
            elif "/neighborhoods" in url or re.search(r"/[a-zA-Z-]+$", url):
                return "Neighborhood Pages"
            elif re.search(r"page
