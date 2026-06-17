# Step 05: Create the Fabric Ontology

**Duration: 25 minutes | Type: Hands-on (Fabric UI)**

---

## What We're Building

We will create a Fabric Ontology item that models the NYC Taxi domain with entity types, properties, keys, data bindings, and relationships using Fabric's native ontology feature.

### Entity Types We'll Create (Core)

| Entity Type | Source Table | Key |
|---|---|---|
| `Trip` | `trips` | (auto-generated row ID) |
| `Zone` | `zones` | `location_id` |
| `PaymentType` | `payment_types` | `payment_type_id` |
| `RateCode` | `rate_codes` | `rate_code_id` |

> **Note**: In Step 06 we will add **semantic entities** (Borough, ZoneType, TripType, TimeContext)
> backed by dimension tables. Those add real value beyond table filtering by enabling
> multi-hop graph traversal and stable business vocabulary.

### Relationships We'll Create

| Relationship | Source → Target | Join Logic |
|---|---|---|
| `hasPickupZone` | Trip → Zone | `trips.pickup_location_id = zones.location_id` |
| `hasDropoffZone` | Trip → Zone | `trips.dropoff_location_id = zones.location_id` |
| `paidWith` | Trip → PaymentType | `trips.payment_type = payment_types.payment_type_id` |
| `usesRate` | Trip → RateCode | `trips.rate_code_id = rate_codes.rate_code_id` |

---

## Prerequisites

Before starting, ensure these **Tenant Settings** are enabled by your Fabric Administrator:

- ✅ Enable Ontology item (preview)
- ✅ User can create Graph (preview)
- ✅ Users can create and share Data agent item types (preview)
- ✅ Users can use Copilot and other features powered by Azure OpenAI
- ✅ Data sent to Azure OpenAI can be processed outside your capacity's geographic region

---

## Step 5.1: Create the Ontology Item

1. Navigate to your **Fabric workspace** (the one containing `NYCTaxiLakehouse`)
2. Click **+ New item**
3. Search for **Ontology (preview)** and select it
4. Name it: `NYCTaxiOntology`

> **Naming rule**: Only numbers, letters, and underscores. No spaces or dashes.

5. Click **Create**

You should now see an empty ontology canvas.

---

## Step 5.2: Create the Zone Entity Type

We start with Zone because it's the simplest and most foundational.

### 5.2.1: Add the Entity Type

1. Click **+ Add entity type** (from the ribbon or the center canvas)
2. Name: `Zone`

### 5.2.2: Bind Data

1. Go to the **Bindings** tab
2. Click **Add data to entity type**
3. Select your Lakehouse: `NYCTaxiLakehouse`
4. Select table: `zones`
5. Binding type: **Static** (default)
6. Properties will auto-populate from column names:

| Property | Type | Maps to Column |
|---|---|---|
| `location_id` | Integer | zones.location_id |
| `borough` | String | zones.borough |
| `zone_name` | String | zones.zone_name |
| `service_zone` | String | zones.service_zone |

### 5.2.3: Set the Entity Key

1. In the Entity type configuration pane, click **Set key**
2. Select `location_id` as the entity type key
3. This uniquely identifies each of the 265 taxi zones

### 5.2.4: Set Display Name

1. Set the **Instance display name** to `zone_name`
2. This makes zones show up as "Midtown Center" instead of "161" in the UI

---

## Step 5.3: Create the PaymentType Entity Type

### 5.3.1: Add the Entity Type

1. Click **+ Add entity type**
2. Name: `PaymentType`

### 5.3.2: Bind Data

1. Bindings tab → **Add data to entity type**
2. Select `NYCTaxiLakehouse` → `payment_types` table
3. Binding type: **Static**
4. Properties auto-populate:

| Property | Type | Maps to Column |
|---|---|---|
| `payment_type_id` | Integer | payment_types.payment_type_id |
| `description` | String | payment_types.description |

### 5.3.3: Set the Entity Key

1. Set `payment_type_id` as the entity type key

### 5.3.4: Set Display Name

1. Set instance display name to `description`
2. Entities will show as "Credit card", "Cash", etc.

---

## Step 5.4: Create the RateCode Entity Type

### 5.4.1: Add the Entity Type

1. Click **+ Add entity type**
2. Name: `RateCode`

### 5.4.2: Bind Data

1. Bindings tab → **Add data to entity type**
2. Select `NYCTaxiLakehouse` → `rate_codes` table
3. Binding type: **Static**
4. Properties auto-populate:

| Property | Type | Maps to Column |
|---|---|---|
| `rate_code_id` | Integer | rate_codes.rate_code_id |
| `description` | String | rate_codes.description |

### 5.4.3: Set the Entity Key

1. Set `rate_code_id` as the entity type key

### 5.4.4: Set Display Name

1. Set instance display name to `description`

---

## Step 5.5: Create the Trip Entity Type

The Trip entity is the central fact table — it's the largest and most important entity.

### 5.5.1: Add the Entity Type

1. Click **+ Add entity type**
2. Name: `Trip`

### 5.5.2: Bind Data

1. Bindings tab → **Add data to entity type**
2. Select `NYCTaxiLakehouse` → `trips` table
3. Binding type: **Static**
4. Properties auto-populate from all 19 columns:

**Key properties to verify are present:**

| Property              | Type       | Business Meaning                   |
|---                    |---         |---                                 |
| `vendor_id`           | Integer    | Taxi vendor (1=CMT, 2=VeriFone)    |
| `pickup_datetime`     | Timestamp  | When the meter was engaged         |
| `dropoff_datetime`    | Timestamp  | When the meter was disengaged      |
| `passenger_count`     | Integer    | Number of passengers               |
| `trip_distance`       | Double     | Distance in miles                  |
| `pickup_location_id`  | Integer    | FK to zones.location_id            |
| `dropoff_location_id` | Integer    | FK to zones.location_id            |
| `rate_code_id`        | Integer    | FK to rate_codes.rate_code_id      |
| `payment_type`        | Integer    | FK to payment_types.payment_type_id|
| `fare_amount`         | Double     | Base fare (USD)                    |
| `tip_amount`          | Double     | Tip (USD, credit card only!)       |
| `total_amount`        | Double     | Total charge (USD)                 |
| `congestion_surcharge`| Double     | NYC congestion surcharge           |
| `airport_fee`         | Double     | Airport pickup fee                 |

### 5.5.3: Set the Entity Key

Since `trips` doesn't have a single unique ID column, you have two options:

**Option A**: Use a composite key if your data has unique combinations
- This depends on your specific data — pickup_datetime + vendor_id might work

**Option B** (Recommended): Add a row ID to the trips table first. Run this in a Fabric notebook:

```python
from pyspark.sql.functions import monotonically_increasing_id

df = spark.table("trips")
df = df.withColumn("trip_id", monotonically_increasing_id())
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("trips")
```

Then set `trip_id` as the entity key.

> **Note**: If setting a key is difficult for the large trips table, you can skip this and focus on the dimension entities (Zone, PaymentType, RateCode) for the ontology relationships. The Data Agent can still query trips through the relationships.

---

## Step 5.6: Create Relationships

Now we connect our entities with meaningful relationships.

### 5.6.1: Relationship: Trip `hasPickupZone` Zone

1. Select the `Trip` entity type
2. Click **+ Add relationship type**
3. Configure:

| Field                   | Value                        |
|---                      |---                           |
| Relationship name       | `hasPickupZone`              |
| Source entity           | `Zone`                       |
| Target entity           | `Trip`                       |
| Source data             | `NYCTaxiLakehouse` → `trips` |
| Source column (Zone)    | `pickup_location_id`         |
| Target column (Trip)    | `trip_id` (or your key)      |

> **How it works**: The `trips` table serves as the bridge — each row has a `pickup_location_id` that references a Zone and a `trip_id` that identifies the Trip.

### 5.6.2: Relationship: Trip `hasDropoffZone` Zone

1. Click **+ Add relationship type**
2. Configure:

| Field | Value |
|---|---|
| Relationship name | `hasDropoffZone` |
| Source entity | `Zone` |
| Target entity | `Trip` |
| Source data | `NYCTaxiLakehouse` → `trips` |
| Source column (Zone) | `dropoff_location_id` |
| Target column (Trip) | `trip_id` |

### 5.6.3: Relationship: Trip `paidWith` PaymentType

1. Click **+ Add relationship type**
2. Configure:

| Field | Value |
|---|---|
| Relationship name | `paidWith` |
| Source entity | `PaymentType` |
| Target entity | `Trip` |
| Source data | `NYCTaxiLakehouse` → `trips` |
| Source column (PaymentType) | `payment_type` |
| Target column (Trip) | `trip_id` |

### 5.6.4: Relationship: Trip `usesRate` RateCode

1. Click **+ Add relationship type**
2. Configure:

| Field | Value |
|---|---|
| Relationship name | `usesRate` |
| Source entity | `RateCode` |
| Target entity | `Trip` |
| Source data | `NYCTaxiLakehouse` → `trips` |
| Source column (RateCode) | `rate_code_id` |
| Target column (Trip) | `trip_id` |

---

## Step 5.7: Verify Your Ontology

At this point, your ontology should show:

```
         Zone (265 instances)
          ▲  ▲
          │  │
 hasPickup│  │hasDropoff
    Zone  │  │Zone
          │  │
          Trip (~2.76M instances)
          │  │
  paidWith│  │usesRate
          │  │
          ▼  ▼
  PaymentType    RateCode
 (6 instances)  (6 instances)
```

### Checklist

- [ ] 4 entity types created: Trip, Zone, PaymentType, RateCode
- [ ] Each entity type has properties bound to Lakehouse tables
- [ ] Entity keys set for Zone, PaymentType, RateCode
- [ ] 4 relationships defined: hasPickupZone, hasDropoffZone, paidWith, usesRate
- [ ] Each relationship has proper data binding with source/target columns

---

## Design Notes and Limitations

Some types of business logic are better handled outside the ontology canvas:

1. **Business rules** are captured in Agent instructions (Step 08)
2. **Classification logic** is implemented with computed columns or Agent instructions
3. **Subtypes** such as AirportTrip are represented via rules, not entity subtypes

We will address these in Steps 06 and 08.

---

**Next: [Step 06 — Enrich the Ontology →](06_enrich_ontology.md)**
