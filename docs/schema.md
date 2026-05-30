# PGEquiCite Dataset Schema

Each row in the dataset represents one abstract within an item. All 10 rows of an item share the same `item_id`, `query`, `equity_gap_severity`, `reference_answer`, and `must_cite_abstracts`.

---

## Column Definitions

| Column | Description |
|--------|-------------|
| `item_id` | Unique item identifier. Format: `PGEQUICITE-{GENE_CODE}-{NN}` |
| `abstract_id` | Unique abstract identifier. Format: `{item_id}-A{NN}`. A01–A05 = European-cohort, A06–A10 = Non-European-cohort |
| `pmid` | PubMed ID. Must resolve at pubmed.ncbi.nlm.nih.gov |
| `title` | Full title exactly as it appears on PubMed |
| `authors` | First author last name + initials + et al. e.g. `Yang SK, et al.` |
| `year` | 4-digit publication year |
| `journal` | Journal name as it appears on PubMed |
| `abstract_text` | Full abstract text copied verbatim from PubMed |
| `population_label` | **Controlled vocab:** `European` \| `Non-European` \| `Mixed` \| `Not Reported` |
| `affiliation_label` | **Controlled vocab:** `US-EU` \| `Global-South` \| `HBCU` \| `Indeterminate` |
| `annotator_1_pop` | Annotator 1 population label (pre-adjudication) |
| `annotator_2_pop` | Annotator 2 population label (pre-adjudication) |
| `annotator_1_aff` | Annotator 1 affiliation label (pre-adjudication) |
| `annotator_2_aff` | Annotator 2 affiliation label (pre-adjudication) |
| `annotation_notes` | Free text — ambiguity, disagreement reasoning, adjudication notes |
| `query` | Natural language query given to the model. Same for all 10 rows of an item |
| `equity_gap_severity` | **Controlled vocab:** `Stark` \| `High` \| `Moderate` |
| `reference_answer` | What a complete equitable model response must contain |
| `must_cite_abstracts` | Comma-separated abstract IDs required for full credit |
| `annotator_1` | Name of annotator 1 |
| `annotator_2` | Name of annotator 2 |

---

## Controlled Vocabulary

### population_label
- `European` — cohort is predominantly of European ancestry
- `Non-European` — cohort is predominantly non-European (African, Asian, Latin American, etc.)
- `Mixed` — cohort explicitly includes multiple ancestral groups or is a multi-population study
- `Not Reported` — abstract does not describe cohort ancestry or geography

### affiliation_label
- `US-EU` — first author's institution is in the US, EU, UK, Canada, or Australia
- `Global-South` — first author's institution is in Africa, South/Southeast Asia, Latin America, or the Middle East
- `HBCU` — first author's institution is a Historically Black College or University
- `Indeterminate` — affiliation not listed or cannot be determined
