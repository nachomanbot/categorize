import streamlit as st
import pandas as pd
import re

# Set the page title
st.title("⚡ Page Categorization Tool")

st.markdown("""
### **What This Tool Does**
This tool categorizes website pages into predefined categories such as CMS Pages, Blog Pages, MLS Pages, and more, based on URL patterns and rules.

### **Categories**
- **Agent Pages**
- **Blog Pages**
- **CMS Pages**
- **Development Pages**
- **Neighborhood Pages**
- **Property Pages**
- **Press Pages**
- **MLS Pages**
- **Blog Filters** (Tag pages and category pages)
- **Pagination**
- **Pages with Parameters**
- **Duplicates** (hashes, tokens, etc.)
- **Long URLs**
""")

# File upload
uploaded_file = st.file_uploader("Upload a CSV file containing URLs", type="csv")

if uploaded_file:
    # Load the uploaded CSV
    pages_df = pd.read_csv(uploaded_file)
    
    # Check if the required "URL" column exists
    if "URL" not in pages_df.columns:
        st.error("The uploaded file must contain a 'URL' column.")
    else:
        st.success("File uploaded successfully!")

        # Define categorization rules
        def categorize_page(url):
            # Rules for categories
            if url == "/" or url.endswith("/home") or re.search(r"^https?://[^/]+/$", url):
                return "CMS Pages"
            if re.search(r"/about|/contact|/resources|/privacy|/tos|/reviews", url, re.IGNORECASE):
                return "CMS Pages"
            if re.search(r"/blog/|/posts/|/articles/", url, re.IGNORECASE):
                return "Blog Pages"
            if re.search(r"/tag/|/category/", url, re.IGNORECASE):
                return "Blog Filters"
            if re.search(r"/agent|/team|/staff|/profile", url, re.IGNORECASE):
                return "Agent Pages"
            if re.search(r"/development|/projects", url, re.IGNORECASE):
                return "Development Pages"
            if re.search(r"/neighborhoods|/community", url, re.IGNORECASE):
                return "Neighborhood Pages"
            if re.search(r"/property|/homes-for-sale|/listing|/properties", url, re.IGNORECASE):
                if len(url.split('/')) > 4:
                    return "Property Pages"
                else:
                    return "MLS Pages"
            if re.search(r"/press|/news", url, re.IGNORECASE):
                return "Press Pages"
            if re.search(r"page=\d+|/page/", url, re.IGNORECASE):
                return "Pagination"
            if re.search(r"\?|&", url):
                return "Pages with Parameters"
            if len(url) > 100:
                return "Long URLs"
            if re.search(r"#|token|session|sid", url, re.IGNORECASE):
                return "Duplicates: Hashes/Tokens"
            
            return "Uncategorized"

        # Apply the categorization function
        pages_df['Category'] = pages_df['URL'].apply(categorize_page)

        # Display the categorized results
        st.header("Categorized Pages")
        st.dataframe(pages_df)

        # Download the results
        st.download_button(
            label="Download Categorized Pages",
            data=pages_df.to_csv(index=False),
            file_name="categorized_pages.csv",
            mime="text/csv",
        )

        st.success("Categorization completed! You can download the categorized file.")
