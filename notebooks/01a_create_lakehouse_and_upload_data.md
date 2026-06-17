# Step 01a: Create the Lakehouse and Upload NYC Taxi Data (UI Guide)

**Duration: 20 minutes | Type: Hands-on (Fabric UI)**

---

## Overview

This guide walks you through creating the `NYCTaxiLakehouse` in Microsoft Fabric and uploading the NYC Yellow Taxi dataset — entirely through the Fabric UI. No code required for this step.

By the end you will have:
- A Fabric Lakehouse named `NYCTaxiLakehouse`
- The raw Parquet file for January 2024 trips (~2.76M rows)
- The taxi zone lookup CSV file
- Both files uploaded and ready to be loaded into Delta tables

---

## Part 1: Download the NYC Taxi Data to Your Computer

Before working in Fabric, download these files to your local machine.

### 1.1: Download the Trip Data (Parquet)

1. Open your browser and navigate to the NYC TLC Trip Record Data page:
   **https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page**

2. Scroll down to the **Yellow Taxi Trip Records** section

3. Find **January 2024** and click the download link for the Parquet file
   - The file is named: `yellow_tripdata_2024-01.parquet`
   - Size: approximately 45 MB
   - Direct link: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet`

4. Save it to a folder you can easily find (e.g., `C:\Downloads\nyc-taxi\`)

### 1.2: Download the Zone Lookup (CSV)

1. On the same NYC TLC page, scroll to find **Taxi Zone Lookup Table**

2. Download the CSV file
   - The file is named: `taxi_zone_lookup.csv` (or `taxi+_zone_lookup.csv`)
   - Direct link: `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv`
   - Size: approximately 12 KB (265 rows)

3. Save it to the same folder

### 1.3: Verify Your Downloads

You should now have two files:

```
C:\Downloads\nyc-taxi\
  ├── yellow_tripdata_2024-01.parquet   (~45 MB)
  └── taxi_zone_lookup.csv              (~12 KB)
```

---

## Part 2: Create the Fabric Workspace (If Needed)

If you already have a Fabric workspace, skip to Part 3.

### 2.1: Navigate to Microsoft Fabric

1. Open your browser and go to: **https://app.fabric.microsoft.com**
2. Sign in with your Microsoft account that has Fabric access

### 2.2: Create a New Workspace

1. In the left navigation panel, click **Workspaces**
2. Click **+ New workspace** at the bottom of the workspaces list
3. Fill in the details:
   - **Name**: `FabricIQMiniHack` (or any name you prefer)
   - **Description**: `Fabric IQ Mini Hack workspace`
4. Expand **Advanced** settings:
   - **License mode**: Select your Fabric-enabled capacity (Trial, Premium, or Fabric capacity)
   - If you don't see a Fabric capacity, contact your Fabric administrator
5. Click **Apply**

You'll be taken to your new empty workspace.

---

## Part 3: Create the Lakehouse

### 3.1: Create the Lakehouse Item

1. In your workspace, click the **+ New item** button (top left area, or center of the page if workspace is empty)

2. In the "New item" dialog, you'll see categories on the left. Click **Data Engineering**

3. Find and click **Lakehouse**

4. In the Name dialog:
   - **Name**: `NYCTaxiLakehouse`
   - (Names can contain letters, numbers, underscores, and spaces)

5. Click **Create**

### 3.2: Understand the Lakehouse UI

After creation, you'll see the Lakehouse explorer. Here's what you're looking at:

```
NYCTaxiLakehouse
├── Tables/          ← Delta tables go here (we'll create these in Step 01)
│   └── (empty)
├── Files/           ← Raw files go here (we'll upload here next)
│   └── (empty)
└── (Lakehouse metadata shown in the center panel)
```

**Key areas of the Lakehouse UI:**

| UI Element | Location | Purpose |
|---|---|---|
| **Explorer panel** | Left side | Browse Tables/ and Files/ folders |
| **Tables** folder | Left panel, top | Contains Delta tables (queryable via SQL/Spark) |
| **Files** folder | Left panel, below Tables | Contains raw files (Parquet, CSV, JSON, etc.) |
| **Home ribbon** | Top | Actions like "Get data", "New notebook", "New SQL query" |
| **Lakehouse name** | Top center | Shows which Lakehouse you're in |
| **SQL analytics endpoint** | Top right toggle | Switch to SQL query view |

---

## Part 4: Upload Data Files to the Lakehouse

### 4.1: Upload the Parquet File

1. In the Lakehouse explorer (left panel), click on the **Files** folder to select it

2. In the top ribbon, click **Upload** → **Upload files**
   - Alternatively: right-click on the **Files** folder → **Upload** → **Upload files**

3. A file browser dialog opens:
   - Navigate to where you saved the downloads (e.g., `C:\Downloads\nyc-taxi\`)
   - Select **`yellow_tripdata_2024-01.parquet`**
   - Click **Open**

4. Wait for the upload to complete. You'll see a progress indicator.
   - The 45 MB file typically takes 30-60 seconds depending on your connection.
   - A green checkmark or notification confirms the upload.

5. Verify: Click on the **Files** folder in the explorer. You should see:
   ```
   Files/
   └── yellow_tripdata_2024-01.parquet
   ```

### 4.2: Upload the CSV File

1. With the **Files** folder still selected, click **Upload** → **Upload files** again

2. Select **`taxi_zone_lookup.csv`** and click **Open**

3. Wait for upload (this is tiny, should be instant)

4. Verify: The Files folder should now show:
   ```
   Files/
   ├── yellow_tripdata_2024-01.parquet
   └── taxi_zone_lookup.csv
   ```

### 4.3: Preview the Uploaded Files (Optional)

You can preview files directly in the Lakehouse:

1. Click on `taxi_zone_lookup.csv` in the Files folder
2. The center panel will show a preview of the CSV data
3. You should see columns: `LocationID`, `Borough`, `Zone`, `service_zone`
4. There should be 265 rows (plus header)

---

## Part 5: Load Files into Delta Tables (UI Method)

While Step 01 (`01_data_foundation.py`) does this programmatically with a notebook, you can also load files to tables via the UI.

### 5.1: Load the CSV to a Table (UI method)

1. In the **Files** folder, right-click on `taxi_zone_lookup.csv`
2. Select **Load to Tables** → **New table**
3. In the dialog:
   - **Table name**: `zones`
   - **Header**: First row is header (should be auto-detected)
   - Click **Load**
4. Wait for the loading to complete (a few seconds for this small file)
5. Check the **Tables** folder — you should see a `zones` table appear

### 5.2: Load the Parquet to a Table (UI method)

1. Right-click on `yellow_tripdata_2024-01.parquet`
2. Select **Load to Tables** → **New table**
3. In the dialog:
   - **Table name**: `trips`
   - Click **Load**
4. Wait for loading (~1-3 minutes for the 2.76M row file)
5. Check the **Tables** folder — you should see a `trips` table

> **Note**: When loading via UI, column names keep their original casing (e.g., `VendorID` instead of `vendor_id`). The notebook in Step 01 renames columns to our standard lowercase convention. If you use the UI method, you'll need to run the renaming cells from Step 01 afterward.

### 5.3: Why We Recommend the Notebook Method

The UI "Load to Tables" is convenient but limited:
- It doesn't rename columns
- It doesn't filter invalid records
- It doesn't create the reference tables (payment_types, rate_codes)

**Recommended approach**: Use the UI to upload files (Parts 4.1 and 4.2), then run the notebook in Step 01 to create properly cleaned and named tables.

---

## Part 6: Create and Run a Notebook (for Step 01)

If you've never used a Fabric notebook before, here's how:

### 6.1: Create a New Notebook

1. With `NYCTaxiLakehouse` open, click **Open notebook** in the top ribbon
   - Or: click **+ New item** → **Notebook**

2. The notebook editor opens. It looks like Jupyter notebooks:
   - **Cells**: Rectangular boxes where you write code
   - **Run button** (▶): Executes the current cell
   - **+ Code / + Markdown**: Adds new cells
   - **Language selector**: Should show **PySpark (Python)** — this is the default

### 6.2: Attach the Lakehouse

If you created the notebook from within the Lakehouse, it should already be attached. If not:

1. In the left panel of the notebook, look for **Lakehouses**
2. Click **Add** → **Existing lakehouse**
3. Select `NYCTaxiLakehouse` and click **Add**
4. You should see the Lakehouse appear in the left panel with its Tables/ and Files/ folders

### 6.3: Copy and Run Code from Step 01

1. Open the file `01_data_foundation.py` from this workshop
2. Copy each cell's code (between the `# %%` markers) into separate notebook cells
3. Run cells sequentially by clicking the **▶ Run** button on each cell
4. Wait for each cell to complete before running the next

**What each cell does:**

| Cell | What It Does | Expected Output |
|---|---|---|
| Cell 1 | Creates `payment_types` (6 rows) and `rate_codes` (6 rows) | "Created payment_types: 6 rows" |
| Cell 2 | Loads `taxi_zone_lookup.csv` → `zones` table (265 rows) | Table preview showing LocationID, Borough, Zone |
| Cell 3 | Reads the raw Parquet file | "Raw records: 2,964,624" (approximately) |
| Cell 4 | Renames columns to lowercase convention | No output (transformation only) |
| Cell 5 | Filters invalid records | "Records after cleaning: 2,764,118" (approximately) |
| Cell 6 | Writes to `trips` Delta table | "Created trips table!" |
| Cell 7 | Verifies all 4 tables | Row counts for each table |
| Cell 8 | Revenue by borough query | Table showing Manhattan, Queens, Brooklyn, etc. |
| Cell 9 | Payment type analysis | Shows the critical cash tip data gap |

### 6.4: Verify Tables in the Lakehouse UI

After running all cells:

1. Go back to your Lakehouse (click `NYCTaxiLakehouse` in the left panel or use breadcrumbs)
2. Click **Refresh** (circular arrow icon) above the explorer panel
3. The **Tables** folder should now show:

```
Tables/
├── trips           (~2.76M rows)
├── zones           (265 rows)
├── payment_types   (6 rows)
└── rate_codes      (6 rows)
```

4. Click on any table to preview its data in the center panel
5. The table preview shows:
   - Column names and types
   - First rows of data
   - Row count

---

## Part 7: Verify with a SQL Query (Optional)

You can run SQL queries directly in the Lakehouse:

### 7.1: Open the SQL Endpoint

1. In the top right of the Lakehouse view, find the view toggle
2. Click **SQL analytics endpoint** (or look for the SQL icon)
3. This switches to a SQL query interface

### 7.2: Run a Verification Query

1. Click **New SQL query** in the top ribbon
2. Paste this query:

```sql
-- Verify all tables
SELECT 'trips' as table_name, COUNT(*) as row_count FROM trips
UNION ALL
SELECT 'zones', COUNT(*) FROM zones
UNION ALL
SELECT 'payment_types', COUNT(*) FROM payment_types
UNION ALL
SELECT 'rate_codes', COUNT(*) FROM rate_codes
ORDER BY table_name;
```

3. Click **▶ Run** (or press F5)
4. Expected results:

| table_name    | row_count |
|---            |---        |
| payment_types | 6         |
| rate_codes    | 6         |
| trips         | ~2,764,118|
| zones         | 265       |
---

## Troubleshooting

### "I don't see the Lakehouse option"
- Your workspace may not have Fabric capacity. Check workspace settings → License mode.
- Contact your Fabric administrator to enable Fabric capacity.

### "Upload is very slow"
- The Parquet file is ~45 MB. On slow connections it may take several minutes.
- Consider using the Fabric notebook to download directly (see alternative below).

### "Load to Tables fails"
- Ensure the file uploaded completely (check file size matches)
- Try refreshing the Lakehouse explorer
- Use the notebook method (Step 01) instead — it's more reliable

### "Notebook won't run / Spark session fails"
- Ensure the Lakehouse is attached to the notebook (left panel → Lakehouses)
- Wait for the Spark session to start (first cell may take 30-60 seconds)
- Check that your workspace has active Fabric capacity

### Alternative: Download Data Directly in a Notebook

If you prefer to skip the manual download, you can download the data directly in a Fabric notebook:

```python
# Cell 1: Download the data files directly to the Lakehouse
import urllib.request

# Download trip data (Parquet, ~45 MB)
print("Downloading trip data...")
urllib.request.urlretrieve(
    "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet",
    "/lakehouse/default/Files/yellow_tripdata_2024-01.parquet"
)
print("Trip data downloaded!")

# Download zone lookup (CSV, ~12 KB)
print("Downloading zone lookup...")
urllib.request.urlretrieve(
    "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv",
    "/lakehouse/default/Files/taxi_zone_lookup.csv"
)
print("Zone lookup downloaded!")
```

> **Note**: This downloads directly to the Lakehouse's Files/ folder, skipping the manual upload. Then proceed with Step 01 notebook cells to load into Delta tables.

---

## Summary

After completing this step, your Fabric workspace contains:

```
FabricIQMiniHack (Workspace)
└── NYCTaxiLakehouse (Lakehouse)
    ├── Tables/
    │   ├── trips           (2.76M rows, 19 columns)
    │   ├── zones           (265 rows, 4 columns)
    │   ├── payment_types   (6 rows, 2 columns)
    │   └── rate_codes      (6 rows, 2 columns)
    └── Files/
        ├── yellow_tripdata_2024-01.parquet
        └── taxi_zone_lookup.csv
```

---

**Next: [Step 01 — Data Foundation (Notebook) →](01_data_foundation.py) or [Step 02 — Technical Layer →](02_technical_layer.py)**
