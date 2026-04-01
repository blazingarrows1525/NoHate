# 🚀 Quick Start Guide

## Local Development (5 minutes)

```bash
# 1. Clone or navigate to project
cd NoHate

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
streamlit run streamlit_app.py
```

**Access**: Open browser to `http://localhost:8501`

---

## Deploy on Streamlit Cloud (3 minutes)

1. **Ensure files are committed to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Go to**: https://streamlit.io/cloud

3. **Click**: "New app"

4. **Fill in**:
   - Repository: your-repo
   - Branch: main
   - File: streamlit_app.py

5. **Click**: "Deploy"

6. **Wait**: 2-5 minutes

7. **Share**: Get public URL and share!

---

## Features Overview

### Main Interface (Text Analyzer Tab)
- Enter any text
- Click "Analyze Text"
- Get instant results with visualizations
- See flagged words and suggestions
- Get improved version of text

### Analytics Tab
- View model accuracy
- See class distribution
- Check dataset statistics
- Understand model performance

### Sample Buttons
- Test with pre-built samples
- Quick way to explore capabilities

---

## What You Get

✅ **Real-time Analysis** - Instant hate speech detection  
✅ **Beautiful Charts** - Interactive pie and bar charts  
✅ **Smart Suggestions** - Auto-generated improvement tips  
✅ **Model Stats** - View training metrics and accuracy  
✅ **Responsive Design** - Works on desktop and mobile  

---

## Troubleshooting

### Issue: App won't start
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: NLTK data missing
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
```

### Issue: Port 8501 in use
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

## File Structure

```
NoHate/
├── streamlit_app.py       ← Main application
├── labeled_data.csv       ← Training data
├── requirements.txt       ← Dependencies
├── README.md             ← Full documentation
├── DEPLOYMENT.md         ← Deployment guide
├── .streamlit/
│   └── config.toml       ← Configuration
└── .gitignore            ← Git ignore rules
```

---

## Key Dependencies

| Library | Purpose |
|---------|---------|
| **streamlit** | Web UI framework |
| **plotly** | Interactive charts |
| **scikit-learn** | ML model |
| **nltk** | Text processing |
| **pandas** | Data handling |
| **numpy** | Numerical ops |

---

## Common Commands

```bash
# Run app
streamlit run streamlit_app.py

# Run with custom port
streamlit run streamlit_app.py --server.port 8502

# View logs
streamlit logs

# Clear cache
streamlit cache clear
```

---

## Quick Tips

💡 Use sample buttons for quick testing  
💡 Charts are interactive - hover for details  
💡 Confidence score shows model certainty  
💡 Flagged words show problematic content  
💡 Analytics tab shows model capabilities  

---

## Need Help?

📖 Full guide: See README.md  
🚀 Deployment: See DEPLOYMENT.md  
📊 Enhancements: See ENHANCEMENTS.md  
🔧 Issues: Check GitHub issues  

---

**Happy analyzing!** 🛡️
