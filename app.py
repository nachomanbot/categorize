import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sentence_transformers import SentenceTransformer
import streamlit as st

# Load the trained model and embedder
embedder = SentenceTransformer('all-MiniLM-L6-v2')
try:
    model = pickle.load(open("neighborhood_model.pkl", "rb"))
except FileNotFoundError:
    model = None  # Handle first-time initialization

# Function to load and process training data
def load_training_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df['combined_text'] = df.apply(
        lambda row: f"{row['URL']} {row.get('Title', '')} {row.get('Meta Description', '')}".lower(), axis=1
    )
    return df

# Function to train the model
def train_model(df):
    X = embedder.encode(df['combined_text'].tolist(), show_progress_bar=True)
    y = df['Category']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate the model
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Save the updated model
    pickle.dump(clf, open("neighborhood_model.pkl", "wb"))
    return clf, report

# Streamlit app
def main():
    st.title("AI-Powered Page Categorizer and Trainer")
    
    # Categorization Section
    st.header("Categorize Pages")
    uploaded_file = st.file_uploader("Upload CSV for categorization", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['combined_text'] = df.apply(
            lambda row: f"{row['URL']} {row.get('Title', '')} {row.get('Meta Description', '')}".lower(), axis=1
        )
        if model:
            embeddings = embedder.encode(df['combined_text'].tolist(), show_progress_bar=True)
            df['Predicted Category'] = model.predict(embeddings)
            st.write("Categorized Data:")
            st.dataframe(df[['URL', 'Predicted Category']])
            st.download_button(
                label="Download Categorized Data",
                data=df.to_csv(index=False),
                file_name="categorized_results.csv",
                mime="text/csv"
            )
        else:
            st.error("No model found. Please train the AI first.")

    # Training Section
    st.header("Train the AI")
    uploaded_training_file = st.file_uploader("Upload Labeled Data for Training", type=["csv"], key="training")
    if uploaded_training_file:
        try:
            training_df = load_training_data(uploaded_training_file)
            st.write("Training data loaded successfully!")
            st.write(training_df.head())

            if st.button("Start Training"):
                trained_model, metrics = train_model(training_df)
                st.success("Model trained successfully!")
                st.json(metrics)
                st.write("The AI is now updated and ready to categorize pages.")
        except Exception as e:
            st.error(f"An error occurred during training: {e}")

if __name__ == "__main__":
    main()
