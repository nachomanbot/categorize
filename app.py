import re
import pandas as pd
import streamlit as st

# Streamlit App Setup
st.title("Enhanced Page Categorization Tool ⚡")
st.markdown("Upload your URL list, and the tool will categorize the pages into predefined categories.")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file with a column named 'URL'", type=["csv"])

if uploaded_file:
    # Load the data
    pages_df = pd.read_csv(uploaded_file)
    if 'URL' not in pages_df.columns:
        st.error("The uploaded file must contain a column named 'URL'.")
    else:
        # Categorization logic
        def categorize_url(url):
            # Blog Filters
            if re.search(r"/tag/|/category/|/author/|\?\w+=|/\d{4}/\d{2}/", url):
                return "Blog Filters"
            # Pagination
            elif re.search(r"page=\d|/page/\d", url, re.IGNORECASE):
                return "Pagination"
            # Parameterized URLs
            elif re.search(r"\?.+", url):
                return "Pages with Parameters"
            # Property Pages
            elif re.search(r"/homes-for-sale/|/listing/", url):
                return "Property Pages"
            # MLS Pages
            elif re.search(r"/property-search/|/search/results/|/homes-for-sale/[^/]+$", url):
                return "MLS Pages"
            # Agent Pages
            elif re.search(r"/agent/|/realtor/", url, re.IGNORECASE):
                return "Agent Pages"
            # Blog Pages
            elif re.search(r"/blog/|/post/", url, re.IGNORECASE):
                return "Blog Pages"
            # CMS Pages
            elif re.search(r"/about|/contact|/privacy|/tos|/terms|/faq|/home-value|/reviews", url, re.IGNORECASE):
                return "CMS Pages"
            # Default category: Uncategorized
            return "Uncategorized"

        # Apply categorization
        pages_df["Category"] = pages_df["URL"].apply(categorize_url)

        # Show results
        st.success("Categorization complete!")
        st.write(pages_df)

        # Download button
        st.download_button(
            label="Download Categorized Results as CSV",
            data=pages_df.to_csv(index=False),
            file_name="categorized_pages.csv",
            mime="text/csv",
        )
