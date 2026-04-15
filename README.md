# 🎭 The Empathy Engine
***Enterprise-Grade AI Emotional Intelligence & Adaptive vocal Synthesis Terminal***

<div align="center">

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61dafb?style=for-the-badge&logo=react&logoColor=white)](https://react.dev/)
[![Transformers](https://img.shields.io/badge/HF_Transformers-Latest-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/)
[![SQLite](https://img.shields.io/badge/SQLite-Latest-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

**A mission-critical AI platform that bridges the gap between static text and human emotion through multi-model ensemble analysis and surgical vocal prosody modulation.**

---

</div>

## 📖 Table of Contents
1. [🌟 Executive Summary](#-executive-summary)
2. [✅ Compliance & Requirements Matrix](#-compliance--requirements-matrix)
3. [🏗️ Deep-Dive Architecture](#-deep-dive-architecture)
    - [Layer 1: Presentation (React Frontend)](#layer-1-presentation-react-frontend)
    - [Layer 2: Orchestration (FastAPI Service)](#layer-2-orchestration-fastapi-service)
    - [Layer 3: Cognitive Intelligence (AI Ensemble)](#layer-3-cognitive-intelligence-ai-ensemble)
    - [Layer 4: Acoustic Mapping (Prosody Engine)](#layer-4-acoustic-mapping-prosody-engine)
    - [Layer 5: Infrastructure (Persistence & Serving)](#layer-5-infrastructure-persistence--serving)
4. [🛠️ The Tech Stack (Exhaustive)](#-the-tech-stack-exhaustive)
5. [🚀 Installation & Setup](#-installation--setup)

---

## 🌟 Executive Summary
The Empathy Engine is a state-of-the-art solution built for the **Darwix AI Engineering Assessment**. It solves the "monotonic robot" problem by performing a deep-spectrum emotional analysis of text and translating it into acoustic features—Pitch, Rate, and Volume—mirroring human psychological states.

---

## ✅ Compliance & Requirements Matrix
| Requirement | Engineering Implementation | Implementation Focus |
| :--- | :--- | :--- |
| **III. Core: Text Input** | ⚡ FastAPI REST Endpoints | Asynchronous ingestion with full Pydantic validation. |
| **III. Core: Emotion Detection** | 🧠 8-Class Neural Ensemble | VADER + DistilBERT + RoBERTa weighted averaging. |
| **III. Core: Parameter Modulation** | 🎛️ Multi-Param Prosody | Real-time shifting of Rate, Pitch, and Amplitude. |
| **III. Core: Mapping Logic** | 📐 Modulation Matrix | Logarithmic intensity scaling based on confidence. |
| **III. Core: Audio Output** | 🔊 Absolute Path Serving | Atomic waveform generation and stable file serving. |
| **IV. Bonus: Granular States** | 🌈 8 Distinct States | Happy, Angry, Sad, Calm, Frustrated, Surprise, Concern, Neutral. |
| **IV. Bonus: Intensity Scaling** | 📈 Logistic Scaling | `modulation = f(confidence)`. Higher intensity = stronger vocal shift. |
| **IV. Bonus: Web Interface** | 🎨 React Terminal | Premium glassmorphism UI with real-time waveform visualizers. |

---

## 🏗️ Deep-Dive Architecture

The Empathy Engine follows the **Clean Architecture (Hexagonal)** pattern, ensuring that the core "Intelligence" is entirely decoupled from external providers like the UI or TTS engines.

### Layer 1: Presentation (React Frontend)
- **Role**: Captures user intent and visualizes emotional feedback.
- **Core Logic**:
    - **State Management**: Uses React Hooks (`useState`, `useEffect`) to manage real-time synthesis cycles.
    - **Waveform Visualization**: Custom CSS animations mapped to the audio playback state.
    - **Asynchronous UX**: Handles polling and loading states while the backend performs its deep-learning inference.
- **Key Files**: `frontend/src/App.jsx`, `frontend/src/index.css`.

### Layer 2: Orchestration (FastAPI Service)
- **Role**: The "Traffic Controller". It handles validation, routing, and asynchronous coordination.
- **Core Logic**:
    - **Async Pipeline**: Every request is `async`, allowing the server to handle detection and synthesis concurrently without blocking.
    - **Validation Layer**: Uses **Pydantic V2** to strictly enforce text length, emotion types, and parameter ranges.
    - **Absolute Serving**: Controls the file system to serve audio from `temp_audio/` using absolute paths, preventing Uvicorn reload loops.
- **Key Files**: `backend/app/main.py`, `backend/app/routes/api.py`.

### Layer 3: Cognitive Intelligence (AI Ensemble)
- **Role**: The "Brain". This is where the raw text is converted into an emotional vector.
- **Ensemble Strategy**:
    - **VADER**: Analyzes lexical features (capital letters, "!!!", emoticons).
    - **DistilBERT**: Uses a transformer architecture to understand semantic meaning (the "what" behind the words).
    - **RoBERTa-Base-Emotion**: Detects nuanced social emotions (Joy, Optimism, Anger) using deep context.
    - **Ensemble Averaging**: Combines all three scores using a weighted-probability formula to find the most likely emotion.
- **Key Files**: `backend/app/models/emotion_detector.py`.

### Layer 4: Acoustic Mapping (Prosody Engine)
- **Role**: Translates psychological states into physical sound parameters.
- **Core Logic**:
    - **Modulation Matrix**: Maps each of the 8 emotions to a specific set of Pitch/Rate/Volume offsets.
    - **Intensity Logic**: If the model is 90% confident, it applies a "Strong" shift. If 50% confident, it applies a "Light" shift.
    - **Prosody Generation**: Converts these shifts into standard Speech Synthesis Markup Language (SSML) instructions.
- **Key Files**: `backend/app/models/voice_mapper.py`.

### Layer 5: Infrastructure (Persistence & Serving)
- **Role**: Manages the storage and audit trails.
- **Core Logic**:
    - **Database**: SQLAlchemy manages an SQLite database to track every synthesis for later review or "AI improvements."
    - **Logging**: **Loguru** provides high-fidelity, production-grade logs of every system event.
- **Key Files**: `backend/app/database.py`, `backend/app/utils/logger.py`.

---

## �️ The Tech Stack (Exhaustive)

### Backend (The Powerhouse)
- **FastAPI**: Modern, high-performance web framework for building APIs.
- **Uvicorn**: Lightning-fast ASGI server for production deployment.
- **PyTorch**: Deep learning framework powering the transformer models.
- **HuggingFace Transformers**: Used to load and serve RoBERTa and DistilBERT models.
- **SQLAlchemy**: The industry standard for robust database ORM.
- **Loguru**: Sophisticated logging for tracking system health in real-time.

### AI Models (The Intelligence)
- **RoBERTa-Base-Emotion**: A multi-class model fine-tuned for high-accuracy social emotion detection.
- **DistilBERT-SST-2**: Optimized for fast semantic sentiment analysis.
- **VADER**: Expert-level lexical sentiment analysis (perfect for punctuation-based emotion).

### Frontend (The Interface)
- **React 18**: Component-based library for building reactive user interfaces.
- **Vite 5**: Blazing fast build tool for modern frontend development.
- **Axios**: Promised-based HTTP client for seamless API communication.
- **Lucide-React**: Premium icon suite for professional aesthetics.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+**

### 2. Backend Initialization
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Frontend Initialization
```bash
cd frontend
npm install
npm run dev
```

---
<div align="center">

**Developed for the Kushagra Darwix AI Internship Assessment.**  
*Where code meets the heart.*

</div>
