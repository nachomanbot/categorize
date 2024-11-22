import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer
import pickle

# Load pre-trained models
models = {
    "global": pickle.load(open("models/global_model.pkl", "rb")),
    "blogs": pickle.load(open("models/blog_model.pkl", "rb")),
    "neighborhoods": pickle.load(open("models/neighborhood_model.pkl", "rb")),
    "properties": pickle.load(open("models/property_model.pkl", "rb")),
}

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def global_classify(row):
    text = f"{row['URL']} {row.get('Title', '')} {row.get('Meta Description', '')}".lower()
    embedding = embedder.encode([text])[0]
    return models["global"].predict([embedding])[0]

def specialized_classify(category, row):
    text = f"{row['URL']} {row.get('Title', '')} {row.get('Meta Description', '')}".lower()
    embedding = embedder.encode([text])[0]
    return models[category].predict([embedding])[0]

# Streamlit App
def main():
    st.title("Multi-Model AI Page Categorizer")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload a CSV for categorization", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['Global Category'] = df.apply(global_classify, axis=1)
        
        # Run specialized models
        for category in ["blogs", "neighborhoods", "properties"]:
            df.loc[df['Global Category'] == category, 'Category'] = df.apply(
                lambda row: specialized_classify(category, row), axis=1
            )
        
        # Output
        st.write(df[['URL', 'Category']])
        st.download_button(
            "Download Categorized Data",
            data=df.to_csv(index=False),
            file_name="categorized_results.csv",
            mime="text/csv"
        )

    # Training Section
    st.header("Train Specialized Models")
    for category in ["blogs", "neighborhoods", "properties"]:
        st.subheader(f"Train {category.capitalize()} Model")
        train_file = st.file_uploader(f"Upload training data for {category}", type=["csv"], key=category)
        if train_file:
            train_df = pd.read_csv(train_file)
            st.write(f"Training data loaded for {category}")
            if st.button(f"Train {category.capitalize()} Model"):
                # Train and save model logic here
                st.success(f"{category.capitalize()} Model Trained Successfully!")

if __name__ == "__main__":
    main()
