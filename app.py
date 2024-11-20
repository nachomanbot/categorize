import streamlit as st
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# Set the page title
st.title("Enhanced Page Categorization Tool")

st.markdown("""
⚡ **What It Does**  
This tool categorizes pages by matching their content with a preloaded list of categories based on text similarity. Includes enhanced preprocessing, weighted embeddings, and fallback categories.

⚡ **Preloaded Categories**  
- **Agent Pages**: Pages describing real estate agents, their profiles, and contact details.  
- **Blog Pages**: Articles and blog posts covering topics related to real estate, lifestyle, or market trends.  
- **CMS Pages**: Content management system pages, such as About Us or Contact pages.  
- **Development Pages**: Pages showcasing new or ongoing real estate developments.  
- **Neighborhood Pages**: Pages providing detailed information about neighborhoods, including amenities and demographics.  
- **Property Pages**: Pages showcasing property listings, including property descriptions, prices, and photos.  
- **Press Pages**: Pages featuring press releases or media coverage.  
- **MLS Pages**: Pages featuring multiple listing service (MLS) data.  
- **Long URLs**: Pages with overly long or complex URLs.  
- **Other Pages**: A generic category for pages that don't fit specific categories.

⚡ **How to Use It:**  
1. Upload `pages.csv` containing the pages to categorize.  
2. Click **"Categorize Pages"** to start the process.  
3. Download the categorized results as a CSV.

⚡ **Note:**  
- Ensure the `pages.csv` file is in `.csv` format with relevant metadata columns.
""")

# Preloaded categories with detailed descriptions
CATEGORIES = {
    "Agent Pages": "Pages describing real estate agents, their profiles, and contact details.",
    "Blog Pages": "Articles and blog posts covering topics related to real estate, lifestyle, or market trends.",
    "CMS Pages": "Content management system pages, such as About Us or Contact pages.",
    "Development Pages": "Pages showcasing new or ongoing real estate developments.",
    "Neighborhood Pages": "Pages providing detailed information about neighborhoods, including amenities and demographics.",
    "Property Pages": "Pages showcasing property listings, including property descriptions, prices, and photos.",
    "Press Pages": "Pages featuring press releases or media coverage.",
    "MLS Pages": "Pages featuring multiple listing service (MLS) data.",
    "Long URLs": "Pages with overly long or complex URLs.",
    "Other Pages": "A fallback category for pages that don't fit specific categories."
}

# Step 1: Upload Pages File
st.header("Upload Your Pages File")
uploaded_pages = st.file_uploader("Upload pages.csv", type="csv")

if uploaded_pages:
    st.success("File uploaded successfully!")
    
    # Step 2: Load Pages Data
    pages_df = pd.read_csv(uploaded_pages)

    # Combine and weight text columns for similarity matching
    pages_df['combined_text'] = (
        pages_df['Title'].fillna('') + " " +
        2 * pages_df['Meta Description'].fillna('') + " " +  # Weighting Meta Descriptions more heavily
        pages_df['Headings'].fillna('')
    )

    # Extract category names and descriptions
    category_names = list(CATEGORIES.keys())
    category_descriptions = list(CATEGORIES.values())

    # Step 3: Categorize Pages
    if st.button("Categorize Pages"):
        st.info("Processing data... This may take a while.")

        # Step 4: Generate Embeddings for Pages and Categories
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Updated model for better performance

        # Generate embeddings for pages
        pages_embeddings = model.encode(pages_df['combined_text'].tolist(), show_progress_bar=True)

        # Generate embeddings for preloaded categories
        category_embeddings = model.encode(category_descriptions, show_progress_bar=True)

        # Create a FAISS index for categories
        dimension = category_embeddings.shape[1]
        faiss_index = faiss.IndexFlatL2(dimension)
        faiss_index.add(category_embeddings.astype('float32'))

        # Match pages to categories
        D, I = faiss_index.search(pages_embeddings.astype('float32'), k=1)  # k=1 for the closest match

        # Log similarity scores for debugging
        similarity_scores = 1 - (D / np.max(D))  # Convert distance to similarity
        st.write("Similarity Scores (Preview):", similarity_scores.flatten()[:10])

        # Assign categories and calculate similarity scores
        threshold = 0.3  # Minimum similarity score for a valid match
        pages_df['assigned_category'] = [
            category_names[i] if score >= threshold else "Other Pages"
            for i, score in zip(I.flatten(), similarity_scores.flatten())
        ]
        pages_df['similarity_score'] = np.round(similarity_scores.flatten(), 4)

        # Step 5: Display and Download Results
        st.success("Categorization complete! Download your results below.")
        st.write(pages_df[['combined_text', 'assigned_category', 'similarity_score']])

        st.download_button(
            label="Download Categorized Pages as CSV",
            data=pages_df.to_csv(index=False),
            file_name="categorized_pages.csv",
            mime="text/csv",
        )
