# Evaluation

This directory contains scripts for evaluating PrivAI's performance across its core capabilities.

## Files

| File | Description |
|---|---|
| [`eval_script.py`](eval_script.py) | End-to-end evaluation of RAG accuracy, summarization quality, and task scheduling correctness |

## Running the Evaluation

```powershell
# Windows
venv\Scripts\python.exe evaluation/eval_script.py
```

```bash
# Linux/macOS
python evaluation/eval_script.py
```

## What is Evaluated

| Component | Metrics |
|---|---|
| **RAG Pipeline** | Answer relevance, retrieval precision, grounding accuracy |
| **Summarizer** | Coverage, compression ratio, format adherence |
| **Scheduler** | Task extraction accuracy, date/time parsing correctness |
| **Intent Detection** | Classification accuracy across 6 intent categories |

## Notes

- Evaluation requires Ollama to be running with `phi3:mini` and `tinyllama` pulled.
- Results are printed to stdout; redirect to a file for logging:

```bash
python evaluation/eval_script.py > eval_results.txt
```
