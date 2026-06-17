# Step 07: Preview and Query the Ontology

**Duration: 15 minutes | Type: Hands-on (Fabric UI)**

---

## Purpose of This Step

You've built the ontology structure (Step 05) and enriched it with business knowledge (Step 06). Now you need to **verify that it actually works** — that the business context is attached to the right entities, that relationships connect correctly, and that the graph can answer the kinds of questions we'll ask the Data Agent in Step 08.

This step is the "see it with your own eyes" moment before we hand control to AI.

---

## Prerequisites: Ensure the Graph Is Created and Refreshed

Before you can run graph queries, the ontology needs a **Graph** item in your workspace. This is created automatically when you set up the ontology, but the data needs to be ingested.

### Check the Graph

1. Go to your **workspace** (e.g., `intelligent-semantic-layer`)
2. Look for an item with a **Graph** icon — it will have a name like `NYCTaxiOntology_graph` or similar
3. If you see it, click the **three dots (...)** next to it → **Schedule** → **Refresh now**
4. Wait for the refresh to complete (may take a few minutes for the Trip entity with 2.76M rows)

> **Why?** The Graph is a separate queryable store that ingests data from your Lakehouse tables via the ontology bindings. If the graph hasn't been refreshed, queries will return empty results or stale data.

> **Known limitation**: Fabric Graph doesn't support the `Decimal` type. If you see `null` values for some properties, this may be the cause.

> **Known limitation**: When new relationships are added to the Ontology after the Graph was created, the Graph may not auto-sync them. You may need to manually add edges in the Graph item (Model view → Add edge) and configure the mapping table, source/target nodes, and key columns.

---

## Step 7.1: Preview Entity Instances

### Purpose

Confirm that the **business knowledge you encoded in Step 06 is actually attached to entity instances**. A database table stores raw values like `payment_type_id = 2`. The ontology stores that same row with `tip_data_available = "No"` and `business_rule = "CRITICAL: Tips are NOT recorded..."`. This step lets you see that difference.

### 7.1.1: Open the Entity Type Overview

1. Open **NYCTaxiOntology** from your workspace
2. In the left **Entity Types** pane, select `Zone`
3. In the **top ribbon**, click **Entity type overview**
4. Wait for data to load (first load may take a few minutes)

The Entity type overview shows:
- **Entity type details**: Name, key, display name, description
- **Properties**: All bound properties with types
- **Entity instances**: Actual data rows from the `zones` table
- **Relationship graph**: Visual graph tile

### 7.1.2: Explore Zone Instances — Verify Business Context Is Attached

1. In the Entity type overview, scroll down to the **Entity instances** section
2. You should see 265 zone instances
3. Each instance shows properties: `zone_name`, `borough`, `zone_type`, `borough_context`

**What to look for:**
- Find **"JFK Airport"** — verify it shows `zone_type = "Airport"`
- Find **"Midtown Center"** — verify it shows `zone_type = "Business District"`
- Find any Brooklyn zone — verify `borough_context` says "Primarily residential..."

**Why this matters**: Without the ontology, `location_id = 132` is just a number. With the ontology, the Data Agent knows it's JFK Airport, classified as an Airport zone, in Queens. That context is what enables intelligent answers.

> **Troubleshooting**: If data doesn't load:
> - Verify the data binding points to the correct `zones` table
> - Check that your Fabric identity has access to the Lakehouse
> - Try refreshing the Graph (see Prerequisites above)

### 7.1.3: Explore PaymentType Instances — Verify the Tip Data Gap Rule

1. In the left Entity Types pane, select `PaymentType`
2. Click **Entity type overview** in the top ribbon
3. Scroll to **Entity instances**
4. You should see 6 instances: Credit card, Cash, No charge, Dispute, Unknown, Voided trip

**What to look for:**
- **Credit card**: `tip_data_available = "Yes"`, `business_rule` explains tips are recorded
- **Cash**: `tip_data_available = "No"`, `business_rule` starts with "CRITICAL"

**Why this matters**: This is the single most important business rule in the workshop. In the raw data, a cash trip with tip_amount = $0 looks identical to a credit card trip where the rider didn't tip. Without this rule attached to the entity, the Data Agent will treat $0 as "no tip given" instead of "tip unknown" — leading to wrong conclusions about tipping behavior by borough.

### 7.1.4: Explore RateCode Instances — Verify Airport Rate Context

1. Select `RateCode` in the left pane
2. Click **Entity type overview**
3. Scroll to Entity instances — you should see 6 instances

**What to look for:**
- **JFK (code 2)**: `is_airport_rate = "Yes"`, context mentions $52 flat rate
- **Newark (code 3)**: `is_airport_rate = "Yes"`, context mentions surcharge

**Why this matters**: Rate code 2 is just a number in the data. The ontology tells the Data Agent it means "JFK flat rate at $52" — enabling it to classify trips and explain fare patterns.

---

## Step 7.2: Preview the Relationship Graph

### Purpose

Confirm that **entities are connected to each other** through the relationships you defined. Relationships are what allow the Data Agent to answer multi-concept questions like "What is average revenue by borough?" — which requires traversing Trip → Zone → Borough. Without relationships, the agent can only query one table at a time.

### 7.2.1: Access the Relationship Graph

1. In the Entity type overview (for any entity type), find the **Relationship graph** tile
2. Click on the tile to expand it into the full graph view

Alternatively:
1. Select an entity type in the left pane (e.g., `Trip`)
2. Click **Entity type overview** in the top ribbon
3. Find and click the **Relationship graph** tile

### 7.2.2: View the Trip Graph

With the `Trip` entity selected, the relationship graph should show Trip connected to:

- **Zone** via `hasPickupZone` and `hasDropoffZone`
- **PaymentType** via `paidWith`
- **RateCode** via `usesRate`
- **TripType** via `hasTripType`
- **TimeContext** via `occursIn`

**Why this matters**: Each arrow is a path the Data Agent can follow. When someone asks "Why are tips lower in Brooklyn?", the agent traverses: Trip → paidWith → PaymentType (finds the cash tip rule) AND Trip → hasPickupZone → Zone → inBorough → Borough (finds the borough context). Without these connections, the agent can only look at one table.

### 7.2.3: Explore from Zone Perspective

1. Go back and select the `Zone` entity type
2. Open its Entity type overview → Relationship graph
3. You should see Zone connected to:
   - **Trip** via `hasPickupZone` and `hasDropoffZone`
   - **Borough** via `inBorough`
   - **ZoneType** via `hasZoneType`

**Key insight**: Zone is the central hub between trips and geographic context. The path Trip → Zone → Borough is how the agent connects trip-level data to borough-level business knowledge.

---

## Step 7.3: Run Graph Queries

### Purpose

Test that the graph can **retrieve specific entities and traverse relationships** — the same operations the Data Agent will perform when answering questions. We focus on two queries that directly support the workshop's core story: the cash tip data gap and the geographic context chain.

### How the Query Builder Works

The query builder is located **inside the Relationship graph view** — it appears as a toolbar at the top of the graph.

- **Add filter**: Click to select an entity type → property → value
- **Run query**: Executes the filter and shows matching instances
- **Clear query**: Resets filters and results

### Query 1: "Which payment types have no tip data?"

**What this proves**: The cash tip data gap — the workshop's most critical business rule — is encoded in the graph and queryable.

1. Select **PaymentType** in the left pane → **Entity type overview** → **Relationship graph**
2. Click **Add filter** → **PaymentType** → **tip_data_available** → equals → `No`
3. Click **Run query**

**Expected result**: 1 node — **Cash** (payment_type_id = 2)

This is the rule that prevents the Data Agent from making the #1 mistake in taxi data analysis: treating $0 cash tips as "no tip given."

4. Click **Clear query** when done

### Query 2: "Which boroughs contain Airport zones?" (Multi-hop traversal)

**What this proves**: The graph can traverse multiple relationships in one query — from ZoneType through Zone to Borough. This is the kind of navigation that's difficult with SQL joins but natural in a graph.

1. Select **ZoneType** in the left pane → **Entity type overview** → **Relationship graph**
2. Click **Add filter** → **ZoneType** → **zone_type** → equals → `Airport`
3. In the Components pane, check:
   - ☑ Nodes > ZoneType
   - ☑ Nodes > Zone
   - ☑ Nodes > Borough
   - ☑ Edges > hasZoneType
   - ☑ Edges > inBorough
4. Click **Run query**

**Expected result**: The Airport ZoneType node → connected to JFK, LaGuardia, Newark zones → connected to Queens and EWR boroughs.

This is the path the Data Agent follows when you ask "How do airport trips compare to regular trips?" — it knows which zones are airports, which boroughs they're in, and can filter trips accordingly.

5. Click **Clear query** when done

### Troubleshooting Graph Queries

| Problem | Solution |
|---|---|
| **"Run query" returns nothing** | The Graph needs to be refreshed. Go to workspace → find the Graph item → ... → Schedule → Refresh now |
| **Queries are very slow** | Queries involving Trip (2.76M rows) are heavy. Filter to small dimension entities (Zone, PaymentType, RateCode) for faster results |
| **Properties show as null** | Fabric Graph doesn't support the `Decimal` type. Properties with decimal values may show as null |
| **"Add filter" doesn't show my property** | The property may not be bound in the ontology. Go back to Step 05/06 and verify data bindings |
| **Graph item not found in workspace** | Ensure both Ontology and Graph tenant settings are enabled by your Fabric admin |
| **New relationships not showing in graph** | The Graph item may not auto-sync new ontology relationships. Open the Graph item → Model view → Add edge → configure mapping table and key columns manually |

---

## Step 7.4: Validate — Is the Ontology Ready for the Data Agent?

### Purpose

Final checklist before handing the ontology to the Data Agent in Step 08. If any of these checks fail, go back to Step 05/06 and fix the issue.

### Check 1: Business context is attached to zones

1. Open Zone entity type overview
2. Scroll through Entity instances and select any Manhattan zone
3. Confirm `borough_context` describes the business context (e.g., "Dominates taxi activity with ~90% of trips...")
4. Confirm `zone_type` is populated (e.g., "Business District", "Tourist Zone")

### Check 2: Cash tip rule is visible

1. Open PaymentType entity type overview
2. Find the Cash instance (payment_type_id = 2)
3. Confirm `tip_data_available = "No"` and `business_rule` starts with "CRITICAL"

### Check 3: Relationships connect Trip to context

1. Open Trip entity type overview → Relationship graph
2. Confirm Trip connects to Zone, PaymentType, RateCode, TripType, and TimeContext
3. Confirm Zone connects to Borough and ZoneType

If all three checks pass, your ontology is ready. The structure, the data, and the business knowledge are all in place for the Data Agent to use.

---

## Key Takeaways

1. **The ontology is not just a schema** — it contains actual data with business meaning attached to every instance
2. **Relationships are paths for reasoning** — the Data Agent follows these paths to connect trip data with business context
3. **The cash tip data gap is the key test** — if the PaymentType entity shows `tip_data_available = "No"` for Cash, the ontology is doing its job
4. **The Graph must be refreshed** — after data or relationship changes, refresh the Graph item in your workspace
5. **Everything here powers Step 08** — the entity instances, relationships, and business rules you just verified are what the Data Agent uses to answer questions intelligently

---

## References

- [Tutorial: Preview the ontology — Microsoft Learn](https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-3-preview-ontology)
- [Use preview experience — Microsoft Learn](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-use-preview-experience)

---

**Next: [Step 08 — Create the Data Agent →](08_create_data_agent.md)**
