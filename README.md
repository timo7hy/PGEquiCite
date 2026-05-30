# PGEquiCite

**Citation Equity Benchmark for AI in Scientific Literature Synthesis**

Course benchmark dataset for ECE 209AS at UCLA. This project evaluates whether AI-powered literature synthesis tools equitably cite pharmacogenomic research from non-European populations, or systematically suppress it.

---

## What This Benchmark Measures

When a researcher asks an AI to summarize pharmacogenomic evidence, does the model cite the full evidence base — including studies from non-European populations — or does it default to majority-population findings and present them as universal?

The human factor being measured is **evidence traceability**: can a scientist trust that the AI's citations represent the full evidence base?

---

## Dataset Structure

Each item consists of:
- A natural language query given to the AI model
- A pool of 10 PubMed abstracts (5 European-cohort, 5 Non-European-cohort)
- A reference answer describing what a complete equitable response must contain
- An evaluation rubric with three components:
  - **Coverage score (0–3):** fraction of non-European papers cited
  - **Equity flag (0/1):** did the model note population-specific limitations?
  - **Universality error (0/1, penalized):** did the model present majority-population findings as universal?

Max score per item = 5.

---

## Gene-Drug Pairs

| Pair | Item Code | Equity Gap |
|------|-----------|------------|
| NUDT15 / Thiopurines | N | Stark |
| CYP2C19 / Clopidogrel | C | High |
| G6PD / Primaquine | G | High |
| SLCO1B1 / Statins | S | High |
| HLA-B*57:01 / Abacavir | H | High |
| CYP2D6 / Codeine | D | Stark |

---

## Repository Structure

```
pgequicite/
├── README.md
├── dataset/
│   └── PGEquiCite_Dataset.csv     # export of master dataset
├── eval/
│   ├── eval.py                    # evaluation script
│   └── pgequicite_eval/           # Python package
├── results/                       # model evaluation outputs
└── docs/
    ├── rubric.md                  # scoring rubric
    └── schema.md                  # dataset column definitions
```

---

## Authors

ECE 209AS — UCLA, Spring 2026
