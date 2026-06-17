# Step 06: Enrich the Ontology with Business Knowledge

**Duration: 20 minutes | Type: Hands-on (Fabric UI + Notebook)**

---

## Why Enrichment Matters

In Step 05, we created the structural skeleton of our ontology — entity types, properties, and relationships. But the real value of an ontology comes from **business knowledge**: the rules, context, and meaning that transforms raw metadata into intelligence.

In Fabric, we encode this knowledge through:
1. **Additional entity properties** (computed columns in the Lakehouse)
2. **Entity descriptions** (in the ontology UI)
3. **Data Agent instructions** (in Step 08)

---

## Step 6.1: Add Business Context as Computed Columns

Run this in a Fabric notebook to add enrichment columns to our tables.

### 6.1.1: Enrich the Zones Table with Zone Types

```python
# Add zone_type classification to zones table
from pyspark.sql.functions import col, when, lit

df_zones = spark.table("zones")

df_zones = df_zones.withColumn("zone_type",
    when(col("location_id").isin(1, 132, 138), "Airport")
    .when(col("zone_name").isin(
        "Midtown Center", "Midtown East", "Midtown North", "Midtown South",
        "Financial District North", "Financial District South",
        "Flatiron", "Gramercy"
    ), "Business District")
    .when(col("zone_name").isin(
        "Times Sq/Theatre District", "Central Park", "SoHo",
        "Greenwich Village North", "Greenwich Village South",
        "West Village", "Chinatown"
    ), "Tourist Zone")
    .when(col("zone_name").isin(
        "Penn Station/Madison Sq West", "East Harlem North",
        "East Harlem South"
    ), "Transit Hub")
    .when(col("zone_name").isin(
        "East Village", "West Village", "Meatpacking/West Village Wst",
        "Lower East Side"
    ), "Entertainment District")
    .when(col("borough") == "Manhattan", "Manhattan Other")
    .otherwise("Residential")
)

# Add business context descriptions per borough
df_zones = df_zones.withColumn("borough_context",
    when(col("borough") == "Manhattan",
         "Dominates taxi activity with ~90% of all trips. Business/tourist density, limited parking drives demand.")
    .when(col("borough") == "Brooklyn",
         "Primarily residential. Lower taxi usage, shorter trips, more local transportation alternatives.")
    .when(col("borough") == "Queens",
         "Contains JFK and LaGuardia airports. High airport trip volume with flat-rate fares.")
    .when(col("borough") == "Bronx",
         "Lower taxi activity. More residential, higher cash payment rate.")
    .when(col("borough") == "Staten Island",
         "Lowest taxi activity due to limited yellow cab service.")
    .when(col("borough") == "EWR",
         "Newark Airport zone. Rate code 3 applies for metered fare plus surcharge.")
    .otherwise("Other area")
)

df_zones.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("zones")
print("Zones enriched with zone_type and borough_context")
df_zones.select("location_id", "zone_name", "borough", "zone_type", "borough_context").show(10, truncate=False)
```

### 6.1.2: Enrich the Payment Types Table with Business Rules

```python
# Add critical business rules to payment_types

from pyspark.sql.functions import col, when

df_payment = spark.table("payment_types")

df_payment = df_payment.withColumn("business_rule",
    when(col("payment_type_id") == 1,
         "Tips ARE recorded. ~70% of all trips. Use for tip analysis.")
    .when(col("payment_type_id") == 2,
         "CRITICAL: Tips are NOT recorded in data. Cash tips given directly to driver. ALWAYS exclude from tip analysis.")
    .when(col("payment_type_id") == 3,
         "No charge trips - promotional or courtesy rides. Exclude from revenue analysis.")
    .when(col("payment_type_id") == 4,
         "Disputed trips - may have incomplete or adjusted fare data.")
    .when(col("payment_type_id") == 5,
         "Unknown payment method - data quality issue.")
    .when(col("payment_type_id") == 6,
         "Voided trip - should be excluded from all analysis.")
    .otherwise("No rule defined")
)

df_payment = df_payment.withColumn("tip_data_available",
    when(col("payment_type_id") == 1, "Yes")
    .otherwise("No")
)

df_payment.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("payment_types")
print("Payment types enriched with business rules")
df_payment.show(truncate=False)
```

### 6.1.3: Enrich the Rate Codes Table

```python
# Add business context to rate codes

from pyspark.sql.functions import col, when

df_rates = spark.table("rate_codes")

df_rates = df_rates.withColumn("business_context",
    when(col("rate_code_id") == 1,
         "Metered fare based on time and distance. Standard for most NYC trips.")
    .when(col("rate_code_id") == 2,
         "Fixed $52 fare to/from JFK Airport to Manhattan. Predictable revenue. Higher tips expected.")
    .when(col("rate_code_id") == 3,
         "Metered fare plus surcharge to Newark Airport. Longer distance, higher total fares.")
    .when(col("rate_code_id") == 4,
         "Negotiated fare to Nassau or Westchester counties. Outside normal service area.")
    .when(col("rate_code_id") == 5,
         "Driver and passenger agreed on a fare. No meter used.")
    .when(col("rate_code_id") == 6,
         "Shared ride with other passengers. Lower per-person fare.")
    .otherwise("Unknown rate type")
)

df_rates = df_rates.withColumn("is_airport_rate",
    when(col("rate_code_id").isin(2, 3), "Yes").otherwise("No")
)

df_rates.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("rate_codes")
print("Rate codes enriched with business context")
df_rates.show(truncate=False)
```

---

### 6.1.4: Add Trip-Level Semantic Classifications

These columns turn raw trips into business concepts that we can model as entity types.

```python
from pyspark.sql.functions import col, when, hour, dayofweek, monotonically_increasing_id

df_trips = spark.table("trips")

# Ensure trip_id exists (needed as ontology key)
if "trip_id" not in df_trips.columns:
    df_trips = df_trips.withColumn("trip_id", monotonically_increasing_id())

# Trip type classification (single label per trip)
df_trips = df_trips.withColumn("trip_type",
    when(col("rate_code_id").isin(2, 3), "Airport")
    .when(col("trip_distance") > 10, "Long Distance")
    .when(col("trip_distance") < 2, "Short")
    .when(((hour(col("pickup_datetime")).between(7, 9)) |
           (hour(col("pickup_datetime")).between(17, 19))) &
          dayofweek(col("pickup_datetime")).between(2, 6), "Commute")
    .when((hour(col("pickup_datetime")) >= 22) |
          (hour(col("pickup_datetime")) < 5), "Night")
    .when(dayofweek(col("pickup_datetime")).isin(1, 7), "Weekend")
    .otherwise("Standard")
)

# Time context (broader temporal bucket)
df_trips = df_trips.withColumn("time_context",
    when(((hour(col("pickup_datetime")).between(7, 9)) |
           (hour(col("pickup_datetime")).between(17, 20))) &
          dayofweek(col("pickup_datetime")).between(2, 6), "Rush Hour")
    .when((hour(col("pickup_datetime")) >= 22) |
          (hour(col("pickup_datetime")) < 5), "Night Time")
    .when(dayofweek(col("pickup_datetime")).isin(1, 7), "Weekend")
    .otherwise("Off-Peak")
)

df_trips.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("trips")
print("Trips enriched with trip_type and time_context")
df_trips.select("trip_id", "trip_type", "time_context").show(10, truncate=False)
```

### 6.1.5: Create Semantic Dimension Tables

These tables become first-class entities in the ontology. They are the "business vocabulary"
that sits above the raw tables.

```python
# Borough dimension (derived from zones)
df_borough = spark.table("zones") \
    .select(col("borough").alias("borough_name"), "borough_context") \
    .dropna(subset=["borough_name"]) \
    .distinct()

df_borough.write.format("delta").mode("overwrite").saveAsTable("dim_borough")
print(f"Created dim_borough: {df_borough.count()} rows")

# Zone type dimension (static definitions)
zone_type_data = [
    ("Airport", "Airport pickup/dropoff zones (JFK, LaGuardia, Newark)"),
    ("Business District", "Dense office districts with high weekday demand"),
    ("Tourist Zone", "Visitor-heavy areas with consistent demand"),
    ("Transit Hub", "Major transit hubs and stations"),
    ("Entertainment District", "Nightlife and dining areas"),
    ("Residential", "Primarily residential neighborhoods")
]

df_zone_type = spark.createDataFrame(zone_type_data, ["zone_type", "definition"])
df_zone_type.write.format("delta").mode("overwrite").saveAsTable("dim_zone_type")
print(f"Created dim_zone_type: {df_zone_type.count()} rows")

# Trip type dimension (classification vocabulary)
trip_type_data = [
    ("Airport", "Rate code 2 or 3; airport-related trips"),
    ("Long Distance", "Trips over 10 miles"),
    ("Short", "Trips under 2 miles"),
    ("Commute", "Weekday rush hours (7-9 AM, 5-7 PM)"),
    ("Night", "Late night pickups (10 PM - 5 AM)"),
    ("Weekend", "Saturday/Sunday trips"),
    ("Standard", "All other trips")
]

df_trip_type = spark.createDataFrame(trip_type_data, ["trip_type", "definition"])
df_trip_type.write.format("delta").mode("overwrite").saveAsTable("dim_trip_type")
print(f"Created dim_trip_type: {df_trip_type.count()} rows")

# Time context dimension (broader temporal buckets)
time_context_data = [
    ("Rush Hour", "Weekday rush hours (7-9 AM, 5-8 PM)"),
    ("Night Time", "Late night (10 PM - 5 AM)"),
    ("Weekend", "Saturday/Sunday"),
    ("Off-Peak", "All other times")
]

df_time_context = spark.createDataFrame(time_context_data, ["time_context", "definition"])
df_time_context.write.format("delta").mode("overwrite").saveAsTable("dim_time_context")
print(f"Created dim_time_context: {df_time_context.count()} rows")
```

---

## Step 6.2: Update Ontology Bindings

After enriching the tables, we need to update the ontology to include the new properties.

### 6.2.1: Update Zone Entity Type

1. Open `NYCTaxiOntology` in Fabric
2. Select the `Zone` entity type
3. Go to **Bindings** tab
4. The new columns (`zone_type`, `borough_context`) should appear
5. If not, remove and re-add the data binding for the `zones` table
6. Verify these new properties appear:

| New Property | Type | Purpose |
|---|---|---|
| `zone_type` | String | Zone classification (Airport, Business, Tourist, etc.) |
| `borough_context` | String | Business explanation for the borough |

### 6.2.2: Update PaymentType Entity Type

1. Select `PaymentType` entity type
2. Update binding with `payment_types` table
3. Verify new properties:

| New Property | Type | Purpose |
|---|---|---|
| `business_rule` | String | Critical business rule for this payment type |
| `tip_data_available` | String | Whether tip data is recorded (Yes/No) |

### 6.2.3: Update RateCode Entity Type

1. Select `RateCode` entity type
2. Update binding with `rate_codes` table
3. Verify new properties:

| New Property | Type | Purpose |
|---|---|---|
| `business_context` | String | Business meaning of this rate type |
| `is_airport_rate` | String | Whether this is an airport rate (Yes/No) |

---

### 6.2.4: Add Semantic Entity Types (New)

Create new entity types backed by the dimension tables. These are the concepts
that provide value beyond raw table filtering.

| Entity Type | Source Table | Key | Display Name |
|---|---|---|---|
| `Borough` | `dim_borough` | `borough_name` | `borough_name` |
| `ZoneType` | `dim_zone_type` | `zone_type` | `zone_type` |
| `TripType` | `dim_trip_type` | `trip_type` | `trip_type` |
| `TimeContext` | `dim_time_context` | `time_context` | `time_context` |

### 6.2.5: Add Relationships to Semantic Entities

Create these relationships to enable graph traversal:

| Relationship | Source → Target | Join Logic |
|---|---|---|
| `inBorough` | Zone → Borough | `zones.borough = dim_borough.borough_name` |
| `hasZoneType` | Zone → ZoneType | `zones.zone_type = dim_zone_type.zone_type` |
| `hasTripType` | Trip → TripType | `trips.trip_type = dim_trip_type.trip_type` |
| `occursIn` | Trip → TimeContext | `trips.time_context = dim_time_context.time_context` |

---

### 6.2.6: (Optional) Add BusinessRule Entity and Relationships

If you create the `business_rules` table (Step 6.3), add a `BusinessRule` entity type:

| Entity Type | Source Table | Key | Display Name |
|---|---|---|---|
| `BusinessRule` | `business_rules` | `rule_name` | `rule_name` |

Then add these relationships:

| Relationship | Source → Target | Join Logic |
|---|---|---|
| `appliesToPaymentType` | BusinessRule → PaymentType | `business_rules.payment_type_id = payment_types.payment_type_id` |
| `appliesToRateCode` | BusinessRule → RateCode | `business_rules.rate_code_id = rate_codes.rate_code_id` |

---

## Step 6.3: Create a Business Rules Reference Table (Optional)

For encoding inference rules that span multiple entities, create a dedicated table.
We also add optional `payment_type_id` and `rate_code_id` columns so rules can
link directly to entity instances in the graph.

```python
# Create business rules table
# These are the rules that an AI agent needs to reason correctly

business_rules_data = [
    ("CashTipDataGap",
     "tip_analysis",
     "payment_type = 2",
     "Tip amount is unknown (recorded as $0). Cash tips given directly to driver.",
     "ALWAYS exclude cash payments (payment_type = 2) from tip analysis.",
     2, None),

    ("ManhattanDominance",
     "revenue_analysis",
     "borough = Manhattan",
     "Manhattan generates ~90% of yellow taxi trips and revenue.",
     "Manhattan will dominate any volume or revenue metric due to business concentration, tourism, and limited parking.",
     None, None),

    ("LowTipInterpretation",
     "tip_analysis",
     "avg_tip < 2.50 AND borough != Manhattan",
     "Low recorded tips in outer boroughs reflect demographics, NOT service quality.",
     "Higher cash usage means tips are invisible. Local residents tip differently than tourists.",
     None, None),

    ("JFKFlatRate",
     "airport_analysis",
     "rate_code_id = 2",
     "JFK Airport has a fixed $52 fare to Manhattan.",
     "Flat rate means predictable revenue. Tips tend to be higher on airport trips.",
     None, 2),

    ("TipAnalysisRule",
     "tip_analysis",
     "payment_type = 1",
     "Only credit card payments have recorded tips.",
     "When analyzing tips, ALWAYS filter to credit card payments. Cash tips exist but aren't recorded.",
     1, None),

    ("PeakHoursRule",
     "demand_analysis",
     "hour IN (7,8,9,17,18,19,20) AND weekday",
     "Peak demand occurs 7-9 AM and 5-8 PM on weekdays.",
     "Commuter patterns drive demand. Expect longer trip durations due to traffic.",
     None, None),

    ("ZonePerformanceRule",
     "zone_analysis",
     "zone_type varies",
     "Zone performance varies by zone type.",
     "Business districts: high volume weekdays. Airport zones: high per-trip revenue. Tourist zones: consistent across week.",
     None, None),

    ("RevenueCalculation",
     "revenue_analysis",
     "fare_amount + tip_amount",
     "Trip revenue = fare + tip. Total amount includes additional fees.",
     "Revenue metric excludes tolls, surcharges. Total_amount is the full passenger charge.",
     None, None),

    ("WeekendPatterns",
     "demand_analysis",
     "dayofweek IN (Saturday, Sunday)",
     "Weekend trips are tourism and leisure focused.",
     "Different geographic patterns than weekdays. Entertainment districts peak on weekends.",
     None, None),

    ("CongestionSurcharge",
     "pricing_analysis",
     "congestion_surcharge > 0",
     "NYC congestion pricing adds surcharge in certain zones.",
     "Congestion surcharge is separate from fare and varies by zone and time.",
     None, None)
]

df_rules = spark.createDataFrame(
    business_rules_data,
    ["rule_name", "analysis_category", "condition", "description", "guidance", "payment_type_id", "rate_code_id"]
)

df_rules.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("business_rules")
print(f"Created business_rules: {df_rules.count()} rules")
df_rules.show(truncate=False)
```

---

## Step 6.4: Verify the Enriched Data

```python
# Verify all enrichments are in place

print("=" * 60)
print("ENRICHMENT VERIFICATION")
print("=" * 60)

print("\n--- Zone Types Distribution ---")
spark.sql("""
    SELECT zone_type, COUNT(*) as zone_count
    FROM zones
    GROUP BY zone_type
    ORDER BY zone_count DESC
""").show()

print("\n--- Payment Type Business Rules ---")
spark.sql("""
    SELECT description, business_rule, tip_data_available
    FROM payment_types
    ORDER BY payment_type_id
""").show(truncate=False)

print("\n--- Rate Code Context ---")
spark.sql("""
    SELECT description, is_airport_rate, business_context
    FROM rate_codes
    ORDER BY rate_code_id
""").show(truncate=False)

print("\n--- Business Rules Summary ---")
spark.sql("""
    SELECT rule_name, analysis_category, description, payment_type_id, rate_code_id
    FROM business_rules
    ORDER BY analysis_category, rule_name
""").show(truncate=False)

print("\n--- Trip Type Distribution ---")
spark.sql("""
    SELECT trip_type, COUNT(*) as trip_count
    FROM trips
    GROUP BY trip_type
    ORDER BY trip_count DESC
""").show()

print("\n--- Time Context Distribution ---")
spark.sql("""
    SELECT time_context, COUNT(*) as trip_count
    FROM trips
    GROUP BY time_context
    ORDER BY trip_count DESC
""").show()
```

---

## What We've Achieved

Our ontology now contains not just structure, but **meaning**:

| Before Enrichment                | After Enrichment                                                             |
|---                               |---                                                                           |
| Zone has `borough = "Manhattan"` | Zone has `borough_context = "Dominates taxi activity with ~90% of trips..."` |
| Zone has `location_id = 132`     | Zone has `zone_type = "Airport"`                                             |
| Payment type `2` = "Cash"        | Payment type `2` has `business_rule = "CRITICAL: Tips NOT recorded..."`      |
| Rate code `2` = "JFK"            | Rate code `2` has `business_context = "Fixed $52 fare..."`                   |
| No inference rules               | 10 business rules encoded in `business_rules` table                          |

### Where the Enrichment Lives

```
Borough context          →  zones.borough_context column
Zone type                →  zones.zone_type column
Payment rule context     →  payment_types.business_rule column
Business rules           →  business_rules table rows
Airport rate flag        →  rate_codes.is_airport_rate = "Yes"
Trip type                →  trips.trip_type column
Time context             →  trips.time_context column
Semantic dimensions      →  dim_borough, dim_zone_type, dim_trip_type, dim_time_context tables
Rule links               →  business_rules.payment_type_id, business_rules.rate_code_id
```

---

**Next: [Step 07 — Preview and Query the Ontology →](07_preview_and_query.md)**
