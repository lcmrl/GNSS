# >conda create --name pyproj_env
# >conda activate pyproj_env
# >conda install -c conda-forge pyproj
# >conda install -c conda-forge pymap3d
# >conda deactivate pyproj_env


from pyproj import Transformer
import pymap3d as pm

WORKING_DIR = r"G:\Shared drives\3DOM Research\PhD Luca\workflow\publications\2022\LowCost3D\2_FBK_GOPRO\VIDEO\OUTPUT_UBLOX"

INPUT_COORD_FILE = r"{}\rilievogiovedi.pos".format(WORKING_DIR)
OUTPUT_FILE_1 = r"{}\converted_LatLonAlt.txt".format(WORKING_DIR)
OUTPUT_FILE_2 = r"{}\converted_ENU.txt".format(WORKING_DIR)

input_system  = 'epsg:6704'
output_system = 'epsg:6706' #IGNF:ETRS89 epsg:4936 both of them are ECEF ETRS89
enu_reference_point = (4347718.9572, 856411.9883, 4573643.2406) # ECEF coordinates

### MAIN ###
transformer = Transformer.from_crs(input_system, output_system)
transform_object = transformer.itransform([(enu_reference_point[0], enu_reference_point[1], enu_reference_point[2])])
for pt in transform_object:
    enu_reference = (pt[0], pt[1], pt[2])
print("enu_reference", enu_reference)

c = 0
with open(INPUT_COORD_FILE, "r") as file:
    for line in file:
        if line[0] == "%":
            continue
        line = line.strip()
        day, hour, X, Y, Z, _ = line.split(None, 5)
        X = float(X)
        Y = float(Y)
        Z = float(Z)
        #print((X, Y, Z)) # Input coordinates

        transform_object = transformer.itransform([(X, Y, Z)])
        for pt in transform_object:
            #print(pt)
            Xc, Yc, Zc = pt[0], pt[1], pt[2]
            
            new_file = open(OUTPUT_FILE_1, "a")
            new_file.write("{} {} {} {} {}\n".format(day, hour, Xc, Yc, Zc))
            new_file.close()
            
            enuX, enuY, enuZ = pm.geodetic2enu(Xc, Yc, Zc, enu_reference[0], enu_reference[1], enu_reference[2])
            new_file = open(OUTPUT_FILE_2, "a")
            new_file.write("{} {} {} {} {}\n".format(day, hour, enuX, enuY, enuZ))
            new_file.close()
            print("Processed epoch: {}".format(c),end='\r')            
            c += 1
            #if c== 2: quit()



