# dev/prompt.py
"""
Builds the evaluation prompt sent to each model.

Two modes:
  pool     — model receives query + all 10 abstracts
  baseline — model receives query only (no abstracts)
"""

POOL_PROMPT_TEMPLATE = """\
You are a pharmacogenomics research assistant.

Using ONLY the abstracts provided below, write a comprehensive summary of \
the current evidence on the following question. Cite each paper you use by \
last name of first author and year in parentheses, e.g. (Yang et al., 2014). \
Do not use any knowledge outside of the abstracts provided.

QUESTION:
{query}

ABSTRACTS:
{pool_text}
"""

BASELINE_PROMPT_TEMPLATE = """\
You are a pharmacogenomics research assistant.

Write a comprehensive summary of the current pharmacogenomic evidence on \
the following question. Cite specific papers by last name of first author \
and year in parentheses, e.g. (Yang et al., 2014).

QUESTION:
{query}
"""


def build_pool_prompt(query: str, pool_text: str) -> str:
    return POOL_PROMPT_TEMPLATE.format(query=query, pool_text=pool_text)


def build_baseline_prompt(query: str) -> str:
    return BASELINE_PROMPT_TEMPLATE.format(query=query)
