# Step 02b: Technical Layer — Using the Fabric UI

**Duration: 20 minutes | Type: Hands-on (Fabric UI)**

---

## Overview

Step 02 (`02_technical_layer.py`) creates the technical layer programmatically using Spark SQL. This companion guide shows you how to do the same thing **manually through the Fabric UI** — adding table descriptions, column descriptions, and exploring metadata without writing code.

### What Is the Technical Layer?

The technical layer answers: **"What data do we have?"** It documents tables, columns, types, relationships, and business descriptions.

| What You Do | Programmatic (Step 02) | UI Method (This Step) |
|---|---|---|
| View table schemas | `DESCRIBE TABLE` | Lakehouse explorer → click table |
| Add table descriptions | `ALTER TABLE SET TBLPROPERTIES` | SQL endpoint → table properties |
| Add column descriptions | Spark SQL comments | SQL endpoint → column editing |
| Explore data | `spark.sql("SELECT ...")` | Lakehouse preview / SQL query |
| View relationships | Print join diagram | Visual query designer |

---

## Part 1: Explore Tables in the Lakehouse UI

### 1.1: Open the Lakehouse

1. Go to your workspace in **https://app.fabric.microsoft.com**
2. Click on **NYCTaxiLakehouse** to open it
3. You'll see the Lakehouse explorer with your tables

### 1.2: Preview Table Data

1. In the left **Explorer** panel, expand the **Tables** folder
2. Click on **trips** — the center panel shows:
   - **Table preview**: First rows of data in a spreadsheet-like view
   - **Column names**: Shown as column headers
   - You can scroll right to see all 19 columns

3. Click on **zones** to preview it:
   - You should see: `location_id`, `borough`, `zone_name`, `service_zone`
   - 265 rows of zone data

4. Click on **payment_types** to preview:
   - You should see: `payment_type_id`, `description`
   - 6 rows: Credit card, Cash, No charge, Dispute, Unknown, Voided trip

5. Click on **rate_codes** to preview:
   - You should see: `rate_code_id`, `description`
   - 6 rows: Standard rate, JFK, Newark, etc.

### 1.3: View Column Details

For any table:

1. Click the table name in the explorer
2. In the center panel, look for a **Schema** or **Columns** view
   - Some views show column name, data type, and nullable status
3. If you hover over a column header in the preview, you may see the data type

**Expected column types for trips:**

| Column | Type |
|---|---|
| vendor_id | INTEGER / LONG |
| pickup_datetime | TIMESTAMP |
| dropoff_datetime | TIMESTAMP |
| passenger_count | DOUBLE / INTEGER |
| trip_distance | DOUBLE |
| pickup_location_id | INTEGER / LONG |
| dropoff_location_id | INTEGER / LONG |
| rate_code_id | DOUBLE / INTEGER |
| payment_type | INTEGER / LONG |
| fare_amount | DOUBLE |
| tip_amount | DOUBLE |
| total_amount | DOUBLE |

---

## Part 2: Add Table and Column Descriptions via SQL Endpoint

### 2.1: Open the SQL Analytics Endpoint

1. In the Lakehouse view, look at the **top right** area for a view toggle/selector
2. Click on **SQL analytics endpoint** (it may show as a dropdown or icon)
   - Alternatively: In the workspace view, you'll see a separate item called `NYCTaxiLakehouse` with a SQL endpoint icon — click that
3. You're now in the SQL query interface

The SQL endpoint UI has:
- **Explorer panel** (left): Shows schemas, tables, columns
- **Query editor** (center): Write and run SQL queries
- **Results panel** (bottom): Shows query output
- **Ribbon** (top): New SQL query, Run, Save buttons

### 2.2: Add Table Descriptions

In the SQL query editor, create a **New SQL query** (click the button in the ribbon), then paste and run each statement:

```sql
-- Add description to trips table
COMMENT ON TABLE trips IS
'NYC Yellow Taxi trip records for January 2024. Each row is a completed trip from pickup to dropoff. Contains fare, tip, distance, and location data for approximately 2.76 million trips.';
```

Click **▶ Run**. Then run:

```sql
-- Add description to zones table
COMMENT ON TABLE zones IS
'TLC taxi zone lookup table. Maps 265 location IDs to zone names, boroughs, and service zones across the 5 NYC boroughs plus EWR (Newark Airport).';
```

```sql
-- Add description to payment_types table
COMMENT ON TABLE payment_types IS
'Payment type reference table. Maps numeric codes to payment descriptions. CRITICAL: Cash payments (type 2) do not record tip amounts.';
```

```sql
-- Add description to rate_codes table
COMMENT ON TABLE rate_codes IS
'Rate code reference table. Maps numeric codes to fare calculation methods. Airport flat rates (JFK=2, Newark=3) have special pricing rules.';
```

> **Note**: If `COMMENT ON TABLE` doesn't work in your endpoint, use the alternative syntax from Step 02:
> ```sql
> ALTER TABLE trips SET TBLPROPERTIES ('comment' = 'Your description here');
> ```

### 2.3: Add Column Descriptions

Add meaningful descriptions to the most important columns:

```sql
-- Trip table column descriptions
ALTER TABLE trips ALTER COLUMN vendor_id COMMENT 'Taxi technology vendor: 1=Creative Mobile Technologies (CMT), 2=VeriFone Inc (VTS)';
ALTER TABLE trips ALTER COLUMN pickup_datetime COMMENT 'Date and time when the meter was engaged at pickup';
ALTER TABLE trips ALTER COLUMN dropoff_datetime COMMENT 'Date and time when the meter was disengaged at dropoff';
ALTER TABLE trips ALTER COLUMN passenger_count COMMENT 'Number of passengers in the vehicle (driver-reported)';
ALTER TABLE trips ALTER COLUMN trip_distance COMMENT 'Trip distance in miles as reported by the taximeter';
ALTER TABLE trips ALTER COLUMN pickup_location_id COMMENT 'TLC Taxi Zone ID where the trip started. FK to zones.location_id';
ALTER TABLE trips ALTER COLUMN dropoff_location_id COMMENT 'TLC Taxi Zone ID where the trip ended. FK to zones.location_id';
ALTER TABLE trips ALTER COLUMN rate_code_id COMMENT 'Rate code: 1=Standard, 2=JFK flat rate ($52), 3=Newark, 4=Nassau/Westchester, 5=Negotiated, 6=Group ride';
ALTER TABLE trips ALTER COLUMN payment_type COMMENT 'Payment method: 1=Credit card (tips recorded), 2=Cash (tips NOT recorded), 3=No charge, 4=Dispute, 5=Unknown, 6=Voided';
ALTER TABLE trips ALTER COLUMN fare_amount COMMENT 'Base fare calculated by the meter (USD)';
ALTER TABLE trips ALTER COLUMN tip_amount COMMENT 'Tip amount (USD). IMPORTANT: Only recorded for credit card payments. Cash tips are NOT captured.';
ALTER TABLE trips ALTER COLUMN tolls_amount COMMENT 'Total toll charges for the trip (USD)';
ALTER TABLE trips ALTER COLUMN total_amount COMMENT 'Total amount charged to passenger including fare, tips, tolls, surcharges, and fees (USD)';
ALTER TABLE trips ALTER COLUMN congestion_surcharge COMMENT 'NYC congestion surcharge applied to trips in certain Manhattan zones';
ALTER TABLE trips ALTER COLUMN airport_fee COMMENT 'Airport pickup fee for trips originating at airports';
```

### 2.4: Verify Descriptions

Run this query to see your descriptions:

```sql
-- View column descriptions for trips
DESCRIBE TABLE EXTENDED trips;
```

Or for a cleaner view:

```sql
SELECT
    column_name,
    data_type,
    comment
FROM information_schema.columns
WHERE table_name = 'trips'
ORDER BY ordinal_position;
```

---

## Part 3: Explore Relationships in the UI

### 3.1: View Table Relationships Using SQL Queries

Run these queries to understand how tables connect:

```sql
-- Verify the pickup zone join
SELECT
    t.pickup_location_id,
    z.zone_name,
    z.borough,
    COUNT(*) as trip_count
FROM trips t
JOIN zones z ON t.pickup_location_id = z.location_id
GROUP BY t.pickup_location_id, z.zone_name, z.borough
ORDER BY trip_count DESC
LIMIT 10;
```

```sql
-- Verify the payment type join
SELECT
    p.description as payment_type,
    COUNT(*) as trip_count,
    ROUND(AVG(t.tip_amount), 2) as avg_tip
FROM trips t
JOIN payment_types p ON t.payment_type = p.payment_type_id
GROUP BY p.description
ORDER BY trip_count DESC;
```

### 3.2: Use the Visual Query Designer (Optional)

1. In the SQL endpoint, look for a **Visual Query** or **Diagram** view option
2. If available, you can drag tables onto a canvas and see relationships visually
3. This varies by Fabric version — not always available

### 3.3: Document Relationships Manually

Even without a visual tool, you now understand the star schema:

```
                    ┌──────────────┐
                    │ payment_types│
                    │              │
                    │payment_type  │◄──┐
                    │_id           │   │
                    └──────────────┘   │ trips.payment_type
                                      │
┌──────────────┐    ┌──────────────┐  │    ┌──────────────┐
│  rate_codes  │    │    trips     │  │    │    zones     │
│              │    │              ├──┘    │              │
│ rate_code_id │◄───┤              │      │ location_id  │
│              │    │ pickup_      ├─────►│ borough      │
└──────────────┘    │ location_id  │      │ zone_name    │
  trips.rate_code_id│              │      └──────────────┘
                    │ dropoff_     ├─────►│    zones     │
                    │ location_id  │      │ (same table) │
                    └──────────────┘      └──────────────┘
```

---

## Part 4: Data Profiling in the UI

### 4.1: Run Profile Queries

In the SQL endpoint, run these profiling queries:

```sql
-- Table row counts
SELECT 'trips' as tbl, COUNT(*) as rows FROM trips
UNION ALL SELECT 'zones', COUNT(*) FROM zones
UNION ALL SELECT 'payment_types', COUNT(*) FROM payment_types
UNION ALL SELECT 'rate_codes', COUNT(*) FROM rate_codes;
```

```sql
-- Borough distribution (shows Manhattan dominance)
SELECT
    z.borough,
    COUNT(*) as trip_count,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips) AS DECIMAL(5,1)) as pct
FROM trips t
JOIN zones z ON t.pickup_location_id = z.location_id
GROUP BY z.borough
ORDER BY trip_count DESC;
```

```sql
-- Data quality check: any nulls in key columns?
SELECT
    COUNT(*) as total_rows,
    SUM(CASE WHEN pickup_location_id IS NULL THEN 1 ELSE 0 END) as null_pickup,
    SUM(CASE WHEN dropoff_location_id IS NULL THEN 1 ELSE 0 END) as null_dropoff,
    SUM(CASE WHEN payment_type IS NULL THEN 1 ELSE 0 END) as null_payment,
    SUM(CASE WHEN fare_amount IS NULL THEN 1 ELSE 0 END) as null_fare
FROM trips;
```

### 4.2: Pin Important Queries

In the SQL endpoint, you can save queries for reuse:

1. After writing a query, click **Save** or **Save as** in the ribbon
2. Give it a descriptive name like `"Data Profile - Borough Distribution"`
3. Saved queries appear in the workspace for future reference

---

## Part 5: Using Microsoft Purview for Metadata (Advanced, Optional)

If your organization uses **Microsoft Purview**, you can add richer metadata:

### 5.1: Access Purview from Fabric

1. In Fabric, go to your workspace **Settings** (gear icon)
2. Look for **Microsoft Purview** integration options
3. If enabled, you can:
   - Add business glossary terms
   - Tag tables and columns with classifications
   - Set data owners and stewards
   - View data lineage automatically

### 5.2: Add Glossary Terms (If Purview Is Available)

| Glossary Term | Definition | Maps to |
|---|---|---|
| Trip Revenue | `fare_amount + tip_amount` for a completed trip | trips.fare_amount + trips.tip_amount |
| Trip Count | Number of completed taxi trips | COUNT(*) on trips |
| Average Tip | Mean tip per trip (credit card only!) | AVG(trips.tip_amount) WHERE payment_type=1 |
| Borough | NYC administrative district | zones.borough |
| Pickup Zone | TLC zone where the trip started | zones.zone_name via trips.pickup_location_id |
| Cash Payment | Cash payment — tips NOT recorded | payment_types WHERE payment_type_id=2 |
| Airport Trip | Trip to/from JFK, LaGuardia, or Newark | trips WHERE rate_code_id IN (2,3) |
| Peak Hours | Weekday 7-9 AM and 5-8 PM | Time-based filter on trips.pickup_datetime |

> **Note**: If Purview isn't available, the column descriptions we added in Part 2 serve the same documentation purpose.

---

## Summary: What the Technical Layer Provides

After completing this step (either via code or UI), you have:

| Asset | Status |
|---|---|
| 4 Delta tables | Documented with descriptions |
| 19 columns in trips | Each with type and business description |
| Star schema relationships | Documented and verified |
| Data profiling | Row counts, distributions, null checks |
| Saved SQL queries | Reusable profile and verification queries |

The technical layer tells us **WHAT** exists. Next, we build the semantic layer to define **HOW** to compute metrics.

---

**Next: [Step 03 — Semantic Layer (Spark SQL) →](03_semantic_layer_spark.py) or [Step 03b — Semantic Model (Power BI DAX, UI) →](03b_semantic_model_powerbi_dax.md)**
