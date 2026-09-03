# ResumeFit - ATS Resume Analyzer 📄✨

**ResumeFit** is a clean, lightweight, and modern web application designed to evaluate resumes against job descriptions for Applicant Tracking System (ATS) compatibility.

---

## 🚀 Key Features

1. **PDF Resume Text Extraction**: Drag-and-drop or select any standard PDF resume to extract content cleanly.
2. **Target Job Description Matching**: Compare the resume directly against the job requirements, responsibilities, and qualifications.
3. **Overall ATS Compatibility Score (0 - 100)**:
   - **Target Keyword Match Rate (50% weight)**
   - **Technical & Hard Skills Match (25% weight)**
   - **Structure & Standard Section Presence (15% weight)**
   - **Action Verbs & Measurable Metrics (10% weight)**
4. **Actionable Improvement Areas**:
   - High, medium, and low priority improvement cards.
   - Missing core technical skills and target domain keywords.
   - Section structure warnings and quantifiable impact tips.
5. **Matched vs. Missing Keyword Chips**: Visual badges indicating exact skills found vs. skills to add.
6. **Built-in Sample Loader**: Test instantly with 1-click sample data even without an immediate PDF.
7. **100% Local & Private**: No external API keys, database, login, or tracking required.

---

## 📁 Project Structure

```
RESUME-FIT/
├── app.py                  # Flask backend server and REST API routes (/api/analyze, /api/sample)
├── analyzer.py             # Core ATS scoring and keyword extraction engine
├── requirements.txt        # Minimal Python dependencies (Flask, pypdf)
├── run.bat                 # 1-click launcher script for Windows
├── templates/
│   └── index.html          # Clean, semantic HTML5 interface
├── static/
│   ├── css/
│   │   └── style.css       # Modern, responsive UI stylesheet
│   └── js/
│       └── main.js         # Client-side controller (drag & drop, score gauge animation, chip rendering)
├── test_analyzer.py        # Automated test suite
└── README.md               # Project documentation
```

---

## 🛠️ How to Run Locally

### Option A: 1-Click Launch on Windows
Double-click `run.bat`. It will check dependencies and automatically open `http://127.0.0.1:5000` in your default browser.

---

### Option B: Manual Command Line Launch

1. Open your terminal / command prompt locate for the file
2. 2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask application:
   ```bash
   python app.py
   ```
4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 🧪 Running Automated Tests

To run the unit test suite verifying the ATS algorithm and API endpoints:

```bash
python test_analyzer.py
```
