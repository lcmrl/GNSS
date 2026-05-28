"""
convert_ecef_to_utm32n.py
--------------------------
Converts ECEF (X, Y, Z) coordinates to ETRS89 / UTM Zone 32N (EPSG:25832),
matching the coordinate system used in Cloud.csv (Easting, Northing, Elevation).

Usage:
    python convert_ecef_to_utm32n.py <input_file.csv>

Input format (CSV or TXT, comma-separated):
    label, x-ecef(m), y-ecef(m), z-ecef(m)
    point 1, 4349527.3166, 857347.6372, 4570763.3568
    ...

Output:
    <input_file>_utm32n.csv  →  label, Easting (m), Northing (m), Elevation (m)
"""

import pandas as pd
from pyproj import Transformer
import sys
import os

# ── Input file ────────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print("Usage: python convert_ecef_to_utm32n.py <input_file.csv>")
    sys.exit(1)

input_file = sys.argv[1]

if not os.path.exists(input_file):
    print(f"❌ File not found: {input_file}")
    sys.exit(1)

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(input_file, skipinitialspace=True)
df.columns = df.columns.str.strip()

# Drop any unnamed/empty trailing columns
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

print(f"✅ Loaded {len(df)} points from: {input_file}")
print(f"   Columns: {list(df.columns)}\n")

# ── Transformers ──────────────────────────────────────────────────────────────
# Step 1: ECEF (geocentric) → WGS84 geographic (lon, lat, h)
ecef_to_geo = Transformer.from_crs("EPSG:4978", "EPSG:4979", always_xy=True)

# Step 2: WGS84 geographic → ETRS89 / UTM Zone 32N  ← matches Cloud.csv
geo_to_utm = Transformer.from_crs("EPSG:4979", "EPSG:25832", always_xy=True)

# ── Step 1: ECEF → geodetic ───────────────────────────────────────────────────
lon, lat, h = ecef_to_geo.transform(
    df["x-ecef(m)"].values,
    df["y-ecef(m)"].values,
    df["z-ecef(m)"].values
)

# ── Step 2: geodetic → UTM 32N ────────────────────────────────────────────────
easting, northing, elevation = geo_to_utm.transform(lon, lat, h)

df["Easting (m)"]   = easting
df["Northing (m)"]  = northing
df["Elevation (m)"] = elevation

# ── Display ───────────────────────────────────────────────────────────────────
print("Converted coordinates (ETRS89 / UTM Zone 32N — EPSG:25832):")
print(df[["label", "Easting (m)", "Northing (m)", "Elevation (m)"]].to_string(index=False))

# ── Save ──────────────────────────────────────────────────────────────────────
base = os.path.splitext(os.path.basename(input_file))[0]
ext = os.path.splitext(input_file)[1]
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{base}_utm32n{ext}")

out_df = df[["label", "Easting (m)", "Northing (m)", "Elevation (m)"]]
out_df.to_csv(output_file, index=False, float_format="%.6f")
print(f"\n✅ Saved to: {output_file}")
