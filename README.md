# FinSight
Financial Analysis AI-Agent, Does research work on your behalf and gives summary of finding's, will give some valuable insights  


'''
Further improvements can be made here.
Embeddings + vector DB (FAISS/Chroma): store long past messages/outputs as embeddings and retrieve only the most relevant chunks per query (best long-term scaling).

Summarize-on-write + summarize-on-read hybrid:
Summarize large tool outputs when written.
For long sessions, do a relevance-based summary or retrieval at query time.

Hierarchical / topic-based memory: group messages by topic/session and summarize per-topic so unrelated context is not sent.
Persistent sessions: save summaries/embeddings to disk or DB with session IDs so memory survives process restarts.
Use local/smaller summarizers for condensation to avoid extra API calls (e.g., open-source models or on-prem summarizer).

Smarter retention policy: score messages by salience (numeric facts, tool outputs, user confirmations) and keep only high-salience items verbatim.

Token budgeting and dynamic model selection:
Automatically switch to smaller model for summarization/argument-optimization, keep gpt-4 class for final answer.
Cache expensive LLM outputs (idempotent prompts / tool optimizations) to avoid repeated token usage.

Add monitoring/metrics: log token usage per-call and count TPM to fine-tune thresholds.


'''