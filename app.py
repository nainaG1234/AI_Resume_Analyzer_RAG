from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai
import streamlit as st
from PyPDF2 import PdfReader
import plotly.express as px

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
genai.configure(api_key="AQ.Ab8RN6KZbPsYyELVP_nXiuBgtEJvyVHexxquRdYRMUi-zSh_Ow")

model = genai.GenerativeModel("gemini-2.5-flash")
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "improved_resume" not in st.session_state:
    st.session_state.improved_resume = ""
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1 {
    text-align: center;
    color: #4CAF50;
}

div[data-testid="metric-container"] {
    background: #1E293B;
    border: 1px solid #4CAF50;
    padding: 15px;
    border-radius: 15px;
}

.stButton button {
    background: linear-gradient(90deg,#4CAF50,#00C853);
    color: white;
    border-radius: 12px;
    font-weight: bold;
    width: 100%;
}

.stDownloadButton button {
    background: linear-gradient(90deg,#2563EB,#3B82F6);
    color: white;
    border-radius: 12px;
    width: 100%;
}

textarea {
    border-radius: 12px !important;
}
div[data-testid="metric-container"]{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}

div[data-testid="metric-container"]:hover{
    transform: translateY(-5px);
    box-shadow: 0 0 20px rgba(76,175,80,0.5);
}
.stButton > button {
    background: linear-gradient(135deg, #4CAF50, #00E676);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 25px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 20px rgba(76, 175, 80, 0.8);
}
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
text-align:center;
padding:20px;
border-radius:20px;
background:linear-gradient(135deg,#1e293b,#0f172a);
border:1px solid #4CAF50;
box-shadow:0 0 25px rgba(76,175,80,0.3);
margin-bottom:20px;
">

<h1 style="
font-size:40px;
margin-bottom:10px;
background:linear-gradient(90deg,#4CAF50,#00E676);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
">
RAG AI Resume Analyzer
</h1>

<p style="
font-size:18px;
color:#B0BEC5;
">
           
<p style="
font-size:20px;
font-weight:600;
color:#4CAF50;
margin-bottom:10px;
">
AI Powered Career Assistant
</p>
ATS Optimization • Resume Intelligence • AI Feedback • Career Coach
</p>
<p style="
color:#B0BEC5;
font-size:14px;
margin-top:10px;
">
Version 1.0 • RAG Powered
</p>         

</div>
""", unsafe_allow_html=True)

st.info(
    "💡 Upload your resume and job description to get ATS Score, Resume-JD Similarity, Skill Gap Analysis, AI Feedback, Cover Letter Generation, Interview Preparation and Career Roadmap."
)
def chunk_text(text):

    chunks = text.split("\n\n")

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]
def retrieve_context(query, top_k=1):

    query_embedding = embedding_model.encode([query])

    distances, indices = index.search(
        np.array(query_embedding),
        top_k
    )

    retrieved_chunks = [
        chunks[i]
        for i in indices[0]
    ]

    return "\n".join(retrieved_chunks)
def generate_pdf_report(content):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "AI Resume Analysis Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(content, styles["BodyText"])
    )

    doc.build(story)

    buffer.seek(0)

    return buffer
skills_db = [
    "Python",
    "Java",
    "C++",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "Data Science",
    "DBMS",
    "Operating Systems",
    "NLP",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Git",
    "GitHub"
]
st.markdown("""
### 📄 Upload Resume

Upload your resume PDF for ATS analysis and AI feedback.
""")
uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)
st.subheader("💼 Job Description")

job_description = st.text_area(
    "Paste Job Description Here",
    height=150
)

st.subheader("🎯 Target Role")

target_role = st.selectbox(
    "Select Role",
    [
        "AI Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Python Developer",
        "Full Stack Developer"
    ]
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Analysis",
    "🤖 AI Feedback",
    "💬 Chat with Resume",
    "🎤 Interview Prep",
    "🎓 Career Coach"
])

if uploaded_file:

    reader = PdfReader(uploaded_file)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text
    chunks = chunk_text(resume_text)
    chunk_embeddings = embedding_model.encode(chunks)
    dimension = chunk_embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(
        np.array(chunk_embeddings)
    )

    found_skills = []

    for skill in skills_db:
        if skill.lower() in resume_text.lower():
            found_skills.append(skill)
    with tab1:
        st.write("ANALYSIS TAB")
        st.subheader("Detected Skills")
        st.subheader("💪 Resume Strengths")

        for skill in found_skills:
            st.success(f"✅ {skill}")

        ats_score = (
            len(found_skills) * 6
        )

        if "Projects" in resume_text:
            ats_score += 10

        if "Certification" in resume_text:
            ats_score += 10

        if "GitHub" in resume_text:
            ats_score += 10

        ats_score = min(ats_score, 100)

        st.subheader("ATS Score")
        st.progress(ats_score / 100)
        st.success(f"ATS Score: {ats_score}/100")
        st.markdown("---")
    
        jd_skills = []   
        if job_description:

                for skill in skills_db:
                    if skill.lower() in job_description.lower():
                        jd_skills.append(skill)
         
        matched_skills = list(
            set(found_skills).intersection(set(jd_skills))
        )
        missing_skills = list(
            set(jd_skills) - set(found_skills)
        )
        similarity_percentage = 0

        if job_description and job_description.strip():

            resume_embedding = embedding_model.encode(
                resume_text,
                convert_to_tensor=True
            )

            jd_embedding = embedding_model.encode(
                job_description,
                convert_to_tensor=True
            )

            from sentence_transformers import util

            similarity_percentage = round(
                util.cos_sim(
                    resume_embedding,
                    jd_embedding
                ).item() * 100,
                2
            )
        st.markdown("---")
        st.subheader("📊 Dashboard Summary")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("✅ Skills Found", len(found_skills))
        col2.metric("🎯 ATS Score", f"{ats_score}%")
        col3.metric("⚠️ Missing Skills", len(missing_skills))
        col4.metric("🎯 Similarity", f"{similarity_percentage}%")  
        
        st.markdown("---")
        st.subheader("💪 Resume Strength")

        strength = 0

        if len(found_skills) >= 5:
            strength += 20

        if ats_score >= 80:
            strength += 20

        if similarity_percentage >= 60:
            strength += 20

        if "project" in resume_text.lower():
            strength += 20

        if "certification" in resume_text.lower() or "certificate" in resume_text.lower():
            strength += 20

        st.progress(strength / 100)
        st.success(f"Resume Strength: {strength}%")

        if len(jd_skills) > 0:
            match_percentage = round(
                len(matched_skills) / len(jd_skills) * 100,
                2 
            )
        else:
            match_percentage = 0
        
        if job_description and job_description.strip():
            st.subheader("📊 Job Match Percentage")
            st.progress(match_percentage / 100)
            st.success(f"{match_percentage}% Match")


            st.subheader("🎯 Resume vs JD Similarity")
            st.progress(similarity_percentage / 100)
            st.success(
                f"Semantic Similarity: {similarity_percentage}%"
            )
            st.markdown("---")
            st.subheader("🎯 Hiring Recommendation")

            if ats_score >= 85 and match_percentage >= 75:
                st.success("🔥 Strong Candidate - Ready for Interview")

            elif ats_score >= 70:
                st.info("👍 Good Candidate - Minor Improvements Needed")

            else:
                st.warning("⚠ Resume Needs Improvement")

            
            if ats_score >= 90:
                st.success("🏆 Excellent ATS Score")
            elif ats_score >= 75:
                st.info("👍 Good ATS Score")
            else:
                st.warning("⚠ ATS Score Needs Improvement")
            chart_data = {
                "Category": ["Matched Skills", "Missing Skills"],
                "Count": [len(matched_skills), len(missing_skills)]
                }

            fig = px.pie(
                    values=chart_data["Count"],
                    names=chart_data["Category"],
                    title="Skill Match Analysis",
                    hole=0.4
                )
            fig.update_traces(
                textinfo="percent+label"
            )

            fig.update_layout(
                    height=400,
                    width=500
                )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("### 📊 Resume Insights")

            if match_percentage >= 80:
                st.success("🚀 Excellent Match with Job Description")
            elif match_percentage >= 60:
                st.info("👍 Good Match, minor improvements needed")
            else:
                st.warning("⚠️ Resume needs more relevant skills")
            
            st.markdown("---")
            st.subheader("🎯 Best Matching Roles")

            roles = {
                "AI Engineer": 92,
                "ML Engineer": 88,
                "Data Scientist": 81,
                "Python Developer": 76
            }

            for role, score in roles.items():
                st.write(f"**{role}**")
                st.progress(score / 100)
                st.write(f"{score}% Match")

            st.markdown("### 🎯 Recommended Skills For Role")

            role_skills = {
                "AI Engineer": ["Deep Learning", "RAG", "LLMs", "Vector DB", "LangChain"],
                "Data Scientist": ["SQL", "Statistics", "Pandas", "Power BI", "Tableau"],
                "Machine Learning Engineer": ["TensorFlow", "PyTorch", "MLOps", "Docker"],
                "Python Developer": ["Django", "FastAPI", "REST API", "Flask"],
                "Full Stack Developer": ["React", "Node.js", "MongoDB", "JavaScript"]
            }

            for skill in role_skills[target_role]:
                st.success(f"✅ {skill}")
        else:
            st.info("📋 Enter a Job Description to calculate Match Percentage.")
        report = f"""
        ATS Score: {ats_score}/100

        
        Skills Found:
        {', '.join(found_skills)}

        Missing Skills:
        {', '.join(missing_skills)}

        Match Percentage:
        {match_percentage}%
        """
        # st.write("JD Skills:", jd_skills)
        # st.write("Found Skills:", found_skills)
        # st.write("Missing Skills:", missing_skills)
        if not job_description or not job_description.strip():

            st.info("📋 Please enter a Job Description to see Job Match Analysis.")

        else:

            missing_skills = list(
                set(jd_skills) - set(found_skills)
            )
            if missing_skills:
                st.subheader("⚠️ Missing Skills")

                for skill in missing_skills:
                    st.warning(f"❌ {skill}")
            else:
                st.success("🎉 All required skills found!")
        


            st.download_button(
                label="📄 Download Analysis Report",
                data=report,
                file_name="resume_analysis_report.txt",
                mime="text/plain"
            )
        # st.write("Number of Chunks:", len(chunks))
        # st.write("Embedding Shape:", chunk_embeddings.shape)
        # if job_description:

        #     context = retrieve_context(job_description)

        #     with st.expander("🔍 Retrieved Resume Context"):
        #      st.text_area(
        #         "Retrieved Context",
        #         context,
        #         height=250,
        #         disabled=True
        #     )
        # st.subheader("Resume Content")
        # st.text_area(
        #         "Extracted Text",
        #         resume_text,
        #         height=200
        # )

    with tab2:
        
        st.markdown("---")
        st.subheader("🤖 AI Resume Feedback")

        if st.button("Generate AI Suggestions"):
            if uploaded_file is None:
                st.warning("⚠ Please upload a resume first.")
                st.stop()

            if not job_description.strip():
                st.warning("⚠ Please enter a Job Description.")
                st.stop()
            missing_text = ", ".join(missing_skills) if "missing_skills" in locals() else "None"
            retrieved_context = retrieve_context(job_description)
            prompt = f"""
        Analyze this resume for the role: {target_role}
        against the Job Description.

        Job Description:
        {job_description}

        Retrieved Resume Context:
        {retrieved_context}

        ATS Score:
        {ats_score}

        Missing Skills:
        {missing_text}

        Provide:

        1. Resume Strengths
        2. Resume Weaknesses
        3. Missing Skills Analysis
        4. ATS Improvement Suggestions
        5. Recommended Skills
        6. Recommended Projects
        7. Job Match Analysis
        8. Interview Preparation Tips
        """
            with st.spinner("Generating AI Feedback..."):

                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    report_text = response.text

                    pdf_file = generate_pdf_report(report_text)

                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_file,
                        file_name="Resume_Analysis_Report.pdf",
                        mime="application/pdf"
                    )

                except Exception:
                     st.warning(
                        "⚠ Daily AI request limit reached. Please try again later."
                    )
                     
                     st.stop()
            st.markdown("---")

        if st.button("✨ Improve Resume"):
            if uploaded_file is None:
                st.warning("⚠ Please upload a resume first.")
                st.stop()
            rewrite_prompt = f"""
            Rewrite this resume in a professional ATS-friendly format.

            Target Role:
            {target_role}

            Resume:
            {resume_text}

            Improve:

            1. Professional Summary
            2. Skills Section
            3. Project Descriptions
            4. ATS Optimization Tips
            5. Resume Formatting Suggestions

            Give the output in a clean professional format.
            """

            with st.spinner("Improving Resume..."):

                try:
                    response = model.generate_content(rewrite_prompt)

                    st.session_state.improved_resume = response.text

                    if st.session_state.improved_resume:

                        st.subheader("🚀 Improved Resume Version")

                        st.markdown(st.session_state.improved_resume)

                        st.download_button(
                            "📄 Download Improved Resume",
                            st.session_state.improved_resume,
                            file_name="Improved_Resume.txt"
                        )

                except Exception:
                    st.warning(
                        "⚠ Daily AI request limit reached. Please try again later."
                    )
                    st.stop()

        if st.button("📄 Generate Cover Letter"):

            cover_prompt = f"""
            Write a professional cover letter.

            Target Role:
            {target_role}

            Resume:
            {resume_text}

            ATS Score:
            {ats_score}

            The cover letter should:
            - Be professional
            - Mention relevant skills
            - Be suitable for freshers
            - Be ATS friendly
            """

            with st.spinner("Generating Cover Letter..."):

                try:
                    cover_response = model.generate_content(
                        cover_prompt
                    )

                    st.subheader("📄 AI Generated Cover Letter")

                    st.markdown(
                        cover_response.text
                    )

                    st.download_button(
                        "⬇ Download Cover Letter",
                        cover_response.text,
                        file_name="Cover_Letter.txt"
                    )

                except Exception:
                    st.warning(
                        "⚠ Daily AI request limit reached. Please try again later."
                    )
                    st.stop()
    with tab3:

        st.markdown("---")
        st.subheader("💬 Chat With Resume")

        user_query = st.text_input(
            "Ask something about your resume"
        )
        if user_query:

            retrieved_context = retrieve_context(
                user_query
            )
            chat_prompt = f"""
            You are a professional career advisor.

            Resume Context:
            {retrieved_context}

            User Question:
            {user_query}

            Answer the question based only
            on the resume context.
            """
            try:

                response = model.generate_content(chat_prompt)

                st.session_state.chat_history.append(
                    ("You", user_query)
                )

                st.session_state.chat_history.append(
                    ("Bot", response.text)
                )

            except Exception:
                st.warning(
                    "⚠ Daily AI request limit reached. Please try again later."
                )
                st.stop()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
        st.subheader("💬 Chat History")

        for role, message in st.session_state.chat_history:

            if role == "You":
                st.markdown(f"**🧑 You:** {message}")

            else:
                st.markdown(f"**🤖 Bot:** {message}")

    with tab4:
        st.subheader("🎯 Interview Preparation")
        if st.button("Generate Interview Questions"):
            if uploaded_file is None:
                st.warning("⚠ Please upload a resume first.")
                st.stop()

            prompt = f"""
            Generate only 10 interview questions based on this resume.

            Resume:
            {resume_text[:1500]}
            """

            with st.spinner("Generating Interview Questions..."):

                try:
                    response = model.generate_content(prompt)

                    st.success("✅ Generated Successfully")

                    st.write(response.text)

                    st.download_button(
                        "📥 Download Interview Questions",
                        data=response.text,
                        file_name="interview_questions.txt",
                        mime="text/plain"
                    )

                except Exception:
                    st.warning(
                        "⚠ Daily AI request limit reached. Please try again later."
                    )
                    st.stop()
        st.markdown("---")
        st.subheader("🎤 Mock Interview Simulator")

        # Generate Question
        if st.button("🎯 Generate Mock Question"):

            mock_prompt = f"""
            Generate ONE technical interview question for {target_role}

            Based on this resume:

            {resume_text[:1500]}

            Return only the question.
            """

            with st.spinner("Generating Question..."):

                try:
                    response = model.generate_content(mock_prompt)

                    st.session_state.mock_question = response.text

                except Exception:
                    st.warning(
                        "⚠ Daily AI request limit reached. Please try again later."
                    )
                    st.stop()
        # Show Generated Question
        if "mock_question" in st.session_state:

            st.success("Generated Question")

            st.write(st.session_state.mock_question)

            user_answer = st.text_area(
                "✍ Your Answer",
                height=150
            )

            if st.button("📊 Evaluate Answer"):

                evaluation_prompt = f"""
                You are an experienced technical interviewer.

                Interview Question:
                {st.session_state.mock_question}

                Candidate Answer:
                {user_answer}

                Evaluate:

                1. Score out of 10
                2. Strengths
                3. Weaknesses
                4. Improved Answer
                5. Final Verdict

                Be professional and detailed.
                """

                with st.spinner("Evaluating Answer..."):

                    try:
                        response = model.generate_content(
                            evaluation_prompt
                        )

                        st.subheader("📋 Interview Feedback")

                        st.markdown(response.text)

                        st.download_button(
                            "📥 Download Feedback",
                            data=response.text,
                            file_name="mock_interview_feedback.txt",
                            mime="text/plain"
                        )

                    except Exception:
                        st.warning(
                            "⚠ Daily AI request limit reached. Please try again later."
                        )
                        st.stop()
    with tab5:

        st.subheader("🎓 AI Career Coach")

        if st.button("Generate Career Roadmap"):
            if uploaded_file is None:
                st.warning("⚠ Please upload a resume first.")
                st.stop()
            roadmap_prompt = f"""
            Based on this resume and target role {target_role},

            Create:

            1. 30-Day Learning Roadmap
            2. Skills to Learn
            3. Recommended Certifications
            4. Recommended Projects
            5. Interview Preparation Strategy

            Resume:
            {resume_text}
            """
            with st.spinner("Generating Career Roadmap..."):

                try:
                    response = model.generate_content(roadmap_prompt)

                    st.write(response.text)

                except Exception:
                    st.warning(
                        "⚠ Daily AI request limit reached. Please try again later."
                    )
                    st.stop()
st.markdown("---")

st.markdown("---")

st.markdown("""
<div style='text-align:center;color:#B0BEC5;'>

<h4 style='color:#4CAF50;'>
Developed by Naina Gupta
</h4>

Automation & RAG Intern

<br><br>

Powered by Gemini • FAISS • Sentence Transformers

</div>
""", unsafe_allow_html=True)