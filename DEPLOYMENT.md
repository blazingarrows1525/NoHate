# 🚀 NoHate - Deployment Guide

## Table of Contents
1. [Streamlit Cloud Deployment (Recommended)](#streamlit-cloud-deployment)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Traditional Hosting](#traditional-hosting)

---

## Streamlit Cloud Deployment (Recommended)

### Why Streamlit Cloud?
✅ Free tier available  
✅ Easy one-click deployment  
✅ Automatic rebuilds on GitHub push  
✅ Perfect for Streamlit apps  
✅ Built-in sharing & analytics  

### Prerequisites
- GitHub account with repository
- Streamlit Cloud account (free signup)

### Step-by-Step Instructions

#### 1. Prepare Your Repository
Ensure your GitHub repo has:
```
NoHate/
├── streamlit_app.py          ← Main app file
├── requirements.txt          ← All dependencies
├── labeled_data.csv          ← Training data (must be present)
├── .streamlit/
│   └── config.toml          ← Streamlit configuration
└── README.md                ← Project documentation
```

#### 2. Verify Files
**streamlit_app.py**
- Must start with: `import streamlit as st`
- Must define all imports correctly
- Should use `@st.cache_resource` for model loading

**requirements.txt** (example)
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
scikit-learn>=1.3.0
nltk>=3.8.0
plotly>=5.17.0
```

#### 3. Push to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

#### 4. Deploy on Streamlit Cloud
1. Visit [Streamlit Cloud](https://streamlit.io/cloud)
2. Click **"New app"** button
3. Select:
   - Repository: your GitHub repo
   - Branch: `main`
   - File path: `streamlit_app.py`
4. Click **"Deploy"** and wait 2-5 minutes

#### 5. Access Your App
Once deployed, you'll get a URL like:
```
https://yourusername-nohate-xxxxx.streamlit.app/
```

Share this URL with others!

---

## Local Development

### Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-username/NoHate.git
cd NoHate
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Download NLTK Data (First Time Only)
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

#### 5. Run the App
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

### Troubleshooting Local Setup

**Issue**: `ModuleNotFoundError: No module named 'streamlit'`
```bash
# Make sure virtual environment is activated
# Then reinstall requirements
pip install -r requirements.txt
```

**Issue**: NLTK data not found
```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet')"
```

**Issue**: Port 8501 already in use
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

## Docker Deployment

### Build Docker Image

#### 1. Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download NLTK data
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2. Build & Run
```bash
# Build image
docker build -t nohate:latest .

# Run container
docker run -p 8501:8501 nohate:latest

# Access at: http://localhost:8501
```

#### 3. Deploy to Docker Hub
```bash
# Login
docker login

# Tag image
docker tag nohate:latest yourusername/nohate:latest

# Push
docker push yourusername/nohate:latest
```

---

## Traditional Hosting

### Option 1: Render.com (Simple)

1. **If using Flask API** (app.py)
2. **Create render.yaml**:
```yaml
services:
  - type: web
    name: nohate-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.13
```

3. **Push to GitHub and deploy** on Render.com

### Option 2: Heroku (Deprecated but may still work)

```bash
# Login
heroku login

# Create app
heroku create your-app-name

# Set Python version
echo 'python-3.10.13' > runtime.txt

# Deploy
git push heroku main
```

### Option 3: DigitalOcean / AWS / Azure

```bash
# Push code to server
git clone <repo> /var/www/nohate

# SSH into server and setup
cd /var/www/nohate
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app:app -w 4 -b 0.0.0.0:8000

# Or run Streamlit
streamlit run streamlit_app.py --server.port 8000
```

---

## Environment Configuration

### .streamlit/config.toml
```toml
[theme]
primaryColor = "#ef4444"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = true
maxUploadSize = 200

[server]
maxUploadSize = 200
headless = true
```

### requirements.txt Best Practices
```
# Always pin versions for reproducibility
streamlit==1.28.1
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
nltk==3.8.1
plotly==5.17.0
```

---

## Performance Tips

### For Streamlit Cloud
- Use `@st.cache_resource` for expensive operations
- Set `max_retries=3` for API calls
- Use `st.write()` instead of print statements
- Compress large files

### Optimization Checklist
- [ ] Model loading with caching
- [ ] NLTK data included/downloaded
- [ ] requirements.txt has exact versions
- [ ] Remove unnecessary dependencies
- [ ] Test locally first
- [ ] Check .gitignore (no data in repo)

---

## Monitoring & Logs

### Streamlit Cloud
1. Go to app settings
2. View "Logs" tab
3. Check for errors and warnings

### Docker
```bash
# View logs
docker logs <container-id>

# Follow logs in real-time
docker logs -f <container-id>
```

### Server (SSH)
```bash
# View Streamlit logs
tail -f ~/.streamlit/logs.txt

# Check app status
ps aux | grep streamlit
```

---

## Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| App crashes after deploy | Check Streamlit logs for import errors |
| Slow initial load | Use `@st.cache_resource` for model |
| CSV file not found | Ensure `labeled_data.csv` in repo root |
| NLTK data missing | Add separate download step in startup |
| Out of memory | Reduce `max_features` in TfidfVectorizer |
| High latency | Enable server caching and compression |

---

## Security Considerations

- [ ] Don't commit sensitive data (use `.gitignore`)
- [ ] Use environment variables for secrets
- [ ] Keep dependencies updated
- [ ] Use HTTPS for production
- [ ] Add authentication if needed

---

## Next Steps

1. ✅ Verify all files are present
2. ✅ Test locally: `streamlit run streamlit_app.py`
3. ✅ Push to GitHub
4. ✅ Deploy to Streamlit Cloud
5. ✅ Share the public URL!

---

## Support

For issues:
- Check [Streamlit docs](https://docs.streamlit.io)
- Search GitHub issues
- Review error logs
- Test locally before deploying

Happy Deploying! 🚀
