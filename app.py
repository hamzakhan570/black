                parts.append(" | ".join(cell.text.strip() for cell in row.cells))
        text = "\n".join(parts)
    elif filename.endswith(".txt"):
        text = uploaded_file.getvalue().decode("utf-8", errors="replace")
    else:
        raise ValueError("Unsupported file type. Upload a PDF, DOCX, or TXT file.")

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError(
            "No readable text was found. If this is a scanned PDF, run OCR on it and upload the searchable PDF."
        )
    return text


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets first, then environment variables."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY")


def analyze_resume(resume_text: str, job_description: str, api_key: str) -> dict[str, Any]:
    client = genai.Client(api_key=api_key)
    prompt = f"""
You are a careful resume reviewer. Analyze the resume against the job description, if one is provided.
Return ONLY valid JSON with these keys:
- ats_score: integer from 0 to 100
- score_explanation: short string explaining that this is an estimate
- strengths: array of 3 to 6 concise strings
- improvements: array of 4 to 8 actionable strings
- missing_keywords: array of relevant keywords or skills not clearly evidenced in the resume
- formatting_checks: array of concise observations about ATS readability, sections, dates, and layout
- summary: concise overall assessment
- rewritten_bullet_examples: array of up to 3 improved resume bullet examples; do not invent achievements or numbers

Rules:
- If no job description is provided, score general resume clarity and ATS readability, and state that job-specific matching cannot be assessed.
- Do not claim to know the score from any real ATS product.
- Do not infer protected traits or judge the applicant based on them.
- Never invent qualifications, employers, credentials, metrics, or accomplishments. Mark any example needing user verification.
- Keep feedback respectful, specific, and practical.

RESUME TEXT:
{resume_text[:24000]}

JOB DESCRIPTION:
{job_description[:12000] if job_description.strip() else "Not provided."}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    raw = (response.text or "").strip()
    if not raw:
        raise RuntimeError("Gemini returned an empty response. Please try again.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Some model responses may include a fenced JSON block despite the response setting.
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise RuntimeError("The AI response was not valid JSON. Please try again.")
        data = json.loads(match.group(0))

    score = data.get("ats_score")
    if not isinstance(score, (int, float)):
        raise RuntimeError("The AI response did not contain a numeric ATS score. Please try again.")
    data["ats_score"] = max(0, min(100, int(score)))
    for key in ("strengths", "improvements", "missing_keywords", "formatting_checks", "rewritten_bullet_examples"):
        if not isinstance(data.get(key), list):
            data[key] = []
    return data


with st.sidebar:
    st.header("How to use")
    st.markdown("1. Upload a resume.\n2. Optionally paste the target job description.\n3. Click **Analyze resume**.")
    st.markdown("**Supported formats:** PDF, DOCX, TXT")
    st.markdown("**Privacy tip:** Avoid uploading information you do not want processed by an external AI service.")

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
job_description = st.text_area(
    "Target job description (optional)",
    height=180,
    placeholder="Paste the job description here for a more relevant keyword and match analysis...",
)

if st.button("Analyze resume", type="primary", use_container_width=True):
    if uploaded_file is None:
        st.error("Please upload your resume first.")
    else:
        api_key = get_api_key()
        if not api_key:
            st.error("Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets or your environment variables.")
        else:
            try:
                with st.spinner("Reading your resume and generating feedback..."):
                    resume_text = extract_text(uploaded_file)
                    result = analyze_resume(resume_text, job_description, api_key)
                st.session_state["analysis_result"] = result
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

result = st.session_state.get("analysis_result")
if result:
    st.divider()
    st.header("Your results")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Estimated ATS score", f"{result['ats_score']}/100")
        st.progress(result["ats_score"] / 100)
    with col2:
        st.subheader("Overall assessment")
        st.write(result.get("summary", "No summary provided."))
        st.caption(result.get("score_explanation", "AI-generated estimate; results vary by employer and ATS."))

    sections = [
        ("Strengths", "strengths"),
        ("Recommended improvements", "improvements"),
        ("Missing or underrepresented keywords", "missing_keywords"),
        ("ATS formatting checks", "formatting_checks"),
        ("Suggested bullet rewrites", "rewritten_bullet_examples"),
    ]
    for title, key in sections:
        st.subheader(title)
        items = result.get(key, [])
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.write("No items returned.")

    st.download_button(
        "Download analysis as JSON",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="resume_ats_analysis.json",
        mime="application/json",
        use_container_width=True,
    )
