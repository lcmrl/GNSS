# >conda create --name pyproj_env
# >conda activate pyproj_env
# >conda install -c conda-forge pyproj
# >conda deactivate pyproj_env

import pymap3d as pm
from pyproj import Transformer

WORKING_DIR = r"./"

INPUT_COORD_FILE = r"{}/input.txt".format(WORKING_DIR)
OUTPUT_FILE_1 = r"{}/converted_LatLonAlt.txt".format(WORKING_DIR)
OUTPUT_FILE_2 = r"{}/converted_ENU.txt".format(WORKING_DIR)
file1 = open(OUTPUT_FILE_1, "w")
file2 = open(OUTPUT_FILE_2, "w")

input_system  = 'epsg:4978' # WGS84 geocentric 'epsg:4978'
output_system = 'epsg:4326' # WGS84 geographic 'epsg:4326'
enu_reference_point = (4347718.9572, 856411.9883, 4573643.2406) # ECEF coordinates of MOCA in WGS84 geocentric 'epsg:4978'

### MAIN ###
transformer = Transformer.from_crs(input_system, output_system)
transform_object = transformer.itransform([(enu_reference_point[0], enu_reference_point[1], enu_reference_point[2])])
for pt in transform_object:
    enu_reference = (pt[0], pt[1], pt[2])
    print("enu_reference", enu_reference)

c = 0
with open(INPUT_COORD_FILE, "r") as file:
    for line in file:
        line = line.strip()
        id, X, Y, Z = line.split(None, 4)
        X = float(X)
        Y = float(Y)
        Z = float(Z)

        transform_object = transformer.itransform([(X, Y, Z)])
        for pt in transform_object:
            Xc, Yc, Zc = pt[0], pt[1], pt[2]
            file1.write("{} {} {} {}\n".format(id, Xc, Yc, Zc))
        
        enuX, enuY, enuZ = pm.geodetic2enu(Xc, Yc, Zc, enu_reference[0], enu_reference[1], enu_reference[2])
        file2.write("{} {} {} {}\n".format(id, enuX, enuY, enuZ))