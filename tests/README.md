# Tests

Unit tests for the PrivAI backend components.

## Running Tests

```bash
# From the project root
pytest tests/ -v
```

Or with the virtual environment:

```powershell
venv\Scripts\python.exe -m pytest tests/ -v
```

## Test Files

| File | What it Tests |
|---|---|
| [`test_rag.py`](test_rag.py) | RAG pipeline: document indexing, embedding, retrieval, and Q&A generation |
| [`test_scheduler.py`](test_scheduler.py) | Task creation from natural language, weekday parsing, priority/status handling |
| [`test_summarizer.py`](test_summarizer.py) | Document summarization pipeline: chunking, per-chunk LLM call, merge summary |

## Test Configuration

See [`conftest.py`](../conftest.py) in the project root for pytest fixtures and shared test configuration.

## Notes

- Tests require the **virtual environment** to be active.
- Tests for RAG and summarization make **local LLM calls** — Ollama must be running.
- Tests are designed to be **safe**: they do not write to your `data/` directory in production paths.
