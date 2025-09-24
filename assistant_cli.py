#!/usr/bin/env python3
"""
Copilot-style assistant for local projects.

Usage:
    python assistant_cli.py "How do I read a CSV file?" --context-root "E:/A.I. Development/Repos/MyApp"

Environment:
    OPENAI_API_KEY            : API key for the OpenAI-compatible endpoint.
    OPENAI_BASE_URL (optional): Override base URL for self-hosted inference servers.
    OPENAI_MODEL    (optional): Chat model ID (default: gpt-4o-mini).
    ASSISTANT_HISTORY(optional): Path to JSONL file used to log Q/A pairs.
"""
from __future__ import annotations


import argparse
import json
import logging
import os
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple, Optional

try:
    import requests
except ImportError:
    print("[error] The 'requests' library is required. Install it with 'pip install requests'.", file=sys.stderr)
    sys.exit(1)

DEFAULT_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


@dataclass
class CodeChunk:
    path: Path
    content: str
    rank: float


@dataclass
class PromptContext:
    question: str
    chunks: List[CodeChunk]


def read_text_files(
    root: Path,
    max_bytes: int = 200_000,
    exclude: Optional[Sequence[str]] = None
) -> Iterable[Tuple[Path, str]]:
    """
    Yield (path, text) pairs for UTF-8/ASCII files under root, excluding patterns.
    """
    exclude = exclude or []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(str(path).startswith(str(root / pat)) for pat in exclude):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".exe", ".dll"}:
            continue
        try:
            data = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if len(data.encode("utf-8")) > max_bytes:
            continue
        yield path, data


def simple_chunk(text: str, size: int = 400, overlap: int = 100) -> Iterable[str]:
    """
    Split text into overlapping chunks.
    """
    tokens = text.split()
    if not tokens:
        return
    start = 0
    while start < len(tokens):
        end = min(len(tokens), start + size)
        yield " ".join(tokens[start:end])
        start = end - overlap


def score_chunk(chunk: str, query: Sequence[str]) -> float:
    """
    Score chunk using simple term frequency.
    """
    if not chunk:
        return 0.0
    words = chunk.lower().split()
    score = sum(words.count(term) for term in query)
    return score / (len(words) or 1)


def collect_relevant_chunks(
    root: Path,
    query: str,
    limit: int = 6,
    exclude: Optional[Sequence[str]] = None
) -> List[CodeChunk]:
    """
    Collect and rank relevant code chunks from files under root.
    """
    query_terms = [term.lower() for term in query.split()]
    ranked: List[CodeChunk] = []
    for path, text in read_text_files(root, exclude=exclude):
        for chunk in simple_chunk(text):
            score = score_chunk(chunk, query_terms)
            if score == 0:
                continue
            ranked.append(CodeChunk(path=path, content=chunk, rank=score))
    ranked.sort(key=lambda c: c.rank, reverse=True)
    return ranked[:limit]


def build_prompt(context: PromptContext) -> List[dict]:
    """
    Build the prompt for the LLM API.
    """
    header = "You are a precise coding assistant. Use ONLY the provided context."
    context_blocks = []
    for chunk in context.chunks:
        context_blocks.append(
            f"### File: {chunk.path}\n"
            f"{chunk.content.strip()}\n"
        )
    payload = textwrap.dedent(
        f"""
        Question:
        {context.question.strip()}

        Project context:
        {textwrap.dedent(os.linesep.join(context_blocks)) if context_blocks else '(no context found)'}
        """
    ).strip()
    return [
        {"role": "system", "content": header},
        {"role": "user", "content": payload},
    ]


def call_openai(messages: List[dict], model: str = DEFAULT_MODEL) -> str:
    """
    Call the OpenAI-compatible API and return the response.
    """
    if not API_KEY:
        logging.error("OPENAI_API_KEY is not set.")
        raise RuntimeError("OPENAI_API_KEY is not set.")
    try:
        response = requests.post(
            f"{DEFAULT_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {'***' + API_KEY[-4:] if API_KEY else ''}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": 0.2,
                "messages": messages,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return "[error] Failed to contact the language model API."
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return f"[error] {e}"


def log_interaction(question: str, answer: str, ctx: List[CodeChunk], history_path: Optional[str] = None) -> None:
    """
    Log the Q/A interaction to a JSONL file if specified.
    """
    history_path = history_path or os.getenv("ASSISTANT_HISTORY")
    if not history_path:
        return
    record = {
        "timestamp": int(time.time()),
        "question": question,
        "answer": answer,
        "context": [{"path": str(chunk.path), "rank": chunk.rank} for chunk in ctx],
    }
    try:
        with open(history_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.warning(f"Failed to log interaction: {e}")


def run_cli() -> int:
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(description="Copilot-style CLI assistant.")
    parser.add_argument("question", help="Prompt or coding question.")
    parser.add_argument(
        "--context-root",
        default=".",
        help="Root directory for context retrieval (default: current directory).",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model name override.")
    parser.add_argument("--history", default=None, help="Path to Q/A history log file.")
    parser.add_argument("--limit", type=int, default=6, help="Number of context chunks to use.")
    parser.add_argument("--exclude", nargs="*", default=[], help="Exclude files/directories (relative to context root).")
    parser.add_argument("--version", action="version", version="assistant_cli.py v1.1")
    args = parser.parse_args()

    context_root = Path(args.context_root).resolve()
    if not context_root.exists():
        logging.error(f"Context root {context_root} does not exist.")
        return 1

    try:
        chunks = collect_relevant_chunks(context_root, args.question, limit=args.limit, exclude=args.exclude)
    except Exception as e:
        logging.error(f"Failed to collect context: {e}")
        return 1

    if not chunks:
        logging.warning("No relevant context found. Proceeding with question only.")

    messages = build_prompt(PromptContext(question=args.question, chunks=chunks))
    answer = call_openai(messages, model=args.model)
    print(answer)
    log_interaction(args.question, answer, chunks, history_path=args.history)
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
