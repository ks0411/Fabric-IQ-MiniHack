# Fabric Notebook — Step 02: Technical Layer
# =============================================================================
# The Technical Layer documents WHAT data exists.
# In Fabric, we use Lakehouse metadata + table/column descriptions.
#
# This step adds business descriptions to our tables and columns,
# making the data self-documenting.
# =============================================================================

# %% [markdown]
# # Step 02: Technical Layer — Documenting What Exists
#
# ## The Technical Layer in Context
#
# ```
# ┌──────────┐ ┌──────────┐ ┌───────────────┐
# │ SEMANTIC │ │ ONTOLOGY │ │  TECHNICAL    │  ◄── YOU ARE HERE
# │  LAYER   │ │  LAYER   │ │    LAYER      │
# │ COMPUTES │ │ EXPLAINS │ │  DOCUMENTS    │
# │ metrics  │ │ why      │ │  what exists  │
# └──────────┘ └──────────┘ └───────────────┘
# ```
#
# The technical layer answers: **"What data do we have?"**
#
# | Fabric capability | What it provides |
# |---|---|
# | Lakehouse metadata | Table discovery via `DESCRIBE` / `information_schema` |
# | Table/column comments | Business descriptions |
# | Lineage view | End-to-end visibility |

# %% Cell 1: Explore what we have — table discovery

print("=" * 60)
print("TABLE DISCOVERY — What's in our Lakehouse?")
print("=" * 60)

# List all tables
tables_df = spark.sql("SHOW TABLES")
tables_df.show()

# %% Cell 2: Inspect each table's schema

for table_name in ["trips", "zones", "payment_types", "rate_codes"]:
    print(f"\n{'=' * 60}")
    print(f"TABLE: {table_name}")
    print(f"{'=' * 60}")
    spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}").show(50, truncate=False)

# %% Cell 3: Add table comments — business descriptions

# These comments serve as the technical metadata layer in Fabric.

spark.sql("""
    ALTER TABLE trips
    SET TBLPROPERTIES (
        'comment' = 'NYC Yellow Taxi trip records for January 2024. Each row is a completed trip from pickup to dropoff. Contains fare, tip, distance, and location data for approximately 2.76 million trips.'
    )
""")

spark.sql("""
    ALTER TABLE zones
    SET TBLPROPERTIES (
        'comment' = 'TLC taxi zone lookup table. Maps 265 location IDs to zone names, boroughs, and service zones across the 5 NYC boroughs plus EWR (Newark Airport).'
    )
""")

spark.sql("""
    ALTER TABLE payment_types
    SET TBLPROPERTIES (
        'comment' = 'Payment type reference table. Maps numeric codes to payment descriptions. CRITICAL: Cash payments (type 2) do not record tip amounts.'
    )
""")

spark.sql("""
    ALTER TABLE rate_codes
    SET TBLPROPERTIES (
        'comment' = 'Rate code reference table. Maps numeric codes to fare calculation methods. Airport flat rates (JFK=2, Newark=3) have special pricing rules.'
    )
""")

print("Table descriptions added.")

# %% Cell 4: Verify table descriptions

for table_name in ["trips", "zones", "payment_types", "rate_codes"]:
    result = spark.sql(f"DESCRIBE TABLE EXTENDED {table_name}")
    comment_row = result.filter(result.col_name == "Comment")
    if comment_row.count() > 0:
        comment = comment_row.collect()[0]["data_type"]
        print(f"\n{table_name}: {comment[:80]}...")

# %% Cell 5: Data profiling — understand the data distribution

print("=" * 60)
print("DATA PROFILING")
print("=" * 60)

# Trip volume over time
print("\n--- Trip Volume by Day (first 10 days) ---")
spark.sql("""
    SELECT
        DATE(pickup_datetime) as trip_date,
        COUNT(*) as trip_count,
        ROUND(SUM(fare_amount + tip_amount), 0) as daily_revenue
    FROM trips
    GROUP BY DATE(pickup_datetime)
    ORDER BY trip_date
    LIMIT 10
""").show()

# Borough distribution
print("\n--- Trip Distribution by Borough ---")
spark.sql("""
    SELECT
        z.borough,
        COUNT(*) as trip_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trips), 1) as pct_of_total
    FROM trips t
    JOIN zones z ON t.pickup_location_id = z.location_id
    GROUP BY z.borough
    ORDER BY trip_count DESC
""").show()

# %% Cell 6: Relationship discovery — how tables connect

print("=" * 60)
print("RELATIONSHIP DISCOVERY")
print("=" * 60)

print("""
Our data has a star schema structure:

                    ┌──────────────┐
                    │ payment_types│
                    │ payment_type │◄──┐
                    │ _id          │   │
                    └──────────────┘   │
                                      │
┌──────────────┐    ┌──────────────┐  │    ┌──────────────┐
│  rate_codes  │    │    trips     │  │    │    zones     │
│  rate_code   │◄───┤              ├──┘    │  location_id │
│  _id         │    │ pickup_      ├──────►│  borough     │
└──────────────┘    │ location_id  │       │  zone_name   │
                    │              │       └──────────────┘
                    │ dropoff_     ├──────►│    zones     │
                    │ location_id  │       │ (same table) │
                    └──────────────┘       └──────────────┘

Foreign Key Relationships:
  trips.pickup_location_id  → zones.location_id
  trips.dropoff_location_id → zones.location_id
  trips.payment_type        → payment_types.payment_type_id
  trips.rate_code_id        → rate_codes.rate_code_id
""")

# Verify join integrity
print("\n--- Join Integrity Check ---")
spark.sql("""
    SELECT
        'pickup_location' as relationship,
        COUNT(*) as total_trips,
        SUM(CASE WHEN z.location_id IS NOT NULL THEN 1 ELSE 0 END) as matched,
        SUM(CASE WHEN z.location_id IS NULL THEN 1 ELSE 0 END) as unmatched
    FROM trips t
    LEFT JOIN zones z ON t.pickup_location_id = z.location_id
    UNION ALL
    SELECT
        'payment_type' as relationship,
        COUNT(*) as total_trips,
        SUM(CASE WHEN p.payment_type_id IS NOT NULL THEN 1 ELSE 0 END) as matched,
        SUM(CASE WHEN p.payment_type_id IS NULL THEN 1 ELSE 0 END) as unmatched
    FROM trips t
    LEFT JOIN payment_types p ON t.payment_type = p.payment_type_id
""").show()

# %% Cell 7: Create a technical metadata summary view

spark.sql("""
    CREATE OR REPLACE VIEW v_technical_metadata AS
    SELECT
        'trips' as table_name,
        'NYC Yellow Taxi trip records (Jan 2024)' as description,
        (SELECT COUNT(*) FROM trips) as row_count,
        19 as column_count
    UNION ALL
    SELECT
        'zones',
        'TLC taxi zone lookup (265 NYC zones)',
        (SELECT COUNT(*) FROM zones),
        4
    UNION ALL
    SELECT
        'payment_types',
        'Payment method reference (6 types)',
        (SELECT COUNT(*) FROM payment_types),
        2
    UNION ALL
    SELECT
        'rate_codes',
        'Fare calculation method reference (6 codes)',
        (SELECT COUNT(*) FROM rate_codes),
        2
""")

print("\n--- Technical Metadata Summary ---")
spark.sql("SELECT * FROM v_technical_metadata").show(truncate=False)

# %% [markdown]
# ## What the Technical Layer Gives Us
#
# We now have documented data:
# - **4 tables** with business descriptions
# - **Star schema** with verified join relationships
# - **Data profiling** showing distributions and volumes
# - **A metadata view** for programmatic discovery
#
# ## What It Cannot Do
#
# The technical layer tells us WHAT exists, but not:
# - How to compute "revenue" (that's the semantic layer)
# - Why Manhattan dominates trip volume (that's the ontology)
# - That cash tips are not recorded (that's a business rule in the ontology)
#
# ---
#
# **Next: [Step 03 — Semantic Layer with Spark →](03_semantic_layer_spark.py)**
