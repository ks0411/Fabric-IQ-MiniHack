# Step 08b: Before and After — The Ontology Difference

**Duration: 20 minutes | Type: Hands-on (Fabric UI) + Discussion**

---

## The Experiment

We will ask the **same questions** to two versions of the Data Agent:

1. **Agent WITHOUT business rules** — ontology structure only, empty agent instructions
2. **Agent WITH business rules** — ontology structure + the full agent instructions from Step 08

This directly demonstrates whether the ontology and business rules actually prevent mistakes — or whether a smart LLM can figure things out on its own.

---

## Step 8b.1: Create a "Naive" Agent (No Business Rules)

### Option A: Temporarily Clear Instructions

1. Open your existing `NYCTaxiAgent`
2. Go to **Agent instructions**
3. **Select all** the instructions text and **cut** it (Ctrl+X) — save it in a text file so you can paste it back later
4. Replace with just this single line:

```
You are a data analyst. Answer questions using the available data.
```

5. Click **Save**

### Option B: Create a Second Agent

1. In your workspace, click **+ New item** → **Data agent (preview)**
2. Name: `NYCTaxiAgent_Naive`
3. Add the same ontology (`NYCTaxiOntology`) as data source
4. Set agent instructions to:

```
You are a data analyst. Answer questions using the available data.
```

5. Click **Save**

---

## Step 8b.2: Test the Naive Agent (No Business Rules)

Ask the following questions and **write down** the agent's responses. Pay close attention to what it gets right and what it gets wrong.

### Question 1: "What are average tips by borough?"

**Ask the naive agent:**
```
What are average tips by borough?
```

**What to watch for:**
- Does it include cash payments in the tip average?
- Does it warn you that cash tips are not recorded?
- Does it filter to credit card only?

**Likely naive response:**
> "Average tips by borough: Manhattan $3.80, Queens $3.20, Brooklyn $2.10, Bronx $1.50..."

**The mistake**: These numbers include cash trips where tip = $0. The agent treats $0 as "no tip given" when it really means "tip not recorded." Brooklyn and Bronx appear to tip less, but they just use more cash.

---

### Question 2: "Why are tips lower in Brooklyn compared to Manhattan?"

**Ask the naive agent:**
```
Why are tips lower in Brooklyn compared to Manhattan?
```

**What to watch for:**
- Does it mention the cash tip data gap?
- Does it blame service quality or rider behavior?
- Does it distinguish between "recorded tips" and "actual tips"?

**Likely naive response:**
> "Tips are lower in Brooklyn because: shorter trip distances lead to lower fares and smaller tips, less tourist activity, and possibly different service expectations..."

**The mistake**: It gives plausible-sounding but WRONG reasons. The real reason is that Brooklyn has more cash payments, and cash tips are invisible in the data. Without the business rule, the agent cannot know this.

---

### Question 3: "Which borough has the best tipping behavior?"

**Ask the naive agent:**
```
Which borough has the best tipping behavior?
```

**What to watch for:**
- Does it rank boroughs by raw average tip?
- Does it account for payment method mix?
- Does it qualify the answer with data limitations?

**Likely naive response:**
> "Manhattan has the best tipping behavior with an average tip of $3.80, followed by Queens at $3.20. Bronx has the lowest at $1.50."

**The mistake**: This is a confident but misleading answer. It conflates "highest recorded tips" with "best tipping behavior." A borough where 50% pay cash will always look like it tips less — even if actual tipping is identical.

---

### Question 4: "What is the average revenue per trip?"

**Ask the naive agent:**
```
What is the average revenue per trip?
```

**What to watch for:**
- Does it define revenue correctly?
- Does it explain what "revenue" includes vs excludes?
- Does it mention the JFK flat rate or other special cases?

**Likely naive response:**
> "The average revenue per trip is $18.50."

**Not wrong, but shallow**: The number is correct, but without context it's meaningless. Is $18.50 good? Does it vary by trip type? The agent doesn't know about airport flat rates, congestion surcharges, or the revenue calculation formula.

---

### Question 5: "Classify this trip: JFK to Midtown, 8 AM Tuesday, rate code 2"

**Ask the naive agent:**
```
What type of trip is this: pickup at JFK Airport, dropoff in Midtown Manhattan, 8 AM on a Tuesday, rate code 2, fare $52?
```

**What to watch for:**
- Does it identify it as an airport trip?
- Does it identify it as a commute trip?
- Does it mention the $52 flat rate?
- Does it predict higher tips?

**Likely naive response:**
> "This appears to be a trip from JFK Airport to Midtown. The fare of $52 suggests it may be a flat rate trip."

**Partial at best**: It may guess "airport trip" but won't systematically classify it as Airport + Commute + Long Distance, won't explain the JFK flat rate business rule, and won't predict tip behavior.

---

## Step 8b.3: Record Naive Agent Results

Fill in this table:

| Question | Naive Agent Response | Correct? | Key Mistake |
|---|---|---|---|
| Avg tips by borough | | | |
| Why Brooklyn tips lower? | | | |
| Best tipping borough? | | | |
| Avg revenue per trip? | | | |
| Classify JFK trip | | | |

---

## Step 8b.4: Switch to the Full Agent (With Business Rules)

### If You Used Option A (Cleared Instructions):

1. Open `NYCTaxiAgent`
2. Go to **Agent instructions**
3. **Paste back** the full instructions from Step 08 (the ones you saved)
4. Click **Save**

### If You Used Option B (Second Agent):

1. Open the original `NYCTaxiAgent` (the one with full instructions from Step 08)

---

## Step 8b.5: Test the Full Agent (With Business Rules)

Ask the **exact same questions** and compare.

### Question 1: "What are average tips by borough?"

**Expected full agent response:**
> "**Important caveat**: Tip data is only available for credit card payments. Cash tips are not recorded in the data.
>
> Filtering to credit card payments only:
> - Manhattan: $4.85 avg tip
> - Queens: $4.60 avg tip
> - Brooklyn: $4.20 avg tip
> - Bronx: $3.80 avg tip
>
> Note: Lower recorded tips in outer boroughs partly reflect higher cash payment usage, not necessarily lower tipping."

**The difference**: The full agent applies the CashTipDataGap business rule automatically.

---

### Question 2: "Why are tips lower in Brooklyn compared to Manhattan?"

**Expected full agent response:**
> "Lower *recorded* tips in Brooklyn reflect several factors:
>
> 1. **Cash tip data gap**: Cash payments do NOT record tips. Brooklyn has a higher cash payment rate than Manhattan, making tips appear lower in the data.
> 2. **Payment method mix**: Manhattan has ~70%+ credit card usage. Brooklyn is lower. Since only credit card tips are recorded, Brooklyn's tip data is less complete.
> 3. **Demographics**: Manhattan has more business travelers and tourists who typically tip higher amounts.
> 4. **Zone types**: Manhattan is dominated by Business Districts and Tourist Zones where tipping norms are higher.
>
> **Key insight**: Lower recorded tips ≠ lower actual tips. The cash tip data gap is the primary driver of this apparent difference."

**The difference**: The full agent doesn't just explain — it corrects the premise of the question.

---

### Question 3: "Which borough has the best tipping behavior?"

**Expected full agent response:**
> "This question cannot be answered accurately from this dataset alone.
>
> **Why**: Cash tips (payment_type = 2) are not recorded. Boroughs with higher cash usage will *appear* to tip less, but their actual tipping may be similar or even higher.
>
> For credit card payments only, tip rates are relatively similar across boroughs (15-20% of fare). The main difference is trip volume and fare amounts, not tipping behavior."

**The difference**: The full agent **refuses to answer misleadingly** — it flags the data limitation instead of giving a confident wrong answer.

---

### Question 4: "What is the average revenue per trip?"

**Expected full agent response:**
> "Average revenue per trip (fare + tip): $18.50
>
> This varies significantly by context:
> - **JFK Airport trips**: ~$60 (fixed $52 fare + higher tips)
> - **Manhattan business districts**: ~$16 (shorter trips, high volume)
> - **Long distance trips**: ~$45 (distance-based metered fare)
> - **Short trips (< 2 mi)**: ~$10
>
> Revenue = fare_amount + tip_amount. Note that total_amount includes additional surcharges and fees."

**The difference**: The full agent breaks down the average and explains what "revenue" means.

---

### Question 5: "Classify this trip: JFK to Midtown, 8 AM Tuesday, rate code 2"

**Expected full agent response:**
> "This trip classifies as:
>
> - **Airport Trip**: Rate code 2 = JFK flat rate ($52 to Manhattan)
> - **Commute Trip**: 8 AM on a Tuesday = weekday rush hour
> - **Long Distance**: JFK to Midtown is approximately 15 miles
>
> Business context:
> - Fixed $52 fare (predictable revenue)
> - Higher tips expected (business travelers, airport service)
> - Rush hour: expect longer duration due to traffic
> - Congestion surcharge may apply for Manhattan dropoff"

**The difference**: Systematic multi-label classification with business context.

---

## Step 8b.6: Compare Side by Side

| Question | Naive Agent | Full Agent | What Changed |
|---|---|---|---|
| Avg tips by borough | Raw averages including $0 cash tips | CC-only averages + cash gap warning | **Prevents wrong numbers** |
| Why Brooklyn tips lower? | Blames service/behavior/distance | Identifies cash data gap as primary cause | **Prevents wrong conclusion** |
| Best tipping borough? | Confidently ranks by raw average | Refuses to answer misleadingly | **Prevents false confidence** |
| Avg revenue per trip? | Single number, no context | Breakdown by trip type + definition | **Adds meaning** |
| Classify JFK trip | Maybe identifies airport | Airport + Commute + Long Distance + context | **Adds classification logic** |

---

## Step 8b.7: The Takeaway

### What the LLM Can Do Without the Ontology
- Query data correctly
- Compute aggregations
- Make reasonable-sounding guesses about "why"

### What the LLM CANNOT Do Without the Ontology
- Know that cash tips are not recorded (it's not in the data — tip_amount = $0 looks like "no tip")
- Distinguish between "zero tip recorded" and "tip unknown"
- Know that JFK rate code 2 means a flat $52 fare
- Classify trips into business categories
- Refuse to answer when the data doesn't support the question

### The Fundamental Problem

The cash tip data gap is **invisible in the data itself**. There is no column called `is_tip_recorded`. There is no flag saying "this $0 means unknown, not zero." The data looks perfectly clean and complete — the numbers just lead to wrong conclusions.

This is exactly the kind of knowledge that:
- **Cannot** be derived from the data
- **Cannot** be inferred by an LLM (no matter how smart)
- **Must** be provided by domain experts
- **Must** be structured and attached to the data

That's what the ontology does. That's why it matters.

---

## Step 8b.8: Clean Up

If you created a second agent (`NYCTaxiAgent_Naive`), you can delete it or keep it for future demonstrations.

If you cleared the instructions from `NYCTaxiAgent`, make sure they are restored (paste back the full instructions from Step 08).

---

**Next: [Step 09 — Intelligent Queries (End-to-End Test) →](09_intelligent_queries.py)**
