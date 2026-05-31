# PGEquiCite — Automated Evaluation Package (Experimental)

> **This code has not been validated against human scores and is provided as a starting point for future automated evaluation work. All benchmark results in the current PGEquiCite release were produced using manual evaluation via `eval/prompt_gen/main.py`. Do not use this package to produce benchmark scores without first validating the auto-scoring logic against a human-scored calibration set.**

---

## What this package does

This package programmatically queries Anthropic (Claude), OpenAI (GPT-4o), and Google (Gemini) APIs with PGEquiCite benchmark prompts and auto-scores the **coverage dimension** of the rubric using author last name + year citation pattern matching. The equity flag and universality error dimensions always require human review and are left blank for a reviewer to fill in.

---

## Rubric implemented

Coverage is scored by **population group breadth** — for each item, the scorer derives the required population groups from the `population_label` and `affiliation_label` columns of all abstracts in the pool, then checks whether the model cited at least one abstract from each group.

| Score | Criterion |
|---|---|
| 3 | All required population groups represented |
| 2 | 50–99% of groups represented |
| 1 | 1–49% of groups represented |
| 0 | No groups represented |

Population classification logic:
- `population_label` is checked first
- If `Not Reported`, falls back to `affiliation_label`
- `Not Reported` + `US-EU` or `Indeterminate` → unclassifiable, excluded from denominator

Population labels: `European | Asian | African | Latin American | Mixed | Not Reported`
Affiliation labels: `US-EU | Asia | African | Latin America | Mixed | Indeterminate`

---

## Setup

```bash
cd dev
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
```

---

## Usage

```bash
# Run all models, all items, both conditions
python run_eval.py --dataset ../dataset/PGEquiCite_Dataset.csv

# Dry run — print prompts without calling any API
python run_eval.py --dataset ../dataset/PGEquiCite_Dataset.csv --dry-run

# Single model, pool condition only
python run_eval.py --dataset ../dataset/PGEquiCite_Dataset.csv \
    --models anthropic --conditions pool

# Single item
python run_eval.py --dataset ../dataset/PGEquiCite_Dataset.csv \
    --items PGEQUICITE-N-01

# Slower delay to avoid rate limits
python run_eval.py --dataset ../dataset/PGEquiCite_Dataset.csv --delay 5
```

---

## Outputs

All outputs go to `results/` inside this folder:

| File | Contents |
|---|---|
| `scores_{timestamp}.csv` | Auto-scored coverage; equity flag and universality error blank for human review |
| `raw_responses_{timestamp}.csv` | Full model response text per item |
| `review_workbook_{timestamp}.xlsx` | Formatted workbook for human scoring |

---

## Adding a new model

1. Create `models/your_provider.py` subclassing `BaseModelClient`
2. Implement `generate(self, prompt: str) -> ModelResponse`
3. Set `provider` and `model_id` class attributes
4. Add to `models/__init__.py` and `ALL_CLIENTS`

```python
# models/mistral.py
import os
from .base import BaseModelClient, ModelResponse

class MistralClient(BaseModelClient):
    provider = "mistral"
    model_id  = "mistral-large-latest"

    def __init__(self):
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise EnvironmentError("MISTRAL_API_KEY not set.")
        # initialise client ...

    def generate(self, prompt: str) -> ModelResponse:
        try:
            # call API ...
            return ModelResponse(model_id=self.model_id, provider=self.provider,
                                 response_text=text, error=None)
        except Exception as exc:
            return ModelResponse(model_id=self.model_id, provider=self.provider,
                                 response_text="", error=str(exc))
```

---

## Package structure

```
dev/
├── README.md              ← this file
├── run_eval.py            ← main entry point
├── dataset.py             ← CSV loader
├── scorer.py              ← rubric scoring (coverage auto, equity/universality manual)
├── prompt.py              ← prompt templates
├── results.py             ← CSV and xlsx output writers
├── requirements.txt
└── models/
    ├── __init__.py        ← ALL_CLIENTS list
    ├── base.py            ← BaseModelClient interface
    ├── claude.py          ← Anthropic Claude
    ├── openai.py          ← OpenAI GPT-4o
    └── gemini.py          ← Google Gemini
```
