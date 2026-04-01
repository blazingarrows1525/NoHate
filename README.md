# NoHate - 🛡️ Hate Speech Detection System

AI-powered **Hate Speech Detection** system using machine learning and Natural Language Processing (NLP) to classify text as hate speech, offensive language, or clean content.

## 🎯 Overview

NoHate uses a Logistic Regression model trained on TF-IDF vectorized text to accurately detect hate speech and offensive language in real-time. The system provides:

- **Real-time Classification**: Instant text analysis with confidence scores
- **Multi-class Detection**: Hate Speech, Offensive Language, or Clean content
- **Word Flagging**: Identifies and suggests replacements for harmful language
- **Interactive Dashboard**: Model performance metrics and analytics
- **Beautiful Visualizations**: Charts, graphs, and probability distributions using Plotly

## 🚀 Live Demo

**Access on Streamlit Cloud**: [NoHate Hate Speech Detector](https://nohate-detector.streamlit.app/)

## 🧠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend/UI** | Streamlit |
| **ML Framework** | Scikit-learn |
| **NLP** | NLTK (Natural Language Toolkit) |
| **Vectorization** | TF-IDF |
| **Visualizations** | Plotly |
| **Backend API** | Flask (optional) |

## 📊 Model Details

### Pipeline Architecture
```
User Input
    ↓
Text Preprocessing (cleanup, tokenization, lemmatization)
    ↓
TF-IDF Vectorization (15,000 features, bigrams)
    ↓
Logistic Regression Classification
    ↓
Probability Distribution & Confidence Score
```

### Model Performance
- **Accuracy**: ~94-96% (varies with dataset)
- **Training Samples**: ~25,000 tweets
- **Features**: 15,000 TF-IDF terms (unigrams + bigrams)
- **Classes**: 3 (Hate Speech, Offensive Language, Clean)

### Text Preprocessing Steps
1. **Lowercasing**: Convert to lowercase
2. **URL/Social Media Cleanup**: Remove URLs, mentions, retweets
3. **Tokenization**: Split into words
4. **Lemmatization**: Reduce words to base form
5. **Stopword Removal**: Filter common words
6. **Min Length**: Keep only words with 3+ characters

## 🎨 Features

✅ **Real-time Text Analysis** - Classify text instantly  
✅ **Confidence Scoring** - Probability distribution for each class  
✅ **Word Suggestions** - Automatically suggest better word choices  
✅ **Improved Text Generation** - Generate cleaner versions of input  
✅ **Interactive Visualizations** - Bar charts, pie charts, metrics  
✅ **Model Analytics Dashboard** - View training statistics  
✅ **Sample Buttons** - Quick testing with pre-filled samples  

## 📈 Dashboard Features

### Text Analyzer Tab
- Input box for text analysis
- Pre-built sample buttons (Hate Speech, Offensive, Clean)
- Classification result with confidence
- Probability distribution (bar & pie charts)
- Flagged words with suggestions
- Improved text generation

### Model Analytics Tab
- Model accuracy metric
- Training/test sample counts
- Feature count statistics
- Class distribution pie chart
- Dataset statistics table

### About Tab
- System purpose and features
- Technical stack details
- Model pipeline explanation
- Disclaimer about limitations

## 📥 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NoHate
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Streamlit app**
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Access the app**
   - Open browser to `http://localhost:8501`

## 🌐 Deployment on Streamlit Cloud

### Step 1: Prepare Repository
Ensure your GitHub repository contains:
- `streamlit_app.py` (main app file)
- `requirements.txt` (dependencies)
- `labeled_data.csv` (training data)
- `.streamlit/config.toml` (configuration)

### Step 2: Deploy to Streamlit Cloud
1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Select your GitHub repository
4. Choose the branch (main)
5. Set main file path to `streamlit_app.py`
6. Click "Deploy"

### Step 3: Configure Resources (if needed)
- Go to App settings
- Adjust timeout and memory if required
- Set any required environment variables

### Step 4: Share Your App
- Get the public URL: `https://<your-username>-nohate-<hash>.streamlit.app/`
- Share with others!

## 🐳 Alternative Deployment Options

### Docker
```bash
docker build -t nohate .
docker run -p 8501:8501 nohate
```

### Render.com (Flask API)
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

## 📚 Project Structure

```
NoHate/
├── streamlit_app.py          # Main Streamlit application
├── app.py                    # Flask API (optional)
├── labeled_data.csv          # Training dataset
├── requirements.txt          # Python dependencies
├── runtime.txt              # Specify Python version
├── Procfile                 # Heroku deployment config
├── render.yaml              # Render.com deployment config
├── .streamlit/
│   ├── config.toml         # Streamlit configuration
│   └── secrets.toml        # Secrets (not in repo)
├── static/
│   ├── index.html          # HTML interface (optional)
│   ├── style.css           # Styling (optional)
│   └── script.js           # Frontend logic (optional)
└── README.md               # This file
```

## 🔧 Configuration

### Streamlit Config (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#ef4444"
backgroundColor = "#ffffff"
textColor = "#262730"

[server]
maxUploadSize = 200
headless = true
```

## 💡 Usage Examples

### Basic Usage
1. Open the app
2. Enter text in the text box
3. Click "Analyze Text"
4. View results with visualizations

### Using Samples
- Click "Hate Speech Sample" for example hate speech
- Click "Offensive Sample" for example offensive language
- Click "Clean Sample" for example clean text

### Interpreting Results
- **High Hate Speech %**: Text contains hate speech elements
- **High Offensive %**: Text contains offensive language
- **High Clean %**: Text appears respectful and appropriate

## ⚠️ Limitations & Disclaimer

- Model trained on Twitter data from specific time period
- May not catch all forms of hate speech or offensive language
- Cultural/contextual variations in different regions
- Should be used as supplementary tool, not replacement for human moderation
- Update regularly with new data to maintain accuracy

## 📊 Sample Results

### Example 1: Hate Speech
```
Input: "I hate all those people"
Classification: Hate Speech (92% confidence)
Flagged Words: hate
Suggestion: Use more neutral language
```

### Example 2: Offensive Language
```
Input: "You're so stupid"
Classification: Offensive Language (87% confidence)  
Flagged Words: stupid
Suggestion: Consider respectful tone
```

### Example 3: Clean Text
```
Input: "I enjoyed the presentation"
Classification: Clean (98% confidence)
Flagged Words: None
Suggestion: Text appears appropriate
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📝 License

This project is open source. Please refer to LICENSE file for details.

## 📧 Support & Feedback

For issues, questions, or suggestions:
- Open a GitHub issue
- Contact: [your-email@example.com]

## 🙏 Acknowledgments

- Dataset: Twitter Hate Speech Detection Dataset
- Libraries: Streamlit, Scikit-learn, NLTK, Plotly
- Inspiration: Making the internet safer

---

**⚡ Last Updated**: April 2026  
**Version**: 2.0 (Enhanced with Visualizations & Streamlit Cloud)

