# Fabric IQ Mini Hack

**Starter repo for a Microsoft Fabric mini hack based on the Fabric Ontology Workshop**

---

## Project Overview

This repo is a starting point for the Fabric IQ Mini Hack. It is based on the Fabric Ontology Workshop and keeps the original notebook-driven flow for building an intelligent semantic layer in Microsoft Fabric.

You'll build a three-layer metadata architecture that enables AI agents to not just *compute* metrics, but *explain* why patterns exist.

### The Problem We Solve

Traditional analytics answers **"what"** and **"how"**:
- "What is total revenue by borough?" → $44M Manhattan, $15M Queens...
- "How is revenue calculated?" → `SUM(fare_amount + tip_amount)`

But it cannot answer **"why"**:
- "Why is Manhattan revenue 5x higher than Brooklyn?"
- "Why are tips lower in outer boroughs?"
- "What should I know before analyzing tip patterns?"

**This workshop shows you how to build systems that answer "why."**

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     INTELLIGENT SEMANTIC LAYER                          │
│                                                                         │
│   User: "What is total revenue by borough and why is Manhattan highest?"│
│                                    │                                    │
│                                    ▼                                    │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                      FABRIC DATA AGENT                           │  │
│   │   • Understands natural language questions                       │  │
│   │   • Queries data via ontology bindings                          │  │
│   │   • Uses entity relationships for context                       │  │
│   │   • Reasons using ontology structure (LLM)                      │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                    │              │              │                      │
│         ┌─────────┴──┐    ┌──────┴──────┐    ┌──┴───────────┐         │
│         ▼            ▼    ▼             ▼    ▼              ▼         │
│   ┌──────────┐ ┌──────────┐ ┌───────────────┐                         │
│   │ SEMANTIC │ │ ONTOLOGY │ │  TECHNICAL    │                         │
│   │  LAYER   │ │  LAYER   │ │    LAYER      │                         │
│   │(Measures)│ │ (Fabric  │ │  (Lakehouse   │                         │
│   │          │ │ Ontology │ │   + Delta)    │                         │
│   │ COMPUTES │ │ Item)    │ │               │                         │
│   │ metrics  │ │ EXPLAINS │ │  DOCUMENTS    │                         │
│   │          │ │ why      │ │  what exists  │                         │
│   └────┬─────┘ └──────────┘ └───────────────┘                         │
│        │                                                               │
│        ▼                                                               │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │               NYCTaxiLakehouse (Delta Tables)                 │    │
│   │              2.76M NYC Yellow Taxi Trips                      │    │
│   │          trips | zones | payment_types | rate_codes            │    │
│   └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layer Mapping in Fabric

| Layer | Microsoft Fabric |
|-------|-----------------|
| **Data** | Lakehouse (Delta Tables) |
| **Technical** | Lakehouse metadata + table descriptions |
| **Semantic** | Spark SQL views + Power BI Semantic Model (DAX) |
| **Ontology** | Fabric Ontology item (preview) |
| **AI Agent** | Fabric Data Agent (preview) |

### Prerequisites

- Microsoft Fabric workspace with Fabric-enabled capacity
- Fabric Admin has enabled:
  - Ontology item (preview)
  - Users can create Graph (preview)
  - Users can create and share Data agent item types (preview)
  - Copilot and Azure OpenAI features
- A web browser and Microsoft account with Fabric access

---

## Workshop Structure

Each step offers **two paths**: a programmatic notebook and a manual UI guide. You can follow either or both.

### Data Foundation

| Step | Notebook | Duration | What You Learn |
|------|----------|----------|----------------|
| 00 | [The WHY: From Data to Intelligence](notebooks/00_the_why_from_data_to_intelligence.md) | 20 min | Why ontologies matter, the gap semantic layers leave |
| 01a | [Create Lakehouse & Upload Data (UI)](notebooks/01a_create_lakehouse_and_upload_data.md) | 20 min | **UI guide**: Create Lakehouse, download NYC Taxi data, upload files |
| 01 | [Data Foundation (Notebook)](notebooks/01_data_foundation.py) | 15 min | **Code**: Load and clean data into Delta tables |

### Technical Layer

| Step | Notebook | Duration | What You Learn |
|------|----------|----------|----------------|
| 02 | [Technical Layer (Notebook)](notebooks/02_technical_layer.py) | 15 min | **Code**: Document tables, profile data, explore metadata |
| 02b | [Technical Layer (Fabric UI)](notebooks/02b_technical_layer_fabric_ui.md) | 20 min | **UI guide**: Add descriptions via SQL endpoint, browse schemas, data profiling |

### Semantic Layer (Both Approaches)

| Step | Notebook | Duration | What You Learn |
|------|----------|----------|----------------|
| 03 | [Semantic Layer — Spark SQL Views (Notebook)](notebooks/03_semantic_layer_spark.py) | 20 min | **Code**: 7 reusable metric views with Spark SQL |
| 03b | [Semantic Layer — Power BI DAX (UI)](notebooks/03b_semantic_model_powerbi_dax.md) | 30 min | **UI guide**: 23 DAX measures, relationships, display folders in Power BI Semantic Model |

### Ontology & AI Agent

| Step | Notebook | Duration | What You Learn |
|------|----------|----------|----------------|
| 04 | [The Ontology Gap](notebooks/04_the_ontology_gap.md) | 15 min | See where metrics fail to explain patterns |
| 05 | [Create Fabric Ontology (UI)](notebooks/05_create_fabric_ontology.md) | 25 min | Model entity types, properties, keys, relationships |
| 06 | [Enrich the Ontology (Code + UI)](notebooks/06_enrich_ontology.md) | 20 min | Add zone types, business rules, semantic context |
| 07 | [Preview and Query (UI)](notebooks/07_preview_and_query.md) | 15 min | Explore the ontology graph visually, run graph queries |
| 08 | [Create Data Agent (UI)](notebooks/08_create_data_agent.md) | 15 min | Build an AI agent grounded in the ontology |
| 08b | [Before & After — The Ontology Difference](notebooks/08b_before_and_after_ontology.md) | 20 min | Compare agent with and without business rules — see what the ontology prevents |

### Testing & Reflection

| Step | Notebook | Duration | What You Learn |
|------|----------|----------|----------------|
| 09 | [Intelligent Queries (Notebook)](notebooks/09_intelligent_queries.py) | 20 min | Test the full architecture end-to-end |
| 10 | [Architecture Reflection](notebooks/10_architecture_reflection.md) | 15 min | Lessons learned, limitations, next steps |

### Reference

| Document | Description |
|----------|-------------|
| [Ontology Mapping Reference](resources/ontology_mapping.md) | Mapping of workshop concepts to Fabric entity types, properties, and rules |

**Total duration: ~4 hours (all paths) or ~3 hours (one path per layer)**

---

### Two Paths Through the Workshop

**Path A — Code-First** (Data Engineers, Developers):
> 00 → 01a → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 08b → 09 → 10

**Path B — UI-First** (Analysts, Report Builders):
> 00 → 01a → 01 → 02b → 03b → 04 → 05 → 06 → 07 → 08 → 08b → 09 → 10

**Path C — Comprehensive** (Learn Both):
> 00 → 01a → 01 → 02 + 02b → 03 + 03b → 04 → 05 → 06 → 07 → 08 → 08b → 09 → 10

---

### Key Concepts Introduced

1. **Semantic Layer** — Standardized metric definitions (the "what" and "how")
2. **Ontology** — Formal domain knowledge model (the "why")
3. **Entity Types** — Real-world concepts (Trip, Zone, Borough, PaymentType)
4. **Relationships** — How entities connect (Trip → hasPickupLocation → Zone)
5. **Business Rules** — Encoded domain expertise (cash tips are not recorded)
6. **Data Agent** — AI that queries data through ontology structure
7. **Inference Rules** — Logic that explains patterns (low tips ≠ bad service)
8. **DAX Measures** — Reusable calculations in Power BI Semantic Models
9. **Spark SQL Views** — Reusable metric definitions as SQL views

### References & Inspiration

- [Ontologies, Context Graphs, and Semantic Layers](https://metadataweekly.substack.com/p/ontologies-context-graphs-and-semantic) — Prukalpa Sankar, Metadata Weekly
- [Semantic Layer DuckDB Tutorial](https://motherduck.com/blog/semantic-layer-duckdb-tutorial/) — Simon Spati, MotherDuck
- [Ontology Series](https://medium.com/@aidatamotion/list/ontology-a5accf1ce836) — AI Data Motion
- [Microsoft Fabric Ontology Tutorials](https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-0-introduction) — Microsoft Learn
