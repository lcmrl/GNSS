import os
import math

DELAY=16#18 # in seconds
DELAY_HOUR = 2
SYNCR = "GoPro_time" # "GPS_time" or "GoPro_time"
IMG_DIR = r"G:\Shared drives\3DOM Research\PhD Luca\workflow\publications\2022\LowCost3D\2_FBK_GOPRO\RAPID-STATIC\imgs"
EXIF_DIR = r"G:\Shared drives\3DOM Research\PhD Luca\workflow\publications\2022\LowCost3D\2_FBK_GOPRO\RAPID-STATIC\exif_data"
ENU_coordinates_file = r"G:\Shared drives\3DOM Research\PhD Luca\workflow\publications\2022\LowCost3D\2_FBK_GOPRO\RAPID-STATIC\with_atx_for_CORS\OUTPUT\converted_ENU.txt"


def TimeCorrectFormat(value):
    if value < 10:
        string_value = "0"+"{}".format(value)
    elif value >= 10:
        string_value = "{}".format(value)
    return string_value

### MAIN ###
imgs = os.listdir(IMG_DIR)
GNSS_solution_dict = {}
data_sync = {}

with open(ENU_coordinates_file, 'r') as ENU_file:
    lines = ENU_file.readlines()
    for line in lines:
        line = line.strip()
        day, hour, X, Y, Z = line.split(" ", 4)
        GNSS_solution_dict[hour] = (X, Y, Z)

for img in imgs[0:]:
    print("\n\n\n", img)

    with open("{}/{}".format(EXIF_DIR, img[:-3]+"txt"), 'r') as exif_file:
        lines = exif_file.readlines()
        line = line.strip()

        for line in lines:
            if SYNCR == "GPS_time" and line[0:13] == "GPS Date/Time":
                date, hour = line[-21:].split(" ", 1)
                h, m, s = hour[:-2].split(":", 2)
                break
            elif SYNCR == "GoPro_time" and line[0:13] == "Create Date  ":
                date, hour = line[-20:].split(" ", 1)
                h, m, s = hour[:-1].split(":", 2)
                h = TimeCorrectFormat(int(h) - DELAY_HOUR)
                print(h, m, s)
                break

        hour_string, min_string, sec_string = h, m, s
        if int(s)+DELAY >= 60:
            dec, integer = math.modf((int(s)+DELAY)/60)
            delta_min = int(integer)
            delta_sec = round(dec * 60)
            sec_string = TimeCorrectFormat(delta_sec)
            if int(m)+delta_min < 60:
                min_string = TimeCorrectFormat(int(m)+delta_min)  
            elif int(m)+delta_min >= 60:
                dec, integer = math.modf((int(m)+delta_min)/60)
                delta_hour = int(integer)
                delta_min = round(dec * 60)
                hour_string = TimeCorrectFormat(int(h)+delta_hour)
                min_string = TimeCorrectFormat(delta_min)
        
        elif int(s)+DELAY < 60:
            delta_sec = DELAY
            sec_string = TimeCorrectFormat(int(s)+delta_sec)  
        for epoch in GNSS_solution_dict:
            if epoch == "{}:{}:{}.000".format(hour_string, min_string, sec_string):
                data_sync[img] = (epoch, GNSS_solution_dict[epoch])
        print("{}:{}:{}.000".format(hour_string, min_string, sec_string))


with open("./out.txt", 'w') as out_file:
    for img in data_sync:
        out_file.write("{},{},{},{},{}\n".format(img, data_sync[img][0], data_sync[img][1][0], data_sync[img][1][1], data_sync[img][1][2]))