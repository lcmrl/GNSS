import pymap3d as pm
from pyproj import Transformer

WORKING_DIR = "./"

INPUT_COORD_FILE = f"{WORKING_DIR}/input2.txt"
OUTPUT_FILE_1 = f"{WORKING_DIR}/converted_LatLonAlt.txt"
OUTPUT_FILE_2 = f"{WORKING_DIR}/converted_ENU.txt"

input_system  = "epsg:4978"   # ECEF WGS84
output_system = "epsg:4326"   # Geodetic WGS84

# Reference point in ECEF
enu_reference_point = (
    4347718.9572,
    856411.9883,
    4573643.2406
)

# IMPORTANT
transformer = Transformer.from_crs(
    input_system,
    output_system,
    always_xy=True
)

# Convert reference ECEF -> geodetic
lon0, lat0, h0 = transformer.transform(
    enu_reference_point[0],
    enu_reference_point[1],
    enu_reference_point[2]
)

print("Reference:")
print(lat0, lon0, h0)

with open(OUTPUT_FILE_1, "w") as file1, \
     open(OUTPUT_FILE_2, "w") as file2, \
     open(INPUT_COORD_FILE, "r") as infile:

    for line in infile:

        line = line.strip()

        if not line:
            continue

        id_, X, Y, Z, _, _, _, _, = line.split(" ", 7)

        X = float(X)
        Y = float(Y)
        Z = float(Z)

        # ECEF -> geodetic
        lon, lat, h = transformer.transform(X, Y, Z)

        file1.write(f"{id_} {lat} {lon} {h}\n")

        # geodetic -> ENU
        east, north, up = pm.geodetic2enu(
            lat,
            lon,
            h,
            lat0,
            lon0,
            h0
        )

        file2.write(f"{id_} {east} {north} {up}\n")

        print(lat, lon, h)