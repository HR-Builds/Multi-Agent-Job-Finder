# 🔎 CareerLens — Multi-Agent Job Finder

> **AI-powered multi-agent job discovery and career research platform**

CareerLens is an AI-powered job finder that uses a **multi-agent architecture** to help users discover relevant job opportunities based on their resume, skills, experience, and career goals.

Instead of manually searching through hundreds of job listings, CareerLens analyzes the user's resume and intelligently researches available opportunities to identify jobs that best match their profile.

## 🚀 Live Demo

🌐 **Try CareerLens:**
https://careenlens.streamlit.app/

---

## ✨ Features

* 📄 **Resume Upload**

  * Upload your resume in PDF or DOCX format.
  * Automatically extracts relevant candidate information.

* 🤖 **Multi-Agent AI System**

  * Uses specialized AI agents for different stages of the job-search process.
  * Agents work together to analyze and research opportunities.

* 🔍 **Intelligent Job Research**

  * Searches for relevant job opportunities based on candidate information.
  * Reduces the need for manual job searching.

* 🧠 **Resume Analysis**

  * Identifies skills, experience, technologies, and professional strengths from the resume.

* 🎯 **Job Matching**

  * Evaluates how well job opportunities match the candidate's profile.

* 📊 **AI-Powered Analysis**

  * Provides useful insights about discovered positions and their relevance.

* 🌐 **Web-Based Interface**

  * Built with Streamlit for a simple and interactive user experience.

---

## 🏗️ How It Works

```text
                ┌──────────────────────┐
                │      User Resume     │
                │      PDF / DOCX      │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │    Resume Reader     │
                │  Extract Candidate   │
                │      Information     │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Multi-Agent AI     │
                │      Pipeline        │
                └──────────┬───────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        ┌─────────┐   ┌─────────┐   ┌─────────┐
        │Research │   │Analyzer │   │ Matcher │
        │  Agent  │   │  Agent  │   │  Agent  │
        └────┬────┘   └────┬────┘   └────┬────┘
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                ┌──────────────────────┐
                │   Job Opportunities  │
                │   + AI Analysis      │
                └──────────────────────┘
```

---

## 🧠 Multi-Agent Architecture

CareerLens separates the job-search workflow into specialized tasks.

### 📄 Resume Reader

Extracts useful information from the uploaded resume, including:

* Skills
* Experience
* Education
* Technologies
* Projects
* Professional background

### 🔎 Research Agent

Researches job opportunities relevant to the candidate's profile.

### 🧠 Analyzer Agent

Analyzes job descriptions and identifies important requirements, technologies, responsibilities, and qualifications.

### 🎯 Matching / Recommendation Layer

Compares the candidate's profile with researched opportunities and helps identify the most relevant positions.

---

## 🛠️ Tech Stack

### AI & LLM

* Python
* LangChain
* Groq
* LLM-based agents

### Backend / Application

* Streamlit
* Python

### Search & Research

* Tavily
* Web-based job research

### Document Processing

* PDF Resume Processing
* DOCX Resume Processing

### Configuration

* Pydantic Settings
* Python-dotenv
* Environment Variables

### Deployment

* Streamlit Cloud
* GitHub

---

## 📁 Project Structure

```text
multi-agent-job-finder/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── sample_resumes/
│
└── src/
    │
    ├── pipeline.py
    ├── config.py
    │
    ├── chains/
    │   └── analyzer.py
    │
    └── tools/
        └── resume_reader.py
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/HR-Builds/Multi-Agent-Job-Finder.git
```

### 2. Navigate to the project

```bash
cd Multi-Agent-Job-Finder
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

#### Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

MODEL_NAME=openai/gpt-oss-120b
TEMPERATURE=0.7
MAX_SEARCH_RESULTS=5
```

⚠️ **Never commit your `.env` file or API keys to GitHub.**

For Streamlit Cloud deployment, add the required secrets through the application's **Secrets** settings.

---

## ▶️ Run Locally

Start the Streamlit application:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## ☁️ Deployment

CareerLens is deployed using **Streamlit Cloud**.

Live application:

https://careenlens.streamlit.app/

The application uses environment secrets for API credentials, keeping sensitive keys outside the public repository.

---

## 🎯 Project Goals

CareerLens was created to explore and demonstrate practical implementation of:

* Multi-agent AI systems
* Agentic workflows
* LLM-powered research
* Resume understanding
* AI-based job matching
* LangChain
* Tool-using AI agents
* AI application deployment
* Streamlit development

---

## 🔮 Future Improvements

Potential future improvements include:

* 🔐 User authentication
* 💾 Job history and saved jobs
* 📌 Bookmark opportunities
* 📊 Advanced candidate-job scoring
* 🧑‍💼 LinkedIn profile integration
* 📧 Job alerts
* 🗂️ Personalized job dashboard
* 📈 Career skill-gap analysis
* 📝 AI-generated cover letters
* 📄 AI-powered resume improvement
* 🎯 Personalized career recommendations
* 🔄 Continuous job monitoring

---

## 🔒 Security

API keys and other sensitive credentials should never be hard-coded into the application.

CareerLens uses environment variables locally and deployment secrets in Streamlit Cloud.

Make sure `.env` is included in `.gitignore`.

---

## 👨‍💻 Author

**Hassan Rashid**

AI / Python Developer

### Skills & Interests

* Python
* LangChain
* RAG Systems
* AI Chatbots
* FastAPI
* Agentic AI
* Multi-Agent Systems

### 🔗 Connect

* GitHub: https://github.com/HR-Builds
* LinkedIn: http://www.linkedin.com/in/hassan-rashid-a325883aa

---

## ⭐ Support

If you find CareerLens interesting, consider giving the repository a ⭐ on GitHub.

**CareerLens — Search smarter. Match better. Build your career with AI.**
