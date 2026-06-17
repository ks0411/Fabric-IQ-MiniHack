# Step 08: Create the Data Agent

**Duration: 15 minutes | Type: Hands-on (Fabric UI)**

---

## The AI Agent: Bringing Everything Together

The **Fabric Data Agent** turns your ontology into a conversational analytics experience. It can:

1. Accept natural language questions
2. Query entity data via ontology bindings
3. Use relationships for context
4. Explain results using your business rules

---

## Step 8.1: Create the Data Agent Item

1. Navigate to your **Fabric workspace**
2. Click **+ New item**
3. Search for **Data agent (preview)** and select it
4. Name: `NYCTaxiAgent`
5. Click **Create**

---

## Step 8.2: Add the Ontology as Data Source

1. In the Data Agent editor, click **Add a data source**
2. Search for `NYCTaxiOntology`
3. Click **Add**
4. You should see the ontology and its entity types in the **Explorer panel**:
   - Trip
   - Zone
   - PaymentType
   - RateCode
   - Borough (if added in Step 06)
   - ZoneType (if added in Step 06)
   - TripType (if added in Step 06)
   - TimeContext (if added in Step 06)
   - BusinessRule (optional, if added in Step 06)

The Data Agent now has access to all entity types, properties, and relationships defined in the ontology.

---

## Step 8.3: Configure Agent Instructions

This is where we encode business knowledge and reasoning rules for the agent.

1. Select **Agent instructions** from the menu ribbon
2. Add the following instructions:

```
You are an expert NYC taxi data analyst with access to NYC Yellow Taxi trip data (January 2024, ~2.76 million trips).

CRITICAL BUSINESS RULES — You MUST apply these when answering:

1. CASH TIP DATA GAP: Cash payments (payment_type = 2) do NOT record tips. Tip amounts show as $0 for cash trips. When analyzing tips, ALWAYS filter to credit card payments (payment_type = 1) only. Lower recorded tips in outer boroughs reflect higher cash usage, NOT worse service.

2. MANHATTAN DOMINANCE: Manhattan generates ~90% of all yellow taxi trips. This is due to business district concentration, tourist activity, and limited parking. Manhattan will dominate any volume or revenue metric.

3. JFK FLAT RATE: Rate code 2 means a fixed $52 fare to/from JFK Airport to Manhattan. This provides predictable revenue and typically higher tips.

4. BOROUGH CONTEXT:
   - Manhattan: Business/tourist hub, highest demand, ~90% of trips
   - Queens: Contains JFK and LaGuardia airports, high airport trip volume
   - Brooklyn: Primarily residential, lower taxi usage, more cash payments
   - Bronx: Lower activity, higher cash payment rate
   - Staten Island: Lowest activity, limited yellow cab service

5. ZONE TYPES: Zones are classified as Airport, Business District, Tourist Zone, Transit Hub, Entertainment District, or Residential. Business districts have high weekday demand. Tourist zones have consistent demand. Airport zones have high per-trip revenue.

6. TRIP CLASSIFICATION:
   - Airport Trip: rate_code_id IN (2, 3) or pickup/dropoff at location 1, 132, or 138
   - Commute Trip: Weekday rush hours (7-9 AM, 5-8 PM)
   - Long Distance: trip_distance > 10 miles
   - Short Trip: trip_distance < 2 miles
   - Night Trip: pickup hour >= 22 or < 5

7. REVENUE CALCULATION: Trip revenue = fare_amount + tip_amount. The total_amount field includes additional surcharges and fees.

8. TIME PATTERNS: Rush hours (7-9 AM, 5-8 PM weekdays) have highest demand. Night trips (10 PM-5 AM) are entertainment-focused. Weekends have different geographic patterns than weekdays.

Support group by in GQL

When answering questions:
- Provide actual numbers from the data
- Explain WHY patterns exist using the business rules above
- Flag the cash tip data gap whenever tip analysis is involved
- Distinguish between recorded data and actual behavior
```

3. Click **Save**

> **Why "Support group by in GQL"?** This is a known requirement for Fabric Data Agents to enable aggregation queries. Without it, queries like "total revenue by borough" may fail.

---

## Step 8.4: How the Data Agent Uses Your Ontology

The Data Agent works because of two inputs:

1. **Ontology bindings** provide the schema and relationships for querying data
2. **Agent instructions** provide business rules and explanations

---

## Step 8.5: Test the Data Agent

Now test with a set of questions that exercise both data retrieval and business reasoning.

### Test 1: Basic Data Query

```
What is the total revenue by borough?
```

**Expected behavior**: The agent queries Trip entities joined with Zone entities, groups by `borough`, and sums `fare_amount + tip_amount`.

**Expected answer**: Numbers showing Manhattan dominant (~$44M), followed by Queens, Brooklyn, etc.

### Test 2: "Why" Question

```
Why is Manhattan revenue so much higher than other boroughs?
```

**Expected behavior**: The agent provides numbers AND context from the agent instructions (business district concentration, tourist activity, limited parking, ~90% of trips).

### Test 3: Tip Analysis (Tests the Critical Business Rule)

```
What are average tips by borough?
```

**Expected behavior**: The agent should note the cash tip data gap — ideally filtering to credit card payments or at minimum flagging that cash tips are not recorded.

### Test 4: Airport Analysis

```
How do airport trips compare to regular trips in terms of revenue?
```

**Expected behavior**: Uses rate_code_id filtering and zone information to compare airport vs. non-airport trips.

### Test 5: Classification Question

```
If a trip goes from JFK Airport to Midtown at 8 AM on a Tuesday with rate code 2, what type of trip is it?
```

**Expected behavior**: Classifies as Airport Trip (rate code 2) + Commute Trip (8 AM weekday) + likely Long Distance (JFK to Midtown is ~15 miles).

### Test 6: The Killer Question

```
Why are tips lower in Brooklyn compared to Manhattan?
```

**Expected behavior**: This is the question that demonstrates the full value of the ontology. The agent should explain:
1. Cash tips are NOT recorded (data gap)
2. Brooklyn has higher cash usage
3. Demographics differ (local vs. tourist/business)
4. Zone types differ (residential vs. business district)
5. Lower recorded tips ≠ lower actual tips

---

## Step 8.6: Capture Your Results

Fill in this table as you test:

| Question | What to look for | Notes |
|---|---|---|
| Revenue by borough | Numbers + Manhattan dominance context | |
| Why Manhattan highest? | Context grounded in business rules | |
| Tips by borough | Cash tip data gap is flagged | |
| Why Brooklyn tips lower? | Multi-factor explanation + data gap caveat | |
| Classify JFK trip | Airport + Commute + Long Distance | |

If the agent responses are off, refine your **Agent instructions** and re-test the same questions.

---

**Next: [Step 09 — Intelligent Queries (End-to-End Test) →](09_intelligent_queries.py)**
