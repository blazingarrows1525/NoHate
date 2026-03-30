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

# ==============================
# NLTK SAFE LOAD
# ==============================
try:
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except:
    nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# ==============================
# PREPROCESS
# ==============================
def preprocess(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]

    return " ".join(words)

# ==============================
# LOAD + TRAIN MODEL (CACHED)
# ==============================
@st.cache_resource
def load_model():
    df = pd.read_csv("https://raw.githubusercontent.com/dD2405/Twitter_Sentiment_Analysis/master/train.csv")

    df = df[['label', 'tweet']]
    df.columns = ['label', 'text']

    df['clean'] = df['text'].apply(preprocess)

    X = df['clean']
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_vec = vectorizer.fit_transform(X_train)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train_vec, y_train)

    return model, vectorizer

# ==============================
# ANALYZE FUNCTION
# ==============================
def analyze_text(text, model, vectorizer):
    clean = preprocess(text)
    vec = vectorizer.transform([clean])
    pred = model.predict(vec)[0]

    if pred == 1:
        return "⚠️ Hate / Offensive Language"
    else:
        return "✅ Clean Text"

# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(page_title="NoHate", layout="centered")

st.title("🛡️ NoHate - NLP Classifier")
st.write("Detect hate speech using NLP")

# Load model once
with st.spinner("Loading model..."):
    model, vectorizer = load_model()

st.success("Model Ready ✅")

# Input
user_input = st.text_area("Enter text")

if st.button("Classify"):
    if user_input.strip() == "":
        st.warning("Please enter text")
    else:
        result = analyze_text(user_input, model, vectorizer)
        st.subheader("Result:")
        st.write(result)