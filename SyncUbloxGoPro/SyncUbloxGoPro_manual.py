import os
import shutil

#line_initial_epoch_in_ENU_file = 497 - 1 #494 - 1
#INITIAL_IMG = 166-17 #72 #-13 e -17
#STEP = 30 #30
#IMGS_ID = range(INITIAL_IMG, 1220, STEP); #print([k for k in IMGS_ID]); quit()
#IMG_DIR = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\calibration\imgs"
#OUT_DIR = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\calibration\prova"
#ENU_coordinates_file = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\converted_ENU.txt"

line_initial_epoch_in_ENU_file = 497 - 1 #494 - 1
INITIAL_IMG = 166-17 #72 #-13 e -17
STEP = 30 #30
IMGS_ID = range(INITIAL_IMG, 1220, STEP); #print([k for k in IMGS_ID]); quit()
IMG_DIR = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\calibration\imgs"
OUT_DIR = r"C:\Users\Luscias\Desktop\3DOM\Github_3DOM\GNSS\SyncUbloxGoPro\imgs"
ENU_coordinates_file = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\converted_ENU.txt"

def numerical_id(string, n_of_remov_final_char=4):
    string = string[:-n_of_remov_final_char]
    value = int(string)
    return value

### MAIN ###
GNSS_solution_dict = {}
imgs = os.listdir(IMG_DIR)
imgs.sort(key=numerical_id)
#print(imgs);quit()

with open(ENU_coordinates_file, 'r') as ENU_file:
    lines = ENU_file.readlines()
    for l, line in enumerate(lines):
        line = line.strip()
        day, hour, X, Y, Z = line.split(" ", 4)
        GNSS_solution_dict[l] = (hour, X, Y, Z)

with open(f"{OUT_DIR}/out.txt", 'w') as out_file:
    for count, i in enumerate(IMGS_ID):
        shutil.copy(rf"{IMG_DIR}/{imgs[i]}", rf"{OUT_DIR}/imgs/{imgs[i]}")
        s = line_initial_epoch_in_ENU_file + count
        out_file.write("{},{},{},{},{}\n".format(imgs[i],  GNSS_solution_dict[s][0], GNSS_solution_dict[s][1], GNSS_solution_dict[s][2], GNSS_solution_dict[s][3]))

        