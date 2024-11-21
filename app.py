import streamlit as st
import pandas as pd
import re

# Title of the app
st.title("URL Categorization Tool")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file with URLs", type=["csv"])

if uploaded_file:
    # Load the data
    data = pd.read_csv(uploaded_file)
    
    if "URL" not in data.columns:
        st.error("The uploaded file must contain a column named 'URL'.")
    else:
        st.success("File uploaded successfully!")

        # Initialize categories
        def categorize_url(url):
            url = url.lower()  # Make it case insensitive

            # Rules for categorization
            if re.search(r'/blog/author/', url):
                return "Author Pages"
            elif re.search(r'/page/', url):
                return "Pagination"
            elif re.search(r'/blog', url):
                return "Blog Pages"
            elif re.search(r'/property', url) and len(url.strip("/").split("/")) > 2:
                return "Property Pages"
            elif re.search(r'/property', url):
                return "MLS Pages"
            elif re.search(r'/about|/contact|/resources|/home|/privacy|/tos|/terms|/help', url):
                return "CMS Pages"
            else:
                return "CMS Pages"  # Default fallback

        # Apply the categorization
        data["Category"] = data["URL"].apply(categorize_url)

        # Display categorized data
        st.write("Categorized Data", data)

        # Allow download of categorized data
        csv = data.to_csv(index=False)
        st.download_button(
            label="Download Categorized Data as CSV",
            data=csv,
            file_name="categorized_urls.csv",
            mime="text/csv",
        )
