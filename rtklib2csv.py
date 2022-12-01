# >conda create --name pyproj_env
# >conda activate pyproj_env
# >conda install -c conda-forge pyproj
# >conda install -c conda-forge pymap3d
# >conda deactivate pyproj_env


INPUT_COORD_FILE = r".\buttare\outputLuca.txt"
OUTPUT_FILE_1 = r".\buttare\converted.txt"


### MAIN ###

c = 0
with open(INPUT_COORD_FILE, "r") as file:
    for line in file:
        if line[0] == "%":
            continue
        line = line.strip()
        day, hour, X1, X2, X3, Y1, Y2, Y3, Z, _ = line.split(None, 9)

        new_file = open(OUTPUT_FILE_1, "a")
        new_file.write("{},{},{} {} {},{} {} {},{}\n".format(day, hour, X1, X2, X3, Y1, Y2, Y3, Z))
        new_file.close()
        print("Processed epoch: {}".format(c),end='\r')            
        c += 1