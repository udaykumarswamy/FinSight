# FinSight

FinSight is an AI-powered financial research agent designed to analyze markets, surface insights, and assist investors and analysts in making informed decisions. It integrates state-of-the-art LLMs and financial tools to deliver deep research, automated workflows, and contextual intelligence.

This project was developed by Uday Kumar Swamy, under the guidance of Professor Raj Krishnan @ IIT Chiacgo.

---

## 🚀 Features

* **Agentic AI Research System** powered by advanced LLMs
* **Conversation memory & context retention** for multi-turn research
* **Tool calling & structured responses** via LangChain
* **Financial data ingestion & processing**
* **Automated market analysis & reasoning**
* **Scalable architecture for parallel model inference**
* **Robust retry, rate-limit handling, and history compression**

---

## 🧠 Tech Stack

* **Python**
* **LangChain** (agents, memory, tool execution)
* **OpenAI GPT models**
* **tiktoken** for token management
* **Pydantic** for structured outputs
* **Custom tool integrations** for financial data

---

## 📂 Project Structure

```bash
├── index.js
├── LICENSE
├── package.json
├── pyproject.toml
├── README.md
├── src
│   ├── finsight
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── agent.py
│   │   ├── cli.py
│   │   ├── memory
│   │   ├── model.py
│   │   ├── plotgraph.py
│   │   ├── prompts.py
│   │   ├── schemas.py
│   │   ├── tools
│   │   └── utils
│   └── finsight.egg-info
│       ├── dependency_links.txt
│       ├── entry_points.txt
│       ├── PKG-INFO
│       ├── requires.txt
│       ├── SOURCES.txt
│       └── top_level.txt
└── uv.lock
```

---

## 🧩 Key Components

### ✅ Conversation Memory

Supports:

* AI & user messages
* Tool call states
* Automatic summarization when context length grows

### ✅ LLM Caller

* Retry mechanism
* Back-off strategy
* Supports structured function calling
* Maintains conversation history

---

## 🛠️ Installation

```bash
git clone https://github.com/udaykumarswamy/finsight.git
cd finsight
uv sync
uv pip install -e .
```

create .env file:

```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your-openai-api-key
# FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

---

## ▶️ Usage

```bash
uv run finsight-agnet
```

---

## 📈 Roadmap

* ✅ Core agent
* ✅ Tool calling
* ✅ Memory summarization
* 🚧 Live market data tools
* 🚧 Visuals
* 🚧 UI dashboard
* 🚧 Advanced autonomous research workflow

## Feature Improvment 
* Embeddings + vector DB (FAISS/Chroma): store long past messages/outputs as embeddings and retrieve only the most relevant chunks per query (best long-term scaling).

* Summarize-on-write + summarize-on-read hybrid:
Summarize large tool outputs when written.
For long sessions, do a relevance-based summary or retrieval at query time.

* Hierarchical / topic-based memory: group messages by topic/session and summarize per-topic so unrelated context is not sent.

* Persistent sessions: save summaries/embeddings to disk or DB with session IDs so memory survives process restarts.
Use local/smaller summarizers for condensation to avoid extra API calls (e.g., open-source models or on-prem summarizer).

* Smarter retention policy: score messages by salience (numeric facts, tool outputs, user confirmations) and keep only high-salience items verbatim.

* Token budgeting and dynamic model selection:
Automatically switch to smaller model for summarization/argument-optimization, keep gpt-4 class for final answer.
Cache expensive LLM outputs (idempotent prompts / tool optimizations) to avoid repeated token usage.

* Add monitoring/metrics: log token usage per-call and count TPM to fine-tune thresholds.

---

## 🤝 Contributing

PRs and feature suggestions are welcome!

---

## 📜 License

MIT License

---

## ⭐ Acknowledgements

Special thanks to the open-source community and AI research teams enabling agentic intelligence.

"Empowering smarter financial research with AI."

