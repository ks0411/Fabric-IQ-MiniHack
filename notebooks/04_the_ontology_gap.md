# Step 04: The Ontology Gap — Where Metrics Fail to Explain

**Duration: 15 minutes | Type: Conceptual + Interactive**

---

## The Semantic Layer Has Limits

We built a solid semantic layer in Step 03. It computes metrics consistently and correctly. But now let's see where it breaks down.

### Exercise: Ask These Questions to Your Semantic Views

Run each query in a Fabric notebook cell and think about what's **missing** from the answer.

---

### Question 1: "Why is Manhattan revenue 5x higher than Brooklyn?"

```python
spark.sql("""
    SELECT borough, trip_count, total_revenue, avg_fare
    FROM v_revenue_by_borough
    ORDER BY total_revenue DESC
""").show()
```

**What the semantic layer tells you:**
| Borough     | Trips     | Revenue     | Avg Fare |
|--------    -|-------    |---------    |----------|
| Manhattan   | 2,100,000 | $44,075,886 | $14.23 |
| Brooklyn    | 285,000   | $8,567,890  | $16.10 |

**What it CANNOT tell you:**
- Manhattan has ~90% of trips because of business district concentration
- Limited parking in Manhattan drives taxi demand
- Tourist activity generates consistent demand across the week
- Brooklyn is primarily residential with alternative transportation

The numbers alone lead to: "Manhattan has more trips." The ontology explains: "Manhattan has more trips **because** of business density, tourism, and limited parking."

---

### Question 2: "Why are tips lower in Brooklyn?"

```python
# The WRONG way (what most analysts do)
spark.sql("""
    SELECT borough, avg_tip
    FROM v_revenue_by_borough
    ORDER BY avg_tip DESC
""").show()
```

**The naive conclusion:** "Brooklyn drivers provide worse service."

**What the ontology knows (and the semantic layer doesn't):**

1. **Cash Tip Data Gap**: Cash tips are NOT recorded. They show as $0. Brooklyn has higher cash usage, making tips *appear* lower.

2. **Demographic Effect**: Manhattan has business travelers and tourists who tip more (expense accounts, unfamiliarity with norms). Brooklyn has local residents making routine trips.

3. **Zone Type Effect**: Business districts see 15-20% tip rates. Residential zones see lower, routine tips.

**The correct conclusion:** "Lower *recorded* tips in Brooklyn reflect payment method mix and demographics, NOT service quality."

---

### Question 3: "What does 'revenue' mean?"

```python
# The semantic layer gives us the formula
print("total_revenue = SUM(fare_amount + tip_amount)")
```

But revenue means different things in different contexts:

- **For airport trips**: Revenue is predictable (JFK flat $52 rate)
- **For cash trips**: Revenue understates actual income (tips not included)
- **For rush hour**: Revenue per trip may be lower but volume compensates
- **For long distance**: High per-trip revenue but lower turnover

A formula doesn't capture this. An ontology does.

---

### Question 4: "Classify this trip: JFK to Midtown, 8 AM Tuesday, $52 fare"

```python
# The semantic layer has no concept of trip "types"
# It can compute metrics but can't classify
print("Error: Semantic layer has no classify_trip() method")
```

**What the ontology knows:**
- **AirportTrip**: rate_code = 2 (JFK flat rate)
- **CommuteTrip**: 8 AM on a weekday (rush hour)
- **LongDistanceTrip**: JFK to Midtown is ~15 miles
- **Business context**: "$52 flat rate, higher tips expected, predictable revenue"

---

## The Gap Visualized

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHAT WE CAN ANSWER TODAY                      │
│                                                                  │
│  ✅ "What is revenue by borough?"          → $44M, $15M, $8.5M │
│  ✅ "What is average tip by payment type?" → $3.40 CC, $0 Cash  │
│  ✅ "How many airport trips?"              → 45,000             │
│  ✅ "What is credit card rate?"            → 70%                │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                    WHAT WE CANNOT ANSWER                         │
│                                                                  │
│  ❌ "WHY is Manhattan revenue highest?"                          │
│  ❌ "WHY are tips lower in Brooklyn?"                            │
│  ❌ "WHAT should I know before analyzing tips?"                  │
│  ❌ "CLASSIFY this trip" (Airport? Commute? Long distance?)     │
│  ❌ "WHAT business rules affect this metric?"                    │
│  ❌ "HOW should I interpret low tips in outer boroughs?"        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## What We Need: Domain Knowledge as Structure

The knowledge to answer "why" questions exists — in the heads of domain experts, in documentation, in tribal knowledge. The problem is that it's not structured, not queryable, and not accessible to AI agents.

An **ontology** structures this knowledge into:

| Ontology Concept | Example | Purpose |
|---|---|---|
| **Entity Types** | Trip, Zone, Borough, PaymentType | Model real-world concepts |
| **Properties** | fareAmount, tipAmount, borough | Attributes with types and meaning |
| **Relationships** | Trip → hasPickupLocation → Zone | How concepts connect |
| **Business Rules** | "Cash tips not recorded" | Encoded domain expertise |
| **Classifications** | AirportTrip, CommuteTrip | Trip type taxonomy |
| **Context** | "Manhattan dominates due to density" | Explanatory knowledge |

### From Conceptual Model to Fabric Ontology

We will capture domain knowledge using the **Fabric Ontology item** — a native Fabric feature that models concepts through a visual interface.

| Concept | Fabric Ontology |
|---|---|
| Class | Entity Type |
| Attribute | Property (Static) |
| Relationship | Relationship Type |
| Business context | Entity description / Agent instruction |
| Classification logic | Derived property or Agent instruction |

---

## The Domain Model We Will Build

We will model:

- **8 core entity classes**: Trip, Location, Borough, PaymentType, RateType, Vendor, ZoneType, TimeContext
- **5 borough instances**: Manhattan, Brooklyn, Queens, Bronx, Staten Island
- **4 payment types**: CreditCard, Cash, NoCharge, Dispute
- **6 rate types**: Standard, JFK, Newark, Nassau/Westchester, Negotiated, Group
- **6 trip type subclasses**: Airport, Commute, LongDistance, Night, Weekend, Short
- **6 zone type subclasses**: Airport, Business, Residential, Tourist, Transit, Entertainment
- **5 time contexts**: RushHour, OffPeak, NightTime, WeekendDay, WeekendNight
- **10+ inference rules**: CashTipDataGap, ManhattanDominance, TipAnalysis, etc.
- **20+ zone instances**: JFK, LaGuardia, Midtown, Times Square, etc.

In the next steps, we'll build the most important parts of this ontology using Fabric's native ontology feature.

---

**Next: [Step 05 — Create Fabric Ontology →](05_create_fabric_ontology.md)**
