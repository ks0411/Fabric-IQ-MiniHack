# Fabric Notebook — Step 01: Data Foundation
# =============================================================================
# This notebook sets up the NYCTaxiLakehouse with all required tables.
# Run each cell sequentially in a Microsoft Fabric notebook.
#
# Prerequisites:
#   - A Fabric workspace with Fabric-enabled capacity
#   - A Lakehouse named "NYCTaxiLakehouse" (create it before running)
#   - Upload these files to the Lakehouse Files section:
#     1. yellow_tripdata_2024-01.parquet (from NYC TLC website)
#     2. taxi_zone_lookup.csv (from NYC TLC website)
#
# Data Source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
# =============================================================================

# %% [markdown]
# # Step 01: Data Foundation — Loading NYC Taxi Data
#
# ## What We're Building
#
# The foundation of our intelligent semantic layer is the **data layer**.
# We need 4 tables in our Lakehouse:
#
# | Table | Rows | Purpose |
# |-------|------|---------|
# | `trips` | ~2.76M | Yellow taxi trip records (Jan 2024) |
# | `zones` | 265 | TLC taxi zone lookup |
# | `payment_types` | 6 | Payment method descriptions |
# | `rate_codes` | 6 | Rate type descriptions |
#
# These tables form the star schema that our semantic layer and ontology
# will build upon.
#
# ```
# payment_types ──┐
#                  ├── trips ──┬── zones (pickup)
# rate_codes ──────┘           └── zones (dropoff)
# ```

# %% Cell 1: Create reference tables (dimension tables)

# ---- Payment Types ----
payment_types_data = [
    (1, "Credit card"),
    (2, "Cash"),
    (3, "No charge"),
    (4, "Dispute"),
    (5, "Unknown"),
    (6, "Voided trip")
]

df_payment = spark.createDataFrame(payment_types_data, ["payment_type_id", "description"])
df_payment.write.format("delta").mode("overwrite").saveAsTable("payment_types")
print(f"Created payment_types: {df_payment.count()} rows")

# ---- Rate Codes ----
rate_codes_data = [
    (1, "Standard rate"),
    (2, "JFK"),
    (3, "Newark"),
    (4, "Nassau or Westchester"),
    (5, "Negotiated fare"),
    (6, "Group ride")
]

df_rates = spark.createDataFrame(rate_codes_data, ["rate_code_id", "description"])
df_rates.write.format("delta").mode("overwrite").saveAsTable("rate_codes")
print(f"Created rate_codes: {df_rates.count()} rows")

# %% Cell 2: Create zones table from CSV

df_zones = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("Files/taxi_zone_lookup.csv")

# Rename columns to match our schema
df_zones = df_zones.withColumnRenamed("LocationID", "location_id") \
                   .withColumnRenamed("Borough", "borough") \
                   .withColumnRenamed("Zone", "zone_name") \
                   .withColumnRenamed("service_zone", "service_zone")

df_zones.write.format("delta").mode("overwrite").saveAsTable("zones")
print(f"Created zones: {df_zones.count()} rows")
df_zones.show(5)

# %% Cell 3: Load and transform trips data

df_trips = spark.read.parquet("Files/yellow_tripdata_2024-01.parquet")

print(f"Raw records: {df_trips.count():,}")
df_trips.printSchema()

# %% Cell 4: Rename columns to our standard naming convention

from pyspark.sql.functions import col

df_trips = df_trips \
    .withColumnRenamed("VendorID", "vendor_id") \
    .withColumnRenamed("tpep_pickup_datetime", "pickup_datetime") \
    .withColumnRenamed("tpep_dropoff_datetime", "dropoff_datetime") \
    .withColumnRenamed("PULocationID", "pickup_location_id") \
    .withColumnRenamed("DOLocationID", "dropoff_location_id") \
    .withColumnRenamed("RatecodeID", "rate_code_id") \
    .withColumnRenamed("Airport_fee", "airport_fee")

# Select and order columns
df_trips = df_trips.select(
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "pickup_location_id",
    "dropoff_location_id",
    "rate_code_id",
    "store_and_fwd_flag",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee"
)

# %% Cell 5: Clean data — filter invalid records

from pyspark.sql.functions import col

# Filter valid location IDs (1-265)
df_trips = df_trips.filter(
    (col("pickup_location_id").between(1, 265)) &
    (col("dropoff_location_id").between(1, 265))
)

# Filter valid payment types (1-6)
df_trips = df_trips.filter(col("payment_type").between(1, 6))

# Filter valid rate codes (1-6) or null
df_trips = df_trips.filter(
    col("rate_code_id").isNull() | col("rate_code_id").between(1, 6)
)

# Filter reasonable values
df_trips = df_trips.filter(
    (col("fare_amount") >= 0) &
    (col("total_amount") >= 0) &
    (col("trip_distance") >= 0)
)

print(f"Records after cleaning: {df_trips.count():,}")

# %% Cell 6: Write trips table

df_trips.write.format("delta").mode("overwrite").saveAsTable("trips")
print("Created trips table!")

# %% Cell 7: Verify all tables

print("=" * 60)
print("DATA VERIFICATION")
print("=" * 60)

tables = ["trips", "zones", "payment_types", "rate_codes"]
for table in tables:
    count = spark.sql(f"SELECT COUNT(*) FROM {table}").collect()[0][0]
    print(f"  {table}: {count:,} rows")

# %% Cell 8: Quick data quality checks

print("\n=== Revenue by Borough ===")
spark.sql("""
    SELECT
        z.borough,
        COUNT(*) as trip_count,
        ROUND(SUM(t.fare_amount + t.tip_amount), 2) as total_revenue,
        ROUND(AVG(t.tip_amount), 2) as avg_tip
    FROM trips t
    JOIN zones z ON t.pickup_location_id = z.location_id
    GROUP BY z.borough
    ORDER BY total_revenue DESC
""").show()

# %% Cell 9: Payment type analysis — this reveals a CRITICAL business rule

print("=== Payment Type Analysis (Critical Business Rule) ===")
spark.sql("""
    SELECT
        p.description as payment_type,
        COUNT(*) as trip_count,
        ROUND(AVG(t.tip_amount), 2) as avg_tip,
        ROUND(SUM(CASE WHEN t.tip_amount > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_with_tip
    FROM trips t
    JOIN payment_types p ON t.payment_type = p.payment_type_id
    GROUP BY p.description
    ORDER BY trip_count DESC
""").show()

# %% [markdown]
# ## Key Observation
#
# Look at the results above carefully:
#
# - **Credit card**: avg tip ~$3.40, ~98% have tips
# - **Cash**: avg tip ~$0.00, ~0% have tips
#
# **This is the Cash Tip Data Gap** — one of the most important business rules
# in this dataset. Cash tips are given directly to the driver and are NOT recorded
# in the electronic system.
#
# This is exactly the kind of knowledge that a semantic layer CANNOT capture
# (it only knows `avg_tip = mean(tip_amount)`) but an ontology CAN
# (it knows "tip analysis must exclude cash payments").
#
# We'll encode this rule in our ontology in Steps 05-06.
#
# ---
#
# **Next: [Step 02 — Technical Layer →](02_technical_layer.py)**
