# Fabric Notebook — Step 03: Semantic Layer with Spark SQL
# =============================================================================
# The Semantic Layer defines HOW to compute metrics consistently.
# In Fabric, we use Spark SQL views + Power BI Semantic Model.
#
# This step creates reusable metric views that serve as our
# "single source of truth" for business metrics.
# =============================================================================

# %% [markdown]
# # Step 03: Semantic Layer — Standardized Metrics
#
# ## The Semantic Layer in Context
#
# ```
# ┌──────────┐ ┌──────────┐ ┌───────────────┐
# │ SEMANTIC │ │ ONTOLOGY │ │  TECHNICAL    │
# │  LAYER   │ │  LAYER   │ │    LAYER      │
# │ COMPUTES │ │ EXPLAINS │ │  DOCUMENTS    │  ✅ Done
# │ metrics  │ │ why      │ │  what exists  │
# └──────────┘ └──────────┘ └───────────────┘
#      ▲
#      │
# YOU ARE HERE
# ```
#
# ## What This Notebook Creates
#
# | Output | Description |
# |---|---|
# | Spark SQL views | Reusable metric definitions |
# | Lakehouse-backed queries | Direct access to Delta tables |
# | Consistent business logic | Shared across notebooks and reports |
#
# ## Why Views as a Semantic Layer?
#
# Views provide:
# - **Consistent calculations**: Revenue is always `fare_amount + tip_amount`
# - **Reusability**: Any notebook or report can use these views
# - **Single source of truth**: One definition, not scattered SQL
# - **Abstraction**: Users don't need to know about joins

# %% Cell 1: Revenue by Borough (the most fundamental metric)

spark.sql("""
    CREATE OR REPLACE VIEW v_revenue_by_borough AS
    SELECT
        z.borough,
        COUNT(*) as trip_count,
        ROUND(SUM(t.fare_amount + t.tip_amount), 2) as total_revenue,
        ROUND(SUM(t.fare_amount), 2) as total_fare,
        ROUND(SUM(t.tip_amount), 2) as total_tips,
        ROUND(AVG(t.fare_amount), 2) as avg_fare,
        ROUND(AVG(t.tip_amount), 2) as avg_tip,
        ROUND(AVG(t.trip_distance), 2) as avg_distance,
        ROUND(AVG(t.total_amount), 2) as avg_total
    FROM trips t
    JOIN zones z ON t.pickup_location_id = z.location_id
    GROUP BY z.borough
""")

print("=== Revenue by Borough ===")
spark.sql("SELECT * FROM v_revenue_by_borough ORDER BY total_revenue DESC").show()

# %% Cell 2: Payment analysis view (includes credit card rate)

spark.sql("""
    CREATE OR REPLACE VIEW v_payment_analysis AS
    SELECT
        p.description as payment_type,
        p.payment_type_id,
        COUNT(*) as trip_count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct_of_trips,
        ROUND(AVG(t.fare_amount), 2) as avg_fare,
        ROUND(AVG(t.tip_amount), 2) as avg_tip,
        ROUND(SUM(CASE WHEN t.tip_amount > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as pct_with_tip,
        ROUND(AVG(t.total_amount), 2) as avg_total
    FROM trips t
    JOIN payment_types p ON t.payment_type = p.payment_type_id
    GROUP BY p.description, p.payment_type_id
""")

print("=== Payment Analysis ===")
spark.sql("SELECT * FROM v_payment_analysis ORDER BY trip_count DESC").show()

# %% Cell 3: Zone performance view (top zones by revenue)

spark.sql("""
    CREATE OR REPLACE VIEW v_zone_performance AS
    SELECT
        z.zone_name,
        z.borough,
        COUNT(*) as trip_count,
        ROUND(SUM(t.fare_amount + t.tip_amount), 2) as total_revenue,
        ROUND(AVG(t.fare_amount + t.tip_amount), 2) as avg_revenue_per_trip,
        ROUND(AVG(t.trip_distance), 2) as avg_distance,
        ROUND(AVG(t.tip_amount), 2) as avg_tip,
        ROUND(
            SUM(CASE WHEN t.payment_type = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            1
        ) as credit_card_pct
    FROM trips t
    JOIN zones z ON t.pickup_location_id = z.location_id
    GROUP BY z.zone_name, z.borough
""")

print("=== Top 15 Zones by Revenue ===")
spark.sql("""
    SELECT * FROM v_zone_performance
    ORDER BY total_revenue DESC
    LIMIT 15
""").show(truncate=False)

# %% Cell 4: Airport analysis view

spark.sql("""
    CREATE OR REPLACE VIEW v_airport_analysis AS
    SELECT
        CASE
            WHEN t.rate_code_id = 2 THEN 'JFK Flat Rate'
            WHEN t.rate_code_id = 3 THEN 'Newark'
            WHEN t.pickup_location_id IN (132, 138) OR t.dropoff_location_id IN (132, 138) THEN 'LaGuardia'
            WHEN t.pickup_location_id = 1 OR t.dropoff_location_id = 1 THEN 'Newark (by zone)'
            ELSE 'Non-Airport'
        END as airport_type,
        COUNT(*) as trip_count,
        ROUND(AVG(t.fare_amount + t.tip_amount), 2) as avg_revenue,
        ROUND(AVG(t.trip_distance), 2) as avg_distance,
        ROUND(AVG(t.tip_amount), 2) as avg_tip
    FROM trips t
    WHERE t.rate_code_id IN (2, 3)
       OR t.pickup_location_id IN (1, 132, 138)
       OR t.dropoff_location_id IN (1, 132, 138)
    GROUP BY
        CASE
            WHEN t.rate_code_id = 2 THEN 'JFK Flat Rate'
            WHEN t.rate_code_id = 3 THEN 'Newark'
            WHEN t.pickup_location_id IN (132, 138) OR t.dropoff_location_id IN (132, 138) THEN 'LaGuardia'
            WHEN t.pickup_location_id = 1 OR t.dropoff_location_id = 1 THEN 'Newark (by zone)'
            ELSE 'Non-Airport'
        END
""")

print("=== Airport Trip Analysis ===")
spark.sql("SELECT * FROM v_airport_analysis ORDER BY trip_count DESC").show()

# %% Cell 5: Time context analysis view

spark.sql("""
    CREATE OR REPLACE VIEW v_time_analysis AS
    SELECT
        CASE
            WHEN (HOUR(t.pickup_datetime) BETWEEN 7 AND 9
                  OR HOUR(t.pickup_datetime) BETWEEN 17 AND 20)
                 AND DAYOFWEEK(t.pickup_datetime) BETWEEN 2 AND 6
            THEN 'Rush Hour'
            WHEN HOUR(t.pickup_datetime) >= 22
                 OR HOUR(t.pickup_datetime) < 5
            THEN 'Night Time'
            WHEN DAYOFWEEK(t.pickup_datetime) IN (1, 7)
            THEN 'Weekend'
            ELSE 'Off-Peak'
        END as time_context,
        COUNT(*) as trip_count,
        ROUND(AVG(t.fare_amount + t.tip_amount), 2) as avg_revenue,
        ROUND(AVG(t.tip_amount), 2) as avg_tip,
        ROUND(AVG(t.trip_distance), 2) as avg_distance
    FROM trips t
    GROUP BY
        CASE
            WHEN (HOUR(t.pickup_datetime) BETWEEN 7 AND 9
                  OR HOUR(t.pickup_datetime) BETWEEN 17 AND 20)
                 AND DAYOFWEEK(t.pickup_datetime) BETWEEN 2 AND 6
            THEN 'Rush Hour'
            WHEN HOUR(t.pickup_datetime) >= 22
                 OR HOUR(t.pickup_datetime) < 5
            THEN 'Night Time'
            WHEN DAYOFWEEK(t.pickup_datetime) IN (1, 7)
            THEN 'Weekend'
            ELSE 'Off-Peak'
        END
""")

print("=== Time Context Analysis ===")
spark.sql("SELECT * FROM v_time_analysis ORDER BY trip_count DESC").show()

# %% Cell 6: Trip classification view (maps to ontology trip types)

spark.sql("""
    CREATE OR REPLACE VIEW v_trip_classification AS
    SELECT
        CASE
            WHEN t.rate_code_id IN (2, 3) THEN 'Airport'
            WHEN t.trip_distance > 10 THEN 'Long Distance'
            WHEN t.trip_distance < 2 THEN 'Short'
            WHEN (HOUR(t.pickup_datetime) BETWEEN 7 AND 9
                  OR HOUR(t.pickup_datetime) BETWEEN 17 AND 19)
                 AND DAYOFWEEK(t.pickup_datetime) BETWEEN 2 AND 6
            THEN 'Commute'
            WHEN HOUR(t.pickup_datetime) >= 22
                 OR HOUR(t.pickup_datetime) < 5
            THEN 'Night'
            WHEN DAYOFWEEK(t.pickup_datetime) IN (1, 7)
            THEN 'Weekend'
            ELSE 'Standard'
        END as trip_type,
        COUNT(*) as trip_count,
        ROUND(SUM(t.fare_amount + t.tip_amount), 2) as total_revenue,
        ROUND(AVG(t.fare_amount + t.tip_amount), 2) as avg_revenue,
        ROUND(AVG(t.trip_distance), 2) as avg_distance,
        ROUND(AVG(t.tip_amount), 2) as avg_tip
    FROM trips t
    GROUP BY
        CASE
            WHEN t.rate_code_id IN (2, 3) THEN 'Airport'
            WHEN t.trip_distance > 10 THEN 'Long Distance'
            WHEN t.trip_distance < 2 THEN 'Short'
            WHEN (HOUR(t.pickup_datetime) BETWEEN 7 AND 9
                  OR HOUR(t.pickup_datetime) BETWEEN 17 AND 19)
                 AND DAYOFWEEK(t.pickup_datetime) BETWEEN 2 AND 6
            THEN 'Commute'
            WHEN HOUR(t.pickup_datetime) >= 22
                 OR HOUR(t.pickup_datetime) < 5
            THEN 'Night'
            WHEN DAYOFWEEK(t.pickup_datetime) IN (1, 7)
            THEN 'Weekend'
            ELSE 'Standard'
        END
""")

print("=== Trip Classification ===")
spark.sql("SELECT * FROM v_trip_classification ORDER BY trip_count DESC").show()

# %% Cell 7: Tip analysis view — credit card only (applying the business rule manually)

spark.sql("""
    CREATE OR REPLACE VIEW v_tip_analysis_correct AS
    SELECT
        z.borough,
        COUNT(*) as cc_trip_count,
        ROUND(AVG(t.tip_amount), 2) as avg_tip,
        ROUND(AVG(t.tip_amount / NULLIF(t.fare_amount, 0)) * 100, 1) as avg_tip_pct,
        ROUND(MIN(t.tip_amount), 2) as min_tip,
        ROUND(MAX(t.tip_amount), 2) as max_tip
    FROM trips t
    JOIN zones z ON t.pickup_location_id = z.location_id
    WHERE t.payment_type = 1  -- Credit card only!
      AND t.fare_amount > 0
    GROUP BY z.borough
""")

print("=== Tip Analysis (Credit Card Only — Correct Method) ===")
spark.sql("SELECT * FROM v_tip_analysis_correct ORDER BY avg_tip DESC").show()

# Compare with the INCORRECT analysis (all payment types)
print("=== Tip Analysis (All Payments — INCORRECT Method) ===")
spark.sql("""
    SELECT
        z.borough,
        COUNT(*) as all_trip_count,
        ROUND(AVG(t.tip_amount), 2) as avg_tip_WRONG,
        ROUND(AVG(CASE WHEN t.payment_type = 1 THEN t.tip_amount END), 2) as avg_tip_CORRECT
    FROM trips t
    JOIN zones z ON t.pickup_location_id = z.location_id
    GROUP BY z.borough
    ORDER BY avg_tip_WRONG DESC
""").show()

# %% Cell 8: Summary of all semantic views

print("=" * 60)
print("SEMANTIC LAYER SUMMARY")
print("=" * 60)
print("""
Views created (our semantic layer):

  v_revenue_by_borough     — Revenue metrics grouped by borough
  v_payment_analysis       — Payment type breakdown with tip analysis
  v_zone_performance       — Zone-level performance metrics
  v_airport_analysis       — Airport trip breakdown (JFK/Newark/LaGuardia)
  v_time_analysis          — Time context analysis (rush/night/weekend)
  v_trip_classification    — Trip type classification with metrics
  v_tip_analysis_correct   — Tips by borough (credit card only)
  v_technical_metadata     — Table metadata summary (from Step 02)

Measures defined:
  - trip_count, total_revenue, total_fare, total_tips
  - avg_fare, avg_tip, avg_total, avg_distance
  - credit_card_pct, pct_with_tip
  - avg_revenue_per_trip

Dimensions used:
  - borough, zone_name, payment_type
  - rate_code_id, time_context, trip_type
""")

# %% [markdown]
# ## What the Semantic Layer Gives Us
#
# We now have consistent, reusable metric definitions:
# - Revenue is **always** `fare_amount + tip_amount`
# - Trip types follow **consistent** classification rules
# - Airport trips are **always** identified by rate_code or location
#
# ## What It Still Cannot Do
#
# Ask the semantic layer: **"Why is Manhattan revenue 5x higher than Brooklyn?"**
#
# It can tell you the NUMBERS ($44M vs $8.5M) but not the REASONS:
# - Business district concentration drives demand
# - Tourist activity generates higher fares
# - Limited parking forces people to take taxis
# - ~90% of all yellow taxi trips start in Manhattan
#
# **That's what the ontology layer is for. Let's see the gap first.**
#
# ---
#
# **Next: [Step 04 — The Ontology Gap →](04_the_ontology_gap.md)**
