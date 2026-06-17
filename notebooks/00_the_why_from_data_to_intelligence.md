# Step 00: The WHY — From Data to Intelligence

**Duration: 20 minutes | Type: Conceptual**

---

## The Journey: Data → Metadata → Semantic Layer → Ontology

Every data platform follows an evolutionary path. Understanding where you are on this path — and where you need to go — is the key insight of this workshop.

### Level 1: Raw Data

```
trips table: 2,764,118 rows × 19 columns
```

You have numbers. You can query them. But you need to know SQL, understand the schema, and figure out the joins yourself. Every analyst writes their own version of "revenue."

**What you can answer:** "Give me the data."

### Level 2: Technical Metadata

```
trips.tip_amount: DECIMAL — "Tip paid to driver"
trips.payment_type: INTEGER — "1=Credit, 2=Cash"
zones.borough: VARCHAR — "NYC administrative district"
```

Now you know what columns exist, their types, and basic descriptions. A data catalog (like Microsoft Purview or Fabric's built-in metadata) gives you this.

**What you can answer:** "What data exists? What are the column types?"

### Level 3: Semantic Layer

```yaml
measures:
  total_revenue: (fare_amount + tip_amount).sum()
  avg_tip: tip_amount.mean()
  credit_card_rate: (payment_type == 1).mean()
```

Now you have standardized metric definitions. Every analyst computes revenue the same way. No more "my revenue doesn't match yours" debates.

**What you can answer:** "What is revenue by borough?" → $44M Manhattan, $15M Queens...

### Level 4: Ontology (Where This Workshop Takes You)

```
Manhattan: "Dominates taxi activity with ~90% of all trips.
           Business district concentration, tourist activity, limited parking."

Cash Payment: "CRITICAL: Tips are NOT recorded in data.
              Tip analysis should exclude cash trips."

Low tips in Brooklyn: "Reflects demographics, NOT service quality.
                      Higher cash usage means tips are invisible in data."
```

Now you have **domain knowledge** encoded in a structured, queryable format. An AI agent can look up why Manhattan revenue is high, why Brooklyn tips appear low, and what to watch out for when analyzing tips.

**What you can answer:** "WHY is Manhattan revenue 5x higher?" → Business density, tourist activity, limited parking drives taxi demand.

---

## The Key Insight: "Meaning Is Not the Same as Measurement"

This phrase from [Prukalpa Sankar's analysis](https://metadataweekly.substack.com/p/ontologies-context-graphs-and-semantic) captures the core problem:

> YAML-based semantic layer definitions capture only syntactic relationships — metric formulas and dimension mappings. They don't capture semantic richness. For AI/LLM agents that need to **reason** about data, ontologies are essential.

### What YAML Captures (Semantic Layer)

```yaml
avg_tip: _.tip_amount.mean()
```

This tells us **how** to calculate. Nothing more.

### What an Ontology Captures

```
tipAmount:
  - Description: "Tip paid (only recorded for credit card)"
  - Maps to: trips.tip_amount
  - Unit: USD
  - Business Rule: "Only available for credit card payments (payment_type = 1)"

CashTipDataGap (Inference Rule):
  - Condition: payment_type = 2
  - Inference: "Tip amount is unknown (recorded as $0)"
  - Context: "Cash tips given directly to driver, not captured in data.
              ALWAYS exclude cash payments from tip analysis."
```

This tells us **what it means**, **when it's valid**, and **how to interpret it**.

---

## A Concrete Example: The Tip Analysis Trap

Without an ontology, here's what happens:

### Analyst asks: "What are average tips by borough?"

```sql
SELECT z.borough, AVG(t.tip_amount) as avg_tip
FROM trips t JOIN zones z ON t.pickup_location_id = z.location_id
GROUP BY z.borough
ORDER BY avg_tip DESC
```

| Borough | Avg Tip |
|---------|---------|
| Manhattan | $3.45 |
| Queens | $2.87 |
| Brooklyn | $2.10 |
| Bronx | $1.45 |

### Analyst concludes: "Bronx drivers provide worse service because tips are lowest."

**This conclusion is WRONG.** But the semantic layer has no way to tell them that.

### What the ontology knows:

1. **Cash tips are NOT recorded.** The $0 tip for cash trips drags down the average.
2. **Bronx has higher cash usage (~50%).** Half the tips are invisible.
3. **Lower tips reflect demographics,** not service quality — local residents vs. tourists.
4. **To analyze tips correctly,** you MUST filter to credit card payments only.

The correct query:

```sql
SELECT z.borough, AVG(t.tip_amount) as avg_tip
FROM trips t JOIN zones z ON t.pickup_location_id = z.location_id
WHERE t.payment_type = 1  -- Credit card only!
GROUP BY z.borough
```

**An ontology prevents this mistake by encoding the business rule.**

---

## When Do You Need an Ontology?

### You DON'T need an ontology when:

- Your analysts know the domain deeply and don't need explanations
- Questions are purely quantitative ("show me revenue by month")
- You're building dashboards for known, recurring questions
- Small teams with shared context

### You DO need an ontology when:

- Users ask "why" questions that require domain knowledge
- You're building AI/LLM interfaces that need business context
- Analysts are exploring unfamiliar data domains
- Business rules affect how to interpret data (cash tips, flat rates, etc.)
- You want to prevent misinterpretation of metrics

---

## What Microsoft Fabric Ontology Gives Us

Fabric's Ontology item (preview) provides a native way to model domain knowledge:

| Fabric Concept | What It Represents | Our Example |
|---|---|---|
| **Entity Type** | A real-world concept | Trip, Zone, Borough, PaymentType |
| **Property** | An attribute of an entity | fareAmount, tipAmount, borough |
| **Entity Key** | Unique identifier | trip_id, location_id |
| **Relationship Type** | How entities connect | Trip → hasPickupLocation → Zone |
| **Data Binding** | Connection to actual data | Entity → Lakehouse delta table |
| **Data Agent** | AI that queries via ontology | Natural language → structured query |

### The Architecture We're Building

```
┌────────────────────────────────────────────────────┐
│           User: "Why are tips lower in Brooklyn?"   │
│                          │                          │
│                          ▼                          │
│              ┌───────────────────┐                  │
│              │   Data Agent      │                  │
│              │   (Fabric AI)     │                  │
│              └─────────┬─────────┘                  │
│                        │                            │
│           ┌────────────┼────────────┐               │
│           ▼            ▼            ▼               │
│    ┌────────────┐ ┌─────────┐ ┌──────────┐         │
│    │ Semantic   │ │Ontology │ │Technical │         │
│    │ Views      │ │ (Fabric │ │ Layer    │         │
│    │(Spark SQL) │ │  Item)  │ │(Metadata)│         │
│    └─────┬──────┘ └────┬────┘ └────┬─────┘         │
│          │             │           │                │
│          ▼             ▼           ▼                │
│    ┌────────────────────────────────────────┐       │
│    │     NYCTaxiLakehouse (Delta Tables)     │       │
│    │   trips | zones | payment_types | rates │       │
│    └────────────────────────────────────────┘       │
└────────────────────────────────────────────────────┘
```

---

## What We Build In This Workshop

By the end of this workshop, you will have:

1. **A Fabric Lakehouse** with 2.76M NYC taxi trips (Step 01)
2. **Documented tables** with column descriptions and business context (Step 02)
3. **Semantic views** that compute metrics consistently (Step 03)
4. **A Fabric Ontology** modeling Trips, Zones, Boroughs, and Payment Types (Steps 05-06)
5. **Entity relationships** connecting trips to locations, payment methods, and rate types (Step 06)
6. **Business rules** encoded as entity properties and descriptions (Step 06)
7. **A Data Agent** that answers natural language questions using the ontology (Step 08)
8. **End-to-end intelligence** — from "what is revenue?" to "why is Manhattan highest?" (Step 09)

Let's begin.

---

**Next: [Step 01 — Data Foundation →](01_data_foundation.py)**
