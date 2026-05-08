"""web.py — Agent Tool: Web Executor.

Role:
- Search external information using DuckDuckGo.
- Summarize findings clearly into a concise report.
"""

from duckduckgo_search import DDGS
from llm import ask_llm

_SUMMARIZE_SYSTEM = """\
You are a WEB RESULT SUMMARIZER.
Your job is to read raw search results and produce a clear, concise, and factual summary.
Remove advertising noise, repetition, and irrelevant details.
Focus on answering the original user query accurately."""

def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web and return a summarized report of the findings.
    """
    raw_results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get("title", "").strip()
                body = r.get("body", "").strip()
                raw_results.append(f"TITLE: {title}\nCONTENT: {body}")
    except Exception as e:
        return f"Error during web search: {e}"

    if not raw_results:
        return "No relevant information found on the web."

    # Summarize the findings
    search_context = "\n---\n".join(raw_results)
    summary_prompt = f"QUERY: {query}\n\nRAW RESULTS:\n{search_context}"
    
    summary = ask_llm(summary_prompt, memory_context="", system_override=_SUMMARIZE_SYSTEM)
    return summary.strip()