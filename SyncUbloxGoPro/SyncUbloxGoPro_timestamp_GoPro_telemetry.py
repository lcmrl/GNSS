import os
import math
import shutil

FIRST_FRAME = 10 # 0
FRAME_INTERVAL = 30 # 18
IMG_RANGE = range(FIRST_FRAME, 1000, FRAME_INTERVAL)
DELAY= 16 # 16 # in seconds
DELAY_HOUR = 0
SYNCR = "GoPro_time" # "GPS_time" or "GoPro_time"
IMG_DIR = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\calibration\imgs"
TELEMETRY_FILE = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\GH016537_HERO9 Black-GPS5.csv"
ENU_coordinates_file = r"C:\Users\Luscias\Desktop\provvisorio\provvisorio4\converted_ENU.txt"
img_out_folder = r"C:\Users\Luscias\Desktop\3DOM\Github_3DOM\GNSS\SyncUbloxGoPro\imgs"


def TimeCorrectFormat(value):
    if value < 10:
        string_value = "0"+"{}".format(value)
    elif value >= 10:
        string_value = "{}".format(value)
    return string_value

def add_delay(hGps, mGps, sGps, DELAY):
    if sGps + DELAY >= 60:
        dec, integer = math.modf((sGps + DELAY)/60)
        delta_min = int(integer)
        delta_sec = round(dec * 60)
        sGps = delta_sec

        if mGps + delta_min < 60:
            mGps = mGps + delta_min

        elif mGps + delta_min >= 60:
            dec, integer = math.modf((mGps + delta_min)/60)
            delta_hour = int(integer)
            delta_min = round(dec * 60)
            hGps = hGps + delta_hour
            mGps = delta_min
    
    elif sGps + DELAY < 60:
        sGps = sGps + DELAY

    return hGps, mGps, sGps

### MAIN ###
imgs = [f"{k}.jpg" for k in IMG_RANGE]
GNSS_solution_dict = {}
data_sync = {}
telemetry_list = []
img_id_dict = {}

with open(ENU_coordinates_file, 'r') as ENU_file:
    lines = ENU_file.readlines()
    for line in lines:
        line = line.strip()
        day, hour, X, Y, Z = line.split(" ", 4)
        GNSS_solution_dict[hour] = (X, Y, Z)

with open("{}".format(TELEMETRY_FILE), 'r') as exif_file:
    lines = exif_file.readlines()
    for line in lines[1:]:
        line = line.strip()
        int_time, GPS_time, _ = line.split(',', 2)
        int_time, GPS_time = int_time.replace('"',''), GPS_time.replace('"','')
        int_time = float(int_time)
        GPS_time = GPS_time.replace('Z','')
        _, GPS_time = GPS_time.split("T", 1)
        hGps, mGps, sGps = GPS_time.split(":", 2)
        hGps, mGps, sGps = int(hGps), int(mGps), float(sGps)
        hGps, mGps, sGps = add_delay(hGps, mGps, sGps, DELAY)
        telemetry_list.append((int_time, hGps, mGps, sGps))

for i, img in enumerate(imgs):
    img_id_dict[img] = i*FRAME_INTERVAL

for img in imgs:
    img_id = img_id_dict[img]
    hGps, mGps, sGps = telemetry_list[img_id][1], telemetry_list[img_id][2], telemetry_list[img_id][3]
    epoch = "{}:{}:{}.000".format(TimeCorrectFormat(hGps), TimeCorrectFormat(mGps), TimeCorrectFormat(round(sGps)))
    print(epoch)
    for hour in GNSS_solution_dict.keys():
        if hour == epoch:
            data_sync[img] = (epoch, GNSS_solution_dict[epoch])
            print(data_sync[img])

name_images = {}
for img in imgs:
    id = int(img[:-4])
    code =f"{id}.jpg"; name_images[img] = code
    #if id < 10: code =f"parte1_0000{id}.jpg"; name_images[img] = code
    #elif id < 100 and id >= 10: code =f"parte1_000{id}.jpg"; name_images[img] = code
    #elif id < 1000 and id >= 100: code =f"parte1_00{id}.jpg"; name_images[img] = code
    #elif id < 10000 and id >= 1000: code =f"parte1_0{id}.jpg"; name_images[img] = code
    #elif id < 100000 and id >= 10000: code =f"parte1_{id}.jpg"; name_images[img] = code

with open("./out.txt", 'w') as out_file:
    for img in data_sync:
        out_file.write("{},{},{},{},{}\n".format(name_images[img], data_sync[img][0], data_sync[img][1][0], data_sync[img][1][1], data_sync[img][1][2]))

for img in imgs:
    shutil.copyfile(rf"{IMG_DIR}/{img}", rf"{img_out_folder}/{img}")