# blackAI Resume ATS Checker
A simple Streamlit app that accepts a PDF, DOCX, or TXT resume and uses Google's Gemini Flash model to estimate ATS-style readability and provide practical feedback. Paste a job description to receive more relevant keyword and role-matching feedback.
Important: The score is an AI-generated estimate, not the score from a real applicant tracking system. Employers use different systems and criteria. Review all suggestions and never add skills or achievements you do not have.

Features
- Upload PDF, DOCX, or TXT resumes
- Optional job description matching
- Estimated score from 0–100
- Strengths, actionable improvements, keyword gaps, and formatting checks
- Example resume bullet rewrites that must be verified by the user
- Download results as JSON
1. Create a Gemini API key
Create an API key in Google AI Studio. Keep it private; do not paste it into app.py or commit it to GitHub.
2. Run locally on Windows
Install Python 3.10 or newer, then open Command Prompt in this project folder and run:
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
Create a folder named .streamlit, then create .streamlit/secrets.toml inside it with:
GEMINI_API_KEY = "paste-your-real-api-key-here"
Run the app:
streamlit run app.py
Keep .streamlit/secrets.toml private. Do not upload it to GitHub.
3. Files
ats-resume-checker/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
Suggested .gitignore contents:
.venv/
__pycache__/
*.py[cod]
.streamlit/secrets.toml
.env
4. Upload the project to GitHub using the website UI
1. Sign in at GitHub and click + → New repository.
2. Give it a name such as ats-resume-checker, choose Public or Private, and click Create repository.
3. In the new repository, choose Add file → Create new file.
4. Enter app.py as the filename, paste the contents of your local app.py, and commit the file.
5. Repeat Add file → Create new file for requirements.txt and README.md.
6. Add .gitignore too, using the contents above.
7. Do not upload .streamlit/secrets.toml or expose your API key.
If GitHub's editor is inconvenient for large files, you can use Add file → Upload files and drag in app.py, requirements.txt, README.md, and .gitignore together.
5. Deploy on Streamlit Community Cloud
1. Open Streamlit Community Cloud and sign in with GitHub.
2. Click Create app (or Deploy an app) and select your repository, branch (usually main), and main file path app.py.
3. Before deploying or from the app's settings, open Advanced settings / Secrets (label may vary).
4. Add this secret, replacing the placeholder with your actual key:
   GEMINI_API_KEY = "paste-your-real-api-key-here"
5. Deploy the app and wait for the build to finish. Streamlit installs dependencies from requirements.txt.
6. If deployment fails, open the app's logs and check for missing packages, an invalid secret, or API quota/model-access errors.
Testing and limitations
- app.py is syntax-checked with Python's compiler before release.
- The resume text-extraction and Gemini call should also be tested locally with sample files and a valid API key. A live Gemini request requires internet access and a valid key, and is not guaranteed by a syntax check.
- Scanned/image-only PDFs may not contain extractable text. Run OCR first and upload a searchable PDF.
- The app sends extracted resume text and any pasted job description to Google's Gemini API for analysis. Do not upload sensitive documents unless you are comfortable with that processing and the provider's current terms.
- The app truncates very long resume/job-description text to keep the prompt bounded.
