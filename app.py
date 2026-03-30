"""
Hate Speech Detection Web Application
Course: 21CSE356T - Natural Language Processing
NLP Pipeline: Text Preprocessing → TF-IDF Vectorization → Logistic Regression Classification

This application uses the Kaggle Hate Speech and Offensive Language Dataset
to train a machine learning model that classifies text as:
  0 - Hate Speech
  1 - Offensive Language
  2 - Neither (Clean)
"""

import os
import re
import string
import json
import traceback

# Base directory (where app.py lives) - critical for Render deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Download NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# ─── Initialize Flask App ────────────────────────────────────────────────────
app = Flask(__name__, static_folder='static')
CORS(app)

# ─── Global Model Variables ──────────────────────────────────────────────────
model = None
vectorizer = None
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
model_stats = {}

# ─── Hateful / Offensive Word Lexicon ────────────────────────────────────────
# Common hate/offensive words for word-level analysis
HATE_INDICATORS = {
    'hate', 'kill', 'die', 'stupid', 'idiot', 'dumb', 'ugly', 'loser',
    'trash', 'garbage', 'worthless', 'pathetic', 'disgusting', 'terrible',
    'horrible', 'worst', 'awful', 'nasty', 'evil', 'sick', 'freak',
    'moron', 'fool', 'jerk', 'creep', 'scum', 'filth', 'vermin',
    'destroy', 'attack', 'threat', 'violence', 'abuse', 'harass',
    'bully', 'racist', 'sexist', 'bigot', 'slur', 'degrade',
    'inferior', 'subhuman', 'retard', 'cripple', 'terrorist',
    'extremist', 'radical', 'toxic', 'venom', 'poison', 'corrupt',
    'degenerate', 'savage', 'barbaric', 'primitive', 'uncivilized',
    'shut', 'stfu', 'gtfo', 'damn', 'hell', 'crap',
}

# Word replacements for improvement suggestions
WORD_IMPROVEMENTS = {
    'hate': 'strongly dislike',
    'stupid': 'uninformed',
    'idiot': 'person',
    'dumb': 'unaware',
    'ugly': 'unattractive',
    'loser': 'unsuccessful person',
    'trash': 'waste',
    'worthless': 'undervalued',
    'pathetic': 'unfortunate',
    'disgusting': 'unpleasant',
    'terrible': 'poor',
    'horrible': 'bad',
    'awful': 'not great',
    'nasty': 'unkind',
    'evil': 'harmful',
    'moron': 'person',
    'fool': 'person',
    'jerk': 'rude person',
    'creep': 'unsettling person',
    'kill': 'stop',
    'die': 'end',
    'destroy': 'dismantle',
    'attack': 'criticize',
    'retard': 'person',
    'shut': 'be quiet',
    'damn': 'darn',
    'hell': 'heck',
    'crap': 'stuff',
    'toxic': 'unhealthy',
    'savage': 'intense',
    'filth': 'mess',
    'scum': 'person',
    'freak': 'unusual person',
    'garbage': 'waste',
    'bully': 'intimidate',
    'racist': 'discriminatory',
    'sexist': 'gender-biased',
    'bigot': 'intolerant person',
}


# ─── Text Preprocessing ─────────────────────────────────────────────────────
def preprocess_text(text):
    """
    NLP Text Preprocessing Pipeline:
    1. Lowercasing
    2. URL removal
    3. Mention removal (@user)
    4. Special character removal
    5. Number removal
    6. Extra whitespace removal
    7. Tokenization
    8. Stopword removal
    9. Lemmatization
    """
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove @mentions
    text = re.sub(r'@\w+', '', text)
    # Remove RT (retweet tag)
    text = re.sub(r'\brt\b', '', text)
    # Remove special characters and punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Tokenize, remove stopwords, lemmatize
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)


# ─── Load Dataset & Train Model ─────────────────────────────────────────────
def load_and_train():
    """Load Kaggle dataset and train the NLP classification model."""
    global model, vectorizer, model_stats

    print("\n" + "=" * 60)
    print("  🔄 Loading Hate Speech Dataset from Kaggle...")
    print("=" * 60)

    try:
        # Always try local CSV first (reliable on Render)
        csv_path = os.path.join(BASE_DIR, 'labeled_data.csv')
        print(f"  📂 Looking for dataset at: {csv_path}")
        print(f"  📂 File exists: {os.path.exists(csv_path)}")

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            print(f"  ✅ Dataset loaded from local file: {df.shape[0]} records")
        else:
            # Fallback to kagglehub
            print("  ⚠️ Local CSV not found, trying kagglehub...")
            import kagglehub
            dataset_path = kagglehub.dataset_download(
                "mrmorj/hate-speech-and-offensive-language-dataset"
            )
            csv_path = os.path.join(dataset_path, 'labeled_data.csv')
            df = pd.read_csv(csv_path)
            print(f"  ✅ Dataset loaded from Kaggle: {df.shape[0]} records")
    except Exception as e:
        print(f"  ❌ FAILED to load dataset: {e}")
        traceback.print_exc()
        return

    # ─── Data Exploration ────────────────────────────────────────────────
    print("\n  📊 Dataset Overview:")
    print(f"     Shape: {df.shape}")
    print(f"     Columns: {list(df.columns)}")
    print(f"\n  First 5 records:\n{df.head()}")

    # Identify the text and label columns
    text_col = None
    label_col = None

    # Common column names in this dataset
    for col in df.columns:
        col_lower = col.lower()
        if 'tweet' in col_lower or 'text' in col_lower or 'comment' in col_lower:
            text_col = col
        if 'class' in col_lower or 'label' in col_lower:
            label_col = col

    if text_col is None or label_col is None:
        # Fallback: assume last string column is text, and there's a numeric class column
        for col in df.columns:
            if df[col].dtype == 'object' and text_col is None:
                text_col = col
            if df[col].dtype in ['int64', 'int32'] and 'class' in col.lower():
                label_col = col

    if text_col is None:
        text_col = 'tweet'
    if label_col is None:
        label_col = 'class'

    print(f"\n  Using text column: '{text_col}', label column: '{label_col}'")

    # Drop NaN values
    df = df.dropna(subset=[text_col, label_col])

    # Class distribution
    class_dist = df[label_col].value_counts().to_dict()
    print(f"\n  📊 Class Distribution:")
    class_names = {0: 'Hate Speech', 1: 'Offensive Language', 2: 'Neither (Clean)'}
    for cls, count in sorted(class_dist.items()):
        name = class_names.get(cls, f'Class {cls}')
        print(f"     {name}: {count} ({count/len(df)*100:.1f}%)")

    # ─── Preprocess Text ─────────────────────────────────────────────────
    print("\n  🔧 Preprocessing text data...")
    df['clean_text'] = df[text_col].astype(str).apply(preprocess_text)

    # Remove empty texts after preprocessing
    df = df[df['clean_text'].str.len() > 0]
    print(f"  ✅ Preprocessing complete. {len(df)} valid records.")

    # ─── Feature Extraction & Model Training ─────────────────────────────
    X = df['clean_text']
    y = df[label_col]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n  📚 Training set: {len(X_train)} | Test set: {len(X_test)}")

    # TF-IDF Vectorizer with n-grams
    print("  🔤 Building TF-IDF features (unigrams + bigrams)...")
    vectorizer = TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True
    )

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"  ✅ TF-IDF matrix: {X_train_tfidf.shape}")

    # Train Logistic Regression
    print("  🤖 Training Logistic Regression model...")
    model = LogisticRegression(
        C=1.0,
        max_iter=1000,
        solver='lbfgs',
        class_weight='balanced',
        random_state=42
    )
    model.fit(X_train_tfidf, y_train)

    # ─── Evaluate Model ──────────────────────────────────────────────────
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()

    print(f"\n  🎯 Model Accuracy: {accuracy * 100:.2f}%")
    print(f"\n  📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=[
        class_names.get(c, f'Class {c}') for c in sorted(y.unique())
    ]))

    # Store model stats
    model_stats = {
        'accuracy': round(accuracy * 100, 2),
        'total_samples': len(df),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'features': X_train_tfidf.shape[1],
        'class_distribution': {class_names.get(int(k), f'Class {k}'): int(v) for k, v in class_dist.items()},
        'classification_report': {
            k: {
                'precision': round(v['precision'] * 100, 2) if isinstance(v, dict) and 'precision' in v else None,
                'recall': round(v['recall'] * 100, 2) if isinstance(v, dict) and 'recall' in v else None,
                'f1_score': round(v['f1-score'] * 100, 2) if isinstance(v, dict) and 'f1-score' in v else None,
            }
            for k, v in report.items() if isinstance(v, dict) and 'precision' in v
        },
        'confusion_matrix': conf_matrix,
    }

    print("\n" + "=" * 60)
    print("  ✅ Model trained and ready!")
    print("=" * 60 + "\n")


# ─── Analyze Text ────────────────────────────────────────────────────────────
def analyze_text(text):
    global model, vectorizer

    # Auto-load model if not loaded
    if model is None or vectorizer is None:
        print("⚠️ Model not loaded, loading now...")
        load_and_train()

    if model is None or vectorizer is None:
        return {"error": "Model failed to load. Check server logs."}

    # Preprocess
    clean = preprocess_text(text)

    if not clean:
        return {
            'classification': 'Clean',
            'class_id': 2,
            'confidence': 100.0,
            'probabilities': {'Hate Speech': 0, 'Offensive Language': 0, 'Clean': 100},
            'flagged_words': [],
            'improved_text': text,
            'suggestions': ['The text appears clean after analysis.'],
            'original_text': text,
            'preprocessed_text': clean,
        }

    # Vectorize and predict
    text_tfidf = vectorizer.transform([clean])
    prediction = model.predict(text_tfidf)[0]
    probabilities = model.predict_proba(text_tfidf)[0]

    class_names = {0: 'Hate Speech', 1: 'Offensive Language', 2: 'Clean'}
    class_label = class_names.get(prediction, 'Unknown')

    # Probability percentages
    prob_dict = {}
    for i, cls in enumerate(model.classes_):
        name = class_names.get(cls, f'Class {cls}')
        prob_dict[name] = round(float(probabilities[i]) * 100, 2)

    confidence = round(float(max(probabilities)) * 100, 2)

    # Word-level analysis
    words = text.lower().split()
    flagged_words = []
    improved_words = []
    suggestions = []

    for word in text.split():
        word_lower = word.lower().strip(string.punctuation)
        if word_lower in HATE_INDICATORS:
            replacement = WORD_IMPROVEMENTS.get(word_lower, '[removed]')
            flagged_words.append({
                'word': word,
                'reason': f'"{word}" is flagged as potentially hateful/offensive',
                'replacement': replacement,
                'severity': 'high'
            })
            improved_words.append(replacement)
            suggestions.append(f'Replace "{word}" with "{replacement}".')
        else:
            improved_words.append(word)

    improved_text = ' '.join(improved_words)

    if prediction == 0:
        suggestions.append('This text contains hate speech. Consider rephrasing.')
    elif prediction == 1:
        suggestions.append('This text contains offensive language. Consider using neutral terms.')
    else:
        suggestions.append('This text appears clean and respectful.')

    total_words = len(words) if words else 1
    hateful_count = len(flagged_words)
    hate_percentage = round((hateful_count / total_words) * 100, 2)
    clean_percentage = round(100 - hate_percentage, 2)

    return {
        'classification': class_label,
        'class_id': int(prediction),
        'confidence': confidence,
        'probabilities': prob_dict,
        'flagged_words': flagged_words,
        'improved_text': improved_text,
        'suggestions': suggestions,
        'original_text': text,
        'preprocessed_text': clean,
        'stats': {
            'total_words': total_words,
            'hateful_words': hateful_count,
            'clean_words': total_words - hateful_count,
            'hate_percentage': hate_percentage,
            'clean_percentage': clean_percentage,
        }
    }


print("🚀 Starting app and loading model...")
load_and_train()

# ─── API Routes ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory('static', 'index.html')


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze text for hate speech."""
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text'].strip()
    if not text:
        return jsonify({'error': 'Empty text provided'}), 400

    result = analyze_text(text)
    return jsonify(result)


@app.route('/api/model-info', methods=['GET'])
def api_model_info():
    """Return model training statistics."""
    return jsonify(model_stats)


# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)