# Enterprise Knowledge Retrieval System

A ready-to-use Windows project for enterprise document retrieval and grounded RAG answers. This open-source edition is based on the established V4 desktop build and preserves its original interface, indexing, exact search, source traceability, and conversation workflow while removing organization-specific branding and local sensitive information.

**Topics:** `enterprise-search` · `document-retrieval` · `enterprise-knowledge-base` · `knowledge-management` · `industrial-ai` · `manufacturing-ai` · `rag` · `local-first`

Download `EnterpriseKnowledgeRetrieval-Windows-x64-v0.4.0.zip` from GitHub Releases, extract it completely, and run `EnterpriseKnowledgeRetrieval.exe`. No registration, login, or server is required.

Exact retrieval runs locally. Configure an OpenAI-compatible endpoint, model, and API key only when grounded RAG answers are needed.

## Run from source

```powershell
git clone https://github.com/Mege98/enterprise-knowledge-retrieval.git
cd enterprise-knowledge-retrieval
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
python enterprise_knowledge_retrieval.py
```

Licensed under the [Apache License 2.0](LICENSE). See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for dependency licenses.
