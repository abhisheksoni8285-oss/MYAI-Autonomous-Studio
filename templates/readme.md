# 🤖 MYAI Autonomous Studio (Flask & Gemini 3.8 Flash)

यह एक Autonomous AI Coding Studio है जो User Prompt के आधार पर वेब ऐप/UI तैयार करता है और उसे लाइव प्रीव्यू (Split Screen View) में दिखाता है।

---

## 📂 Project Structure Overview

AutonaumasAgentNew/
├── venv/                      # Virtual Environment
├── .env                       # Environment Variables (GEMINI_API_KEY)
├── .gitignore                 # Files to exclude from Git
├── app.py                     # Main Flask Server & Gemini API Backend
├── requirements.txt           # Python Package Dependencies
├── Procfile                   # Render Server Startup Configuration
├── vercel.json                # Vercel Deployment Config (Optional)
├── templates/
│   └── index.html             # UI Dashboard (Split Screen View)
└── static/
    └── preview.html           # Live Generated App Output