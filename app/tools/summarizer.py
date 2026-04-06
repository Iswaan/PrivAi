"""
Summarizer tool with configurable detail, output structure, and saved history.
"""
import re
import time

from app.config import PRIMARY_MODEL
from app.models.llm_client import chat
from app.storage.database import SessionLocal, SummaryRecord
from app.storage.file_manager import chunk_text, extract_text

DETAIL_GUIDANCE = {
    "concise": "Keep the output tight and high signal. Prioritize only the most important ideas.",
    "standard": "Balance brevity with clarity. Cover the main ideas with enough detail to understand the document.",
    "detailed": "Be comprehensive. Include major topics, subtopics, supporting details, examples, and notable arguments.",
}

FORMAT_GUIDANCE = {
    "plain": "Write a clean readable summary in prose, with short bullets only when helpful.",
    "structured": """Use this exact structure:
## Overview
## Main Topics
- Topic
  - Subtopics / important details
## Key Takeaways
## Important Details
## Action Items or Open Questions
Prefer clear bullets and include subtopics under each major topic.""",
    "study_guide": """Use this exact structure:
## Big Picture
## Topics and Subtopics
- Topic
  - Definition / explanation
  - Important details
## Terms to Remember
## Possible Questions
## Short Recap
Make it useful for revision and learning.""",
}

CHUNK_SUMMARY_PROMPT = """You are summarizing one chunk from a larger document.
{detail_guidance}

Rules:
- Stay faithful to the source text
- Prefer specific facts over vague wording
- Preserve important section names when present
- Do not invent missing details

Extract:
- the chunk's main topic
- important subtopics
- key facts, arguments, or decisions
- any dates, action items, or examples

Write a compact chunk summary that will later be merged with other chunk summaries.
Use short bullets when helpful.

Section:
{chunk}

Chunk Summary:"""

MERGE_PROMPT = """You are given multiple chunk summaries from the same document.
Produce one final document summary.

Detail requirement:
{detail_guidance}

Formatting requirement:
{format_guidance}

Rules:
- Combine overlapping points instead of repeating them
- Preserve important topics and subtopics from across the document
- Mention concrete dates, names, decisions, and action items when present
- If the source is sparse or messy, say so briefly instead of guessing

Chunk Summaries:
{summaries}

Final Summary:"""


def summarize_text(
    text: str,
    model: str = PRIMARY_MODEL,
    detail_level: str = "standard",
    format_type: str = "structured",
) -> dict:
    """
    Summarize raw text with timing info.

    Returns:
        dict with summary metadata.
    """
    start = time.time()
    normalized_text = _normalize_text(text)
    chunks = chunk_text(normalized_text)
    detail_level = detail_level if detail_level in DETAIL_GUIDANCE else "standard"
    format_type = format_type if format_type in FORMAT_GUIDANCE else "structured"
    source_word_count = len(normalized_text.split())

    if not chunks:
        return {
            "summary": "No content found to summarize.",
            "chunk_count": 0,
            "time_seconds": 0,
            "detail_level": detail_level,
            "format_type": format_type,
            "source_word_count": source_word_count,
        }

    chunk_summaries = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_summary = chat(
            CHUNK_SUMMARY_PROMPT.format(
                chunk=f"[Chunk {index}/{len(chunks)}]\n{chunk}",
                detail_guidance=DETAIL_GUIDANCE[detail_level],
            ),
            model=model,
        )
        chunk_summaries.append(chunk_summary)

    combined = "\n\n---\n\n".join(chunk_summaries)
    summary = chat(
        MERGE_PROMPT.format(
            summaries=combined,
            detail_guidance=DETAIL_GUIDANCE[detail_level],
            format_guidance=FORMAT_GUIDANCE[format_type],
        ),
        model=model,
    )
    summary = summary.strip()

    elapsed = round(time.time() - start, 2)
    return {
        "summary": summary,
        "chunk_count": len(chunks),
        "time_seconds": elapsed,
        "detail_level": detail_level,
        "format_type": format_type,
        "source_word_count": source_word_count,
    }


def summarize_file(
    filepath: str,
    filename: str | None = None,
    detail_level: str = "standard",
    format_type: str = "structured",
) -> dict:
    """
    Extract text from a file and return summary metadata.
    """
    text = extract_text(filepath)
    result = summarize_text(
        text,
        detail_level=detail_level,
        format_type=format_type,
    )
    stored_record = save_summary_record(
        filename=filename or filepath.split("\\")[-1].split("/")[-1],
        detail_level=result["detail_level"],
        format_type=result["format_type"],
        source_word_count=result["source_word_count"],
        chunk_count=result["chunk_count"],
        summary=result["summary"],
    )
    result["summary_id"] = stored_record["id"]
    return result


def save_summary_record(
    filename: str,
    detail_level: str,
    format_type: str,
    source_word_count: int,
    chunk_count: int,
    summary: str,
) -> dict:
    db = SessionLocal()
    try:
        record = SummaryRecord(
            filename=filename,
            detail_level=detail_level,
            format_type=format_type,
            source_word_count=source_word_count,
            chunk_count=chunk_count,
            summary=summary,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return _summary_record_to_dict(record)
    finally:
        db.close()


def list_summary_history(limit: int = 20) -> list[dict]:
    db = SessionLocal()
    try:
        records = (
            db.query(SummaryRecord)
            .order_by(SummaryRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        return [_summary_record_to_dict(record) for record in records]
    finally:
        db.close()


def _summary_record_to_dict(record: SummaryRecord) -> dict:
    return {
        "id": record.id,
        "filename": record.filename,
        "detail_level": record.detail_level,
        "format_type": record.format_type,
        "source_word_count": record.source_word_count,
        "chunk_count": record.chunk_count,
        "summary": record.summary,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
