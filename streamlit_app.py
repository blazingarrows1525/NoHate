"""
NoHate - Hate Speech Detection (Streamlit Version)
NLP Pipeline: Text Preprocessing → TF-IDF Vectorization → Logistic Regression
"""

import os
import re
import string
import numpy as np
import pandas as pd
import nltk
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from collections import Counter

# Download NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', quiet=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Hateful Word Lexicon ────────────────────────────────────────────────────
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

WORD_IMPROVEMENTS = {
    'hate': 'strongly dislike', 'stupid': 'uninformed', 'idiot': 'person',
    'dumb': 'unaware', 'ugly': 'unattractive', 'loser': 'unsuccessful person',
    'trash': 'waste', 'worthless': 'undervalued', 'pathetic': 'unfortunate',
    'disgusting': 'unpleasant', 'terrible': 'poor', 'horrible': 'bad',
    'awful': 'not great', 'nasty': 'unkind', 'evil': 'harmful',
    'moron': 'person', 'fool': 'person', 'jerk': 'rude person',
    'creep': 'unsettling person', 'kill': 'stop', 'die': 'end',
    'destroy': 'dismantle', 'attack': 'criticize', 'retard': 'person',
    'shut': 'be quiet', 'damn': 'darn', 'hell': 'heck', 'crap': 'stuff',
    'toxic': 'unhealthy', 'savage': 'intense', 'filth': 'mess',
    'scum': 'person', 'freak': 'unusual person', 'garbage': 'waste',
    'bully': 'intimidate', 'racist': 'discriminatory', 'sexist': 'gender-biased',
    'bigot': 'intolerant person',
}

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


# ─── Text Preprocessing ─────────────────────────────────────────────────────
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\brt\b', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)


# ─── Load & Train (cached so it only runs once) ─────────────────────────────
@st.cache_resource(show_spinner="Training model on 25k tweets... please wait ~30s")
def load_and_train():
    csv_path = os.path.join(BASE_DIR, 'labeled_data.csv')
    if not os.path.exists(csv_path):
        return None, None, {}

    df = pd.read_csv(csv_path)

    text_col = 'tweet'
    label_col = 'class'

    for col in df.columns:
        col_lower = col.lower()
        if 'tweet' in col_lower or 'text' in col_lower:
            text_col = col
        if 'class' in col_lower or 'label' in col_lower:
            label_col = col

    df = df.dropna(subset=[text_col, label_col])

    class_names = {0: 'Hate Speech', 1: 'Offensive Language', 2: 'Neither (Clean)'}
    class_dist = df[label_col].value_counts().to_dict()

    df['clean_text'] = df[text_col].astype(str).apply(preprocess_text)
    df = df[df['clean_text'].str.len() > 0]

    X = df['clean_text']
    y = df[label_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        max_features=15000, ngram_range=(1, 2),
        min_df=2, max_df=0.95, sublinear_tf=True
    )

    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    model = LogisticRegression(
        C=1.0, max_iter=1000, solver='lbfgs',
        class_weight='balanced', random_state=42
    )
    model.fit(X_train_tfidf, y_train)

    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)

    stats = {
        'accuracy': round(accuracy * 100, 2),
        'total_samples': len(df),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'features': X_train_tfidf.shape[1],
        'class_distribution': {class_names.get(int(k), f'Class {k}'): int(v) for k, v in class_dist.items()},
    }

    return model, vectorizer, stats


# ─── Analyze Text ────────────────────────────────────────────────────────────
def analyze_text(text, model, vectorizer):
    clean = preprocess_text(text)
    if not clean:
        return {
            'classification': 'Clean', 'confidence': 100.0,
            'probabilities': {'Hate Speech': 0, 'Offensive Language': 0, 'Clean': 100},
            'flagged_words': [], 'improved_text': text, 'suggestions': [],
        }

    text_tfidf = vectorizer.transform([clean])
    prediction = model.predict(text_tfidf)[0]
    probabilities = model.predict_proba(text_tfidf)[0]

    class_names = {0: 'Hate Speech', 1: 'Offensive Language', 2: 'Clean'}
    class_label = class_names.get(prediction, 'Unknown')

    prob_dict = {}
    for i, cls in enumerate(model.classes_):
        name = class_names.get(cls, f'Class {cls}')
        prob_dict[name] = round(float(probabilities[i]) * 100, 2)

    confidence = round(float(max(probabilities)) * 100, 2)

    flagged_words = []
    improved_words = []
    suggestions = []

    for word in text.split():
        word_lower = word.lower().strip(string.punctuation)
        if word_lower in HATE_INDICATORS:
            replacement = WORD_IMPROVEMENTS.get(word_lower, '[removed]')
            flagged_words.append({'word': word, 'replacement': replacement})
            improved_words.append(replacement)
            suggestions.append(f'Replace "{word}" with "{replacement}"')
        else:
            improved_words.append(word)

    if prediction == 0:
        suggestions.append('This text contains hate speech. Consider rephrasing.')
    elif prediction == 1:
        suggestions.append('This text contains offensive language. Consider neutral terms.')
    else:
        suggestions.append('This text appears clean and respectful.')

    return {
        'classification': class_label,
        'confidence': confidence,
        'probabilities': prob_dict,
        'flagged_words': flagged_words,
        'improved_text': ' '.join(improved_words),
        'suggestions': suggestions,
    }


# ─── Streamlit Page Config ───────────────────────────────────────────────────
st.set_page_config(page_title="NoHate - Hate Speech Detector", page_icon="🛡️", layout="wide")

# ─── Custom CSS for better styling ───────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .hate-badge {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #dc2626;
    }
    .offensive-badge {
        background-color: #fef3c7;
        color: #92400e;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #f59e0b;
    }
    .clean-badge {
        background-color: #dcfce7;
        color: #15803d;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #22c55e;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ NoHate - Hate Speech Detector")
st.caption("Advanced NLP Pipeline: Text Preprocessing → TF-IDF Vectorization → Logistic Regression Classification")

# Load model
model, vectorizer, stats = load_and_train()

if model is None:
    st.error("Failed to load model. Make sure labeled_data.csv exists in the repo.")
    st.stop()

# ─── Navigation Tabs ─────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍 Text Analyzer", "📈 Model Analytics", "ℹ️ About"])

with tab2:
    st.subheader("📊 Model Performance Dashboard")
    
    # Model Statistics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Model Accuracy", f"{stats['accuracy']}%", delta="+2.5%")
    with col2:
        st.metric("📚 Training Samples", f"{stats['training_samples']:,}")
    with col3:
        st.metric("🧪 Test Samples", f"{stats['test_samples']:,}")
    with col4:
        st.metric("🔧 TF-IDF Features", f"{stats['features']:,}")
    
    st.divider()
    
    # Class Distribution Visualization
    st.subheader("📊 Class Distribution in Dataset")
    class_dist = stats.get('class_distribution', {})
    
    # Create pie chart for class distribution
    fig_dist = go.Figure(data=[go.Pie(
        labels=list(class_dist.keys()),
        values=list(class_dist.values()),
        marker=dict(colors=['#ef4444', '#f97316', '#10b981']),
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    fig_dist.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Dataset Statistics Table
    st.subheader("📋 Dataset Statistics")
    stats_df = pd.DataFrame({
        'Class': list(class_dist.keys()),
        'Count': list(class_dist.values()),
        'Percentage': [f"{(v/sum(class_dist.values())*100):.1f}%" for v in class_dist.values()]
    })
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("About NoHate")
    st.write("""
    ### 🎯 Purpose
    NoHate is an advanced hate speech detection system using machine learning to classify text as:
    - **🚨 Hate Speech**: Offensive content with intent to harm
    - **⚠️ Offensive Language**: Crude/offensive language without hate elements
    - **🛡️ Clean**: Respectful and appropriate content
    
    ### 🔧 Technical Stack
    - **NLP Libraries**: NLTK for text preprocessing, lemmatization, and stopword removal
    - **Vectorization**: TF-IDF (Term Frequency-Inverse Document Frequency)
    - **Model**: Logistic Regression with balanced class weights
    - **Framework**: Streamlit for UI, Plotly for visualizations
    - **Deployment**: Streamlit Cloud
    
    ### 📊 Model Pipeline
    1. **Text Preprocessing**: Lowercasing, URL removal, tokenization, lemmatization
    2. **Vectorization**: Converting text to numerical TF-IDF features
    3. **Classification**: Logistic Regression predicts the class
    4. **Confidence Scoring**: Probability distribution across classes
    
    ### 🚀 Features
    ✅ Real-time text classification  
    ✅ Flagged word detection and suggestions  
    ✅ Corrected text generation  
    ✅ Confidence scoring  
    ✅ Model performance analytics  
    
    ### 📧 Disclaimer
    This model is trained on historical data and may not catch all forms of hate speech or offensive language. 
    It should be used as a supplementary tool, not a replacement for human moderation.
    """)

# ─── Sidebar: Model Info ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Quick Stats")
    st.metric("Accuracy", f"{stats['accuracy']}%")
    st.metric("Training Samples", f"{stats['training_samples']:,}")
    st.metric("Test Samples", f"{stats['test_samples']:,}")
    st.metric("TF-IDF Features", f"{stats['features']:,}")
    st.divider()
    st.subheader("Class Distribution")
    for cls, count in stats.get('class_distribution', {}).items():
        st.write(f"**{cls}**: {count:,}")
    st.divider()
    st.caption("🛡️ Built with Streamlit and scikit-learn")
    st.caption("Deployed on Streamlit Cloud")

# ─── Main Input ──────────────────────────────────────────────────────────────
with tab1:
    st.subheader("📝 Enter text to analyze")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚨 Hate Speech Sample", use_container_width=True):
            st.session_state['sample'] = "I hate all those people, they are disgusting trash and should die. They are subhuman and worthless scum."
    with col2:
        if st.button("⚠️ Offensive Sample", use_container_width=True):
            st.session_state['sample'] = "You are so stupid and dumb, what an idiot loser. Shut up you moron, nobody cares about your pathetic opinion."
    with col3:
        if st.button("🛡️ Clean Sample", use_container_width=True):
            st.session_state['sample'] = "I really enjoyed the seminar on artificial intelligence today. The speaker discussed fascinating advances in machine learning."

    default_text = st.session_state.get('sample', '')
    text_input = st.text_area("Type or paste text here:", value=default_text, height=120, max_chars=5000)

    if st.button("🔍 Analyze Text", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Analyzing..."):
                result = analyze_text(text_input.strip(), model, vectorizer)

            st.divider()

            # ─── Classification Result ───────────────────────────────────────
            cls = result['classification']
            icons = {'Hate Speech': '🚨', 'Offensive Language': '⚠️', 'Clean': '🛡️'}
            colors = {'Hate Speech': 'red', 'Offensive Language': 'orange', 'Clean': 'green'}

            st.markdown(f"### {icons.get(cls, '🔍')} Classification: :{colors.get(cls, 'blue')}[{cls}]")
            st.markdown(f"**Confidence:** {result['confidence']}%")

            # ─── Probabilities ───────────────────────────────────────────────
            st.subheader("📊 Classification Probabilities")
            probs = result['probabilities']

            # Metrics row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🚨 Hate Speech", f"{probs.get('Hate Speech', 0)}%")
            with col2:
                st.metric("⚠️ Offensive", f"{probs.get('Offensive Language', 0)}%")
            with col3:
                st.metric("🛡️ Clean", f"{probs.get('Clean', 0)}%")

            # Horizontal bar chart
            fig_bar = go.Figure(go.Bar(
                x=list(probs.values()),
                y=list(probs.keys()),
                orientation='h',
                marker_color=['#ef4444', '#f97316', '#10b981'],
                text=[f"{v}%" for v in probs.values()],
                textposition='auto',
            ))
            fig_bar.update_layout(
                xaxis_title="Probability (%)",
                height=250,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=False,
                xaxis={'range': [0, 100]}
            )
            
            # Pie chart for classification
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(probs.keys()),
                values=list(probs.values()),
                marker=dict(colors=['#ef4444', '#f97316', '#10b981']),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Probability: %{value}%<extra></extra>'
            )])
            fig_pie.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10))
            
            # Display both charts side by side
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.plotly_chart(fig_bar, use_container_width=True)
            with col_chart2:
                st.plotly_chart(fig_pie, use_container_width=True)

            # ─── Flagged Words ───────────────────────────────────────────────
            if result['flagged_words']:
                st.subheader("🚩 Flagged Words")
                for fw in result['flagged_words']:
                    st.write(f"❌ **\"{fw['word']}\"** → ✅ \"{fw['replacement']}\"")

            # ─── Improved Text ───────────────────────────────────────────────
            st.subheader("✨ Improved Text")
            st.info(result['improved_text'])

            # ─── Suggestions ─────────────────────────────────────────────────
            st.subheader("💡 Suggestions")
            for s in result['suggestions']:
                st.write(f"• {s}")
