# Step 03b: Semantic Layer — Power BI Semantic Model with DAX (UI Guide)    

**Duration: 30 minutes | Type: Hands-on (Fabric UI)**

---

## Overview

Step 03 (`03_semantic_layer_spark.py`) creates the semantic layer programmatically using Spark SQL views. This companion guide shows you how to build the semantic layer as a **Power BI Semantic Model** using **DAX measures** — entirely through the Fabric UI.

### Why Two Approaches?

| Approach | Technology | Best For |
|---|---|---|
| **Step 03** (Spark SQL views) | PySpark + SQL | Notebook users, data engineers, programmatic access |
| **Step 03b** (This step) | Power BI + DAX | Report builders, analysts, visual exploration, Fabric Ontology integration |

The Power BI Semantic Model is also what Fabric uses to **generate ontologies** (the "Generate from Semantic Model" path in Step 05). Having a well-structured semantic model makes ontology creation much smoother.

### What Is a Semantic Model in Fabric?

A **semantic model** (formerly called a "Power BI dataset") is a structured representation of your data that includes:
- **Tables** (connected to your Lakehouse delta tables)
- **Relationships** (foreign keys between tables)
- **Measures** (DAX formulas that compute metrics like revenue, avg tip, trip count)
- **Calculated columns** (derived columns using DAX)
- **Hierarchies** (e.g., Borough → Zone)

Think of it as the Fabric-native semantic layer: relationships, measures, and metadata in one model.

---

## Part 1: Create the Semantic Model

### 1.1: Navigate to Your Lakehouse

1. Open **https://app.fabric.microsoft.com**
2. Go to your workspace (e.g., `NYCTaxiWorkshop`)
3. Click on **NYCTaxiLakehouse** to open it

### 1.2: Create the Semantic Model from Lakehouse Tables

1. In the Lakehouse view, look at the **top ribbon**
2. Click **New semantic model** (or find it under **New item** → **Semantic model**)

   > If you don't see this option directly:
   > - Go to your workspace
   > - Click **+ New item**
   > - Select **Semantic model (Power BI)**
   > - Choose **Direct Lake** as the connection mode (this connects directly to Lakehouse delta tables)

3. In the **New semantic model** dialog:
   - **Name**: `NYCTaxiSemanticModel`
   - **Select tables**: Check all 4 tables:
     - ☑ `trips`
     - ☑ `zones`
     - ☑ `payment_types`
     - ☑ `rate_codes`
   - Click **Create** (or **Confirm**)

4. Wait for the model to be created. You'll be taken to the **model editor**.

---

## Part 2: Understand the Semantic Model Editor

The editor has several views. Here's what you'll see:

### 2.1: Key UI Areas

```
┌──────────────────────────────────────────────────────────────────┐
│  [Home]  [Model view]  [Data view]  [DAX query view]            │  ← Ribbon tabs
├──────────────┬───────────────────────────────────────────────────┤
│              │                                                   │
│  Data panel  │              Model canvas                         │
│  (left)      │    (shows tables as boxes with columns)          │
│              │                                                   │
│  • Tables    │    ┌─────────┐    ┌─────────┐                    │
│  • Columns   │    │  trips  │─── │  zones  │                    │
│  • Measures  │    └─────────┘    └─────────┘                    │
│              │                                                   │
│              │    ┌───────────┐  ┌──────────┐                   │
│              │    │payment_   │  │rate_     │                   │
│              │    │types      │  │codes     │                   │
│              │    └───────────┘  └──────────┘                   │
│              │                                                   │
├──────────────┴───────────────────────────────────────────────────┤
│  Properties panel (right) — shows selected item's properties     │
└──────────────────────────────────────────────────────────────────┘
```

| View | Purpose | How to Access |
|---|---|---|
| **Model view** | See tables, relationships, create measures | Click "Model view" tab or icon |
| **Data view** | Preview data in tables | Click "Data view" tab |
| **DAX query view** | Write and test DAX queries | Click "DAX query view" tab |
| **Properties panel** | Edit names, descriptions, formatting | Right side (appears when you select something) |

---

## Part 3: Create Relationships Between Tables

Relationships define how tables connect — this is the join logic for the model.

### 3.1: Switch to Model View

1. Click the **Model view** tab/icon (it looks like a diagram with connected boxes)
2. You should see your 4 tables as boxes on the canvas
3. Each box shows the table name and its columns

### 3.2: Create Relationship: trips → zones (Pickup)

1. In the `trips` table box, find the `pickup_location_id` column
2. **Click and drag** from `pickup_location_id` to `location_id` in the `zones` table
3. A **Create relationship** dialog appears:

| Setting | Value |
|---|---|
| **From table** | `trips` |
| **From column** | `pickup_location_id` |
| **To table** | `zones` |
| **To column** | `location_id` |
| **Cardinality** | Many-to-one (*:1) |
| **Cross filter direction** | Single |
| **Make this relationship active** | ☑ Yes |

4. Click **OK** (or **Create**)
5. A line appears connecting the two tables

> **Important**: This is the "active" relationship for zones. Since trips has TWO zone references (pickup and dropoff), only one can be active. We'll make pickup the active one.

### 3.3: Create Relationship: trips → zones (Dropoff)

1. Drag from `dropoff_location_id` in `trips` to `location_id` in `zones`
2. In the dialog:

| Setting | Value |
|---|---|
| **From table** | `trips` |
| **From column** | `dropoff_location_id` |
| **To table** | `zones` |
| **To column** | `location_id` |
| **Cardinality** | Many-to-one (*:1) |
| **Cross filter direction** | Single |
| **Make this relationship active** | ☐ **No** (inactive — use USERELATIONSHIP in DAX when needed) |

3. Click **OK**
4. The line appears as **dashed** (indicating inactive relationship)

### 3.4: Create Relationship: trips → payment_types

1. Drag from `payment_type` in `trips` to `payment_type_id` in `payment_types`
2. Settings:

| Setting | Value |
|---|---|
| **From / To** | `trips.payment_type` → `payment_types.payment_type_id` |
| **Cardinality** | Many-to-one (*:1) |
| **Active** | ☑ Yes |

3. Click **OK**

### 3.5: Create Relationship: trips → rate_codes

1. Drag from `rate_code_id` in `trips` to `rate_code_id` in `rate_codes`
2. Settings:

| Setting | Value |
|---|---|
| **From / To** | `trips.rate_code_id` → `rate_codes.rate_code_id` |
| **Cardinality** | Many-to-one (*:1) |
| **Active** | ☑ Yes |

3. Click **OK**

### 3.6: Verify Relationships

Your model canvas should now show:

```
         zones
          ▲  ▲
     (active) (dashed/inactive)
     pickup    dropoff
          │  │
          trips ────────► payment_types
          │
          └────────────► rate_codes
```

You should see **4 relationship lines**: 3 solid (active) and 1 dashed (inactive).

## Part 4: Create DAX Measures

Measures are reusable calculations — the heart of the semantic layer.

### 4.1: How to Create a Measure

1. In **Model view** or **Data view**, select the `trips` table in the left Data panel
2. In the top ribbon, click **New measure**
   - Alternatively: right-click on the `trips` table → **New measure**
3. The **formula bar** appears at the top of the center panel
4. Type your DAX formula
5. Press **Enter** or click the **checkmark** to confirm
6. The measure appears under the `trips` table with a calculator icon (fx)

### 4.2: Volume Measures

Create each measure one at a time:

**Measure 1: Trip Count**
```dax
Trip Count = COUNTROWS(trips)
```

After pressing Enter:
- In the **Properties panel** (right side), set:
  - **Description**: `Total number of completed taxi trips`
  - **Format**: Whole number (no decimal places)
  - **Display folder**: `Volume` (type this to organize measures)

---

### 4.3: Revenue Measures

**Measure 2: Total Revenue**
```dax
Total Revenue = SUMX(trips, trips[fare_amount] + trips[tip_amount])
```

Properties:
- **Description**: `Sum of fare + tip amounts. Does NOT include tolls, surcharges, or fees.`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

**Measure 3: Total Fare**
```dax
Total Fare = SUM(trips[fare_amount])
```

Properties:
- **Description**: `Sum of base fare amounts from the meter`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

**Measure 4: Total Tips**
```dax
Total Tips = SUM(trips[tip_amount])
```

Properties:
- **Description**: `Sum of tip amounts. IMPORTANT: Only includes credit card tips. Cash tips are NOT recorded.`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

**Measure 5: Average Fare**
```dax
Avg Fare = AVERAGE(trips[fare_amount])
```

Properties:
- **Description**: `Average fare per trip. Higher in areas with longer trips or airport service.`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

**Measure 6: Average Tip**
```dax
Avg Tip = AVERAGE(trips[tip_amount])
```

Properties:
- **Description**: `Average tip per trip. WARNING: Cash tips (payment_type=2) are NOT recorded, showing as $0. This measure is misleading when cash trips are included. Use "Avg Tip (CC Only)" for accurate tip analysis.`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

**Measure 7: Average Tip (Credit Card Only) — The Correct Measure**
```dax
Avg Tip (CC Only) =
CALCULATE(
    AVERAGE(trips[tip_amount]),
    trips[payment_type] = 1
)
```

Properties:
- **Description**: `Average tip per trip, filtered to credit card payments only. This is the CORRECT way to analyze tips because cash tips are not recorded in the data.`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

**Measure 8: Average Total**
```dax
Avg Total = AVERAGE(trips[total_amount])
```

Properties:
- **Description**: `Average total charge per trip including all fees and surcharges`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

**Measure 9: Total Amount**
```dax
Total Amount = SUM(trips[total_amount])
```

Properties:
- **Description**: `Sum of all charges including fare, tips, tolls, surcharges, and fees`
- **Format**: Currency ($), 2 decimal places
- **Display folder**: `Revenue`

---

### 4.4: Distance Measures

**Measure 10: Average Distance**
```dax
Avg Distance = AVERAGE(trips[trip_distance])
```

Properties:
- **Description**: `Average trip distance in miles. Manhattan trips average 2-3 miles. Airport trips average 10-20 miles.`
- **Format**: Decimal number, 2 decimal places, suffix ` mi`
- **Display folder**: `Distance`

---

**Measure 11: Total Distance**
```dax
Total Distance = SUM(trips[trip_distance])
```

Properties:
- **Description**: `Total miles traveled across all trips`
- **Format**: Whole number
- **Display folder**: `Distance`

---

### 4.5: Passenger Measures

**Measure 12: Average Passengers**
```dax
Avg Passengers = AVERAGE(trips[passenger_count])
```

Properties:
- **Description**: `Average number of passengers per trip (driver-reported)`
- **Format**: Decimal number, 1 decimal place
- **Display folder**: `Passengers`

---

**Measure 13: Total Passengers**
```dax
Total Passengers = SUM(trips[passenger_count])
```

Properties:
- **Description**: `Total passengers transported across all trips`
- **Format**: Whole number
- **Display folder**: `Passengers`

---

### 4.6: Payment Analysis Measures

**Measure 14: Credit Card Trips**
```dax
Credit Card Trips = CALCULATE(COUNTROWS(trips), trips[payment_type] = 1)
```

Properties:
- **Description**: `Number of trips paid by credit card. These are the only trips with recorded tip data.`
- **Format**: Whole number
- **Display folder**: `Payment`

---

**Measure 15: Cash Trips**
```dax
Cash Trips = CALCULATE(COUNTROWS(trips), trips[payment_type] = 2)
```

Properties:
- **Description**: `Number of trips paid in cash. IMPORTANT: Tips are NOT recorded for cash payments.`
- **Format**: Whole number
- **Display folder**: `Payment`

---

**Measure 16: Credit Card Rate**
```dax
Credit Card Rate =
DIVIDE(
    CALCULATE(COUNTROWS(trips), trips[payment_type] = 1),
    COUNTROWS(trips),
    0
)
```

Properties:
- **Description**: `Percentage of trips paid by credit card. Higher rates mean more reliable tip data. Manhattan ~70%, outer boroughs lower.`
- **Format**: Percentage, 1 decimal place
- **Display folder**: `Payment`

---

**Measure 17: Pct With Tip**
```dax
Pct With Tip =
DIVIDE(
    CALCULATE(COUNTROWS(trips), trips[tip_amount] > 0),
    COUNTROWS(trips),
    0
)
```

Properties:
- **Description**: `Percentage of trips with a recorded tip. Low values in a borough may indicate high cash usage, not low tipping.`
- **Format**: Percentage, 1 decimal place
- **Display folder**: `Payment`

---

### 4.7: Airport Measures

**Measure 18: Airport Trips**
```dax
Airport Trips =
CALCULATE(
    COUNTROWS(trips),
    trips[rate_code_id] IN {2, 3}
)
```

Properties:
- **Description**: `Number of airport trips identified by rate code. Rate code 2 = JFK flat rate ($52), Rate code 3 = Newark.`
- **Format**: Whole number
- **Display folder**: `Airport`

---

**Measure 19: Airport Trip Rate**
```dax
Airport Trip Rate =
DIVIDE(
    CALCULATE(COUNTROWS(trips), trips[rate_code_id] IN {2, 3}),
    COUNTROWS(trips),
    0
)
```

Properties:
- **Description**: `Percentage of trips that are airport trips (rate code 2 or 3)`
- **Format**: Percentage, 1 decimal place
- **Display folder**: `Airport`

---

### 4.8: Surcharge Measures

**Measure 20: Total Tolls**
```dax
Total Tolls = SUM(trips[tolls_amount])
```

Properties: Format: Currency ($), Display folder: `Surcharges`

---

**Measure 21: Total Congestion Surcharge**
```dax
Total Congestion = SUM(trips[congestion_surcharge])
```

Properties: Format: Currency ($), Display folder: `Surcharges`

---

**Measure 22: Total Airport Fee**
```dax
Total Airport Fee = SUM(trips[airport_fee])
```

Properties: Format: Currency ($), Display folder: `Surcharges`

---

### 4.9: Advanced Measures (Tip Analysis with Business Rules)

**Measure 23: Tip Percentage (Credit Card Only)**
```dax
Tip Pct (CC Only) =
CALCULATE(
    DIVIDE(
        SUM(trips[tip_amount]),
        SUM(trips[fare_amount]),
        0
    ),
    trips[payment_type] = 1,
    trips[fare_amount] > 0
)
```

Properties:
- **Description**: `Average tip as percentage of fare, for credit card payments only. Business districts typically see 15-20%. This is the correct way to measure tipping behavior.`
- **Format**: Percentage, 1 decimal place
- **Display folder**: `Revenue`

---

## Part 5: Set Up Display Formatting

### 5.1: Organize with Display Folders

After creating all measures, verify they're organized:

1. In the Data panel (left), expand the `trips` table
2. You should see measures grouped by folder:
   - **Revenue**: Total Revenue, Total Fare, Total Tips, Avg Fare, Avg Tip, Avg Tip (CC Only), Avg Total, Total Amount, Tip Pct (CC Only)
   - **Volume**: Trip Count
   - **Distance**: Avg Distance, Total Distance
   - **Passengers**: Avg Passengers, Total Passengers
   - **Payment**: Credit Card Trips, Cash Trips, Credit Card Rate, Pct With Tip
   - **Airport**: Airport Trips, Airport Trip Rate
   - **Surcharges**: Total Tolls, Total Congestion, Total Airport Fee

### 5.2: Hide Technical Columns

Some columns are foreign keys and shouldn't appear in reports:

1. In the Data panel, right-click on `trips` → `pickup_location_id`
2. Select **Hide in report view**
3. Repeat for:
   - `trips.dropoff_location_id`
   - `trips.payment_type` (users should use `payment_types.description` instead)
   - `trips.rate_code_id` (users should use `rate_codes.description` instead)
   - `trips.vendor_id`
   - `trips.store_and_fwd_flag`

Hidden columns still work in DAX and relationships, but don't clutter the report field list.

### 5.3: Rename Columns for User-Friendliness (Optional)

In the Properties panel, you can rename columns to be more readable:

1. Click on `zones.zone_name` in the Data panel
2. In Properties, change **Name** to `Zone Name`
3. Do the same for other columns:
   - `zones.borough` → `Borough`
   - `zones.service_zone` → `Service Zone`
   - `payment_types.description` → `Payment Type`
   - `rate_codes.description` → `Rate Type`
   - `trips.pickup_datetime` → `Pickup DateTime`
   - `trips.trip_distance` → `Trip Distance (miles)`

---

## Part 6: Create a Date Table (Optional but Recommended)

A proper date table enables time intelligence in DAX:

### 6.1: Create the Date Table with DAX

In the ribbon, click **New table** and enter:

```dax
DateTable =
ADDCOLUMNS(
    CALENDAR(DATE(2024, 1, 1), DATE(2024, 1, 31)),
    "Year", YEAR([Date]),
    "Month", MONTH([Date]),
    "Day", DAY([Date]),
    "DayOfWeek", WEEKDAY([Date], 2),
    "DayName", FORMAT([Date], "dddd"),
    "IsWeekend", IF(WEEKDAY([Date], 2) >= 6, "Weekend", "Weekday"),
    "TimeContext",
        SWITCH(TRUE(),
            WEEKDAY([Date], 2) >= 6, "Weekend",
            TRUE(), "Weekday"
        )
)
```

### 6.2: Mark as Date Table

1. Select the `DateTable` in the Data panel
2. In the ribbon, click **Mark as date table**
3. Select the `Date` column as the date column
4. Click **OK**

### 6.3: Create Relationship

1. Switch to Model view
2. Drag from `trips.pickup_datetime` to `DateTable.Date`
   - Note: This may require the pickup_datetime to be cast to a date-only column

---

## Part 7: Test Your Measures

### 7.1: Use DAX Query View

1. Click the **DAX query view** tab in the ribbon
2. Test your measures:

```dax
EVALUATE
SUMMARIZECOLUMNS(
    zones[borough],
    "Trip Count", [Trip Count],
    "Total Revenue", [Total Revenue],
    "Avg Tip", [Avg Tip],
    "Avg Tip CC Only", [Avg Tip (CC Only)],
    "CC Rate", [Credit Card Rate]
)
```

Click **▶ Run**. You should see a table with each borough and its metrics.

### 7.2: Test the Tip Analysis Business Rule

```dax
EVALUATE
SUMMARIZECOLUMNS(
    payment_types[Payment Type],
    "Trip Count", [Trip Count],
    "Avg Tip", [Avg Tip],
    "Pct With Tip", [Pct With Tip]
)
```

**Expected result**: This shows that Cash has $0 avg tip and 0% with tip — confirming the business rule.

### 7.3: Test Airport Analysis

```dax
EVALUATE
SUMMARIZECOLUMNS(
    rate_codes[Rate Type],
    "Trip Count", [Trip Count],
    "Avg Fare", [Avg Fare],
    "Avg Tip CC Only", [Avg Tip (CC Only)]
)
```

---

## Part 8: Review and Organize the Model

1. Confirm all measures are placed in the correct **Display folders** (Volume, Revenue, Distance, Passengers, Payment, Airport, Surcharges)
2. Add or review **Descriptions** for key measures so they show up in the Fabric Ontology
3. If desired, hide raw technical columns in the report view to keep the model clean

---

## Part 9: Publish and Use

### 9.1: Save the Semantic Model

The model auto-saves in Fabric. To manually save:
- Click **Save** (Ctrl+S) in the ribbon
- Or the model saves when you navigate away

### 9.2: Use for Reports — Step-by-Step for First-Time Power BI Users

#### 9.2.1: Create the Report

1. Go to your **workspace** (click the workspace name in the left nav)
2. Click **+ New item**
3. Select **Report**
4. A dialog asks you to choose a data source — select **Pick a published semantic model**
5. Find and select **NYCTaxiSemanticModel**
6. Click **Auto-create a report** for a quick start, or **Create a blank report** to build from scratch
7. Choose **Create a blank report** (we'll learn by doing)

#### 9.2.2: Understand the Report Editor

You'll see three panels:

```
┌─────────────────────────────────────────────────────────────────┐
│  [File]  [Home]  [Insert]  [Format]                             │  ← Ribbon
├──────────────────────────────────┬──────────────────────────────┤
│                                  │  Visualizations panel        │
│                                  │  ┌───┬───┬───┬───┐          │
│      REPORT CANVAS               │  │ Bar│Pie│Tbl│Lin│ ...     │
│                                  │  └───┴───┴───┴───┘          │
│   (this is where your charts     │                              │
│    and tables will appear)       │  Build visual:               │
│                                  │  • X-axis                    │
│                                  │  • Y-axis                    │
│                                  │  • Values                    │
│                                  │  • Legend                    │
│                                  │  • Filters                   │
│                                  ├──────────────────────────────┤
│                                  │  Data panel                  │
│                                  │                              │
│                                  │  ▸ trips                     │
│                                  │    ▸ Revenue (folder)        │
│                                  │      Σ Total Revenue         │
│                                  │      Σ Avg Fare              │
│                                  │    ▸ Volume (folder)         │
│                                  │      Σ Trip Count            │
│                                  │  ▸ zones                     │
│                                  │      Borough                 │
│                                  │      Zone Name               │
│                                  │  ▸ payment_types             │
│                                  │      Payment Type            │
│                                  │  ▸ rate_codes                │
│                                  │      Rate Type               │
└──────────────────────────────────┴──────────────────────────────┘
```

- **Report canvas** (center): Where visuals appear
- **Visualizations panel** (top right): Choose chart types and configure axes
- **Data panel** (bottom right): Your tables, columns, and measures (Σ icon = measure)

---

#### 9.2.3: Visualization 1 — Bar Chart: Revenue by Borough

This is the most fundamental chart — it immediately shows Manhattan dominance.

1. In the **Visualizations panel**, click the **Clustered bar chart** icon (horizontal bars)
2. An empty chart placeholder appears on the canvas
3. From the **Data panel** (bottom right):
   - Find `zones` → drag **Borough** to the **Y-axis** well
   - Find `trips` → Revenue folder → drag **Total Revenue** to the **X-axis** well
4. The chart now shows horizontal bars with revenue per borough
5. To sort: click the **three dots (...)** on the chart → **Sort axis** → **Total Revenue** → **Descending**

**What you should see**: Manhattan bar is massively longer than all others — this is the "Manhattan dominance" the workshop talks about.

**Resize the chart**: Click and drag the corner handles to make it bigger.

---

#### 9.2.4: Visualization 2 — Table: Payment Type Breakdown

This table shows the critical cash tip data gap.

1. Click on an **empty area** of the canvas (so you deselect the bar chart)
2. In Visualizations, click the **Table** icon (grid of rows/columns)
3. From the Data panel, drag these fields into the **Columns** well (drag them one by one):
   - `payment_types` → **Payment Type**
   - `trips` → Volume → **Trip Count**
   - `trips` → Revenue → **Avg Tip**
   - `trips` → Revenue → **Avg Tip (CC Only)**
   - `trips` → Payment → **Pct With Tip**
4. The table now shows each payment type with its metrics

**What you should see**:
| Payment Type | Trip Count | Avg Tip | Avg Tip (CC Only) | Pct With Tip |
|---|---|---|---|---|
| Credit card | ~1.9M | ~$3.40 | ~$3.40 | ~97% |
| Cash | ~800K | $0.00 | (blank) | 0% |

This is the **Cash Tip Data Gap** — the #1 business rule in our ontology.

---

#### 9.2.5: Visualization 3 — Pie Chart: Credit Card vs Cash Split

1. Click on an **empty area** of the canvas
2. In Visualizations, click the **Pie chart** icon
3. From the Data panel:
   - Drag `payment_types` → **Payment Type** to the **Legend** well
   - Drag `trips` → Volume → **Trip Count** to the **Values** well
4. The pie chart shows the proportion of each payment method

**What you should see**: Credit card is ~70%, Cash is ~30%. This matters because tip data only exists for the credit card slice.

---

#### 9.2.6: Visualization 4 — Clustered Column Chart: Tips by Borough (The Misleading One)

This chart demonstrates WHY you need an ontology — it shows a misleading picture.

1. Click on an **empty area** of the canvas
2. Click the **Clustered column chart** icon (vertical bars)
3. From the Data panel:
   - Drag `zones` → **Borough** to the **X-axis** well
   - Drag `trips` → Revenue → **Avg Tip** to the **Y-axis** well
4. Now add the correct measure for comparison:
   - Drag `trips` → Revenue → **Avg Tip (CC Only)** to the **Y-axis** well (next to Avg Tip)
5. You now have two bars per borough — the wrong metric and the correct metric side by side

**What you should see**: The "Avg Tip" bar (includes cash $0s) is much lower in outer boroughs. The "Avg Tip (CC Only)" bar shows the real tipping behavior — the gap between boroughs is much smaller.

**This is the visualization that proves the ontology's value**: without the business rule "cash tips aren't recorded," you'd conclude Brooklyn tips less. With the rule, you see it's a data artifact.

---

#### 9.2.7: Visualization 5 — Card: Key Numbers

Cards show a single big number — great for dashboards.

1. Click an **empty area** of the canvas
2. Click the **Card** icon (shows a single number)
3. Drag `trips` → Volume → **Trip Count** to the **Fields** well
4. A big number appears: ~2,764,118

Repeat to create more cards:
- **Total Revenue** card (drag Total Revenue to a new Card visual)
- **Credit Card Rate** card (shows ~70%)
- **Airport Trips** card

**Arrange them**: Drag the card visuals to the top of the canvas in a row to create a KPI header:

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  2,764,118   │ │  $47,234,567 │ │    69.8%     │ │   45,231     │
│  Trip Count  │ │ Total Revenue│ │  CC Rate     │ │Airport Trips │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

#### 9.2.8: Add a Slicer (Interactive Filter)

Slicers let you filter all visuals on the page at once.

1. Click an **empty area**
2. Click the **Slicer** icon (funnel-like icon in Visualizations)
3. Drag `zones` → **Borough** to the **Field** well
4. A list of boroughs appears (Manhattan, Brooklyn, Queens, etc.)
5. Click **Manhattan** — all charts on the page instantly filter to Manhattan only
6. Click **Manhattan** again to deselect (or click **Select all**)

Try clicking **Brooklyn** — watch how the revenue bar, tip charts, and cards all update. This is the power of a semantic model: one set of measures, interactive filtering.

---

#### 9.2.9: Save the Report

1. Click **File** → **Save**
2. Name: `NYCTaxiDashboard`
3. Select your workspace
4. Click **Save**

The report is now in your workspace alongside the Lakehouse and Semantic Model.

---

#### 9.2.10: Summary of What You Built

| Visual | Type | What It Shows |
|---|---|---|
| Revenue by Borough | Bar chart | Manhattan dominance (~90% of revenue) |
| Payment Type Table | Table | Cash tip data gap (Cash = $0 tips) |
| Payment Split | Pie chart | ~70% credit card, ~30% cash |
| Tips Comparison | Column chart | Misleading vs correct tip analysis |
| KPI Cards | Cards | Trip count, revenue, CC rate, airport trips |
| Borough Slicer | Slicer | Interactive filter for all visuals |

These 6 visuals tell the core story of the workshop: **the numbers are easy to compute (semantic layer), but easy to misinterpret without business context (ontology)**.

### 9.3: Use for Ontology Generation

When you create the Fabric Ontology (Step 05), you can choose **"Generate from Semantic Model"**:
1. Open `NYCTaxiSemanticModel`
2. In the ribbon, look for **Generate Ontology**
3. This auto-creates entity types from your model tables and relationships

---

## Summary: 23 DAX Measures Created

| Category | Measures |
|---|---|
| **Volume** (1) | Trip Count |
| **Revenue** (9) | Total Revenue, Total Fare, Total Tips, Avg Fare, Avg Tip, Avg Tip (CC Only), Avg Total, Total Amount, Tip Pct (CC Only) |
| **Distance** (2) | Avg Distance, Total Distance |
| **Passengers** (2) | Avg Passengers, Total Passengers |
| **Payment** (4) | Credit Card Trips, Cash Trips, Credit Card Rate, Pct With Tip |
| **Airport** (2) | Airport Trips, Airport Trip Rate |
| **Surcharges** (3) | Total Tolls, Total Congestion, Total Airport Fee |

This semantic model provides 23 reusable measures accessible through Power BI, reports, and the Fabric Ontology.

---

**Next: [Step 04 — The Ontology Gap →](04_the_ontology_gap.md)**
