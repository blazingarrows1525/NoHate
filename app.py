import os
import re
import string
import numpy as np
import pandas as pd
import streamlit as st
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ==============================
# SAFE NLTK (NO CRASH ONLINE)
# ==============================
try:
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except:
    nltk.download('wordnet')

# ==============================
# GLOBALS
# ==============================
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# ==============================
# TEXT PREPROCESSING
# ==============================
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    tokens = text.split()
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
    return " ".join(tokens)

# ==============================
# LOAD + TRAIN (CACHED)
# ==============================
@st.cache_resource
def load_model():
    # Use small dataset for deployment stability
    df = pd.read_csv("https://raw.githubusercontent.com/dD2405/Twitter_Sentiment_Analysis/master/train.csv")

    df = df[['label', 'tweet']]
    df.columns = ['label', 'text']

    df['clean'] = df['text'].apply(preprocess_text)

    X = df['clean']
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_tfidf = vectorizer.fit_transform(X_train)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train_tfidf, y_train)

    acc = accuracy_score(y_test, model.predict(vectorizer.transform(X_test)))

    return model, vectorizer, acc

# ==============================
# PREDICT
# ==============================
def predict(text, model, vectorizer):
    clean = preprocess_text(text)
    vec = vectorizer.transform([clean])
    pred = model.predict(vec)[0]

    if pred == 1:
        return "Hate / Offensive ⚠️"
    else:
        return "Clean ✅"

# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(page_title="NoHate", layout="wide")

st.title("🛡️ NoHate - NLP Classifier")

st.write("Detect hate / offensive language using NLP")

# Load model
with st.spinner("Loading model..."):
    model, vectorizer, acc = load_model()

st.success(f"Model Loaded ✅ | Accuracy: {round(acc*100,2)}%")

# Input
text = st.text_area("Enter text to analyze")

if st.button("Classify"):
    if text.strip() == "":
        st.warning("Please enter text")
    else:
        result = predict(text, model, vectorizer)
        st.subheader("Result:")
        st.write(result)