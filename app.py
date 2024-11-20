import streamlit as st
import pandas as pd
import re

# Set the page title
st.title("Enhanced URL-Based Page Categorization Tool")

st.markdown("""
⚡ **What It Does**  
This tool categorizes pages solely based on URL patterns, with improved distinctions between Property Pages and MLS Pages.

⚡ **How to Use It:**  
1. Upload `pages.csv` containing a single column: `URL`.  
2. Click **"Categorize Pages"** to start the process.  
3. Download the categorized results as a CSV.

⚡ **Predefined Categories**  
- **Property Pages**: URLs containing `/property` or single listings.  
- **MLS Pages**: URLs with `/homes-for-sale`, `/listings`, or commercial intent patterns.  
- **Agent Pages**: URLs with `/agents`, `/team`, or names (e.g., `/john-doe`).  
- **Blog Pages**: URLs with `/blog`.  
- **CMS Pages**: Generic pages like `/about`, `/contact`, `/testimonials`.  
- **Neighborhood Pages**: URLs referencing specific locations or communities.  
- **Pagination**: URLs indicating `page=2` or `/page/2`.  
- **Parameters**: URLs with query parameters (e.g., `?city=`).  
- **Duplicates**: `http vs https` or `www vs non-www` (processed last).  
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
            # Predefined rules
            if "/property/" in url or re.search(r"/listings/\d+", url):
                return "Property Pages"
            elif re.search(r"/homes-for-sale|/listings|/by-price|/by-property-type", url):
                return "MLS Pages"
            elif "/agents" in url or "/team" in url or re.search(r"/[a-zA-Z-]+$", url):
                return "Agent Pages"
            elif "/blog" in url:
                return "Blog Pages"
            elif re.search(r"/about|/contact|/testimonials|/compare", url):
                return "CMS Pages"
            elif "/neighborhoods" in url or re.search(r"/[a-zA-Z-]+$", url):
                return "Neighborhood Pages"
            elif re.search(r"page=[0-9]+", url) or "/page/" in url:
                return "Pagination"
            elif "?" in url:
                return "Parameters"
            elif re.match(r"^http://", url):
                return "Duplicates: http vs https"
            elif re.match(r"^https?://www\.", url) or re.match(r"^https?://[^www]\.", url):
                return "Duplicates: www vs Non-www"
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
