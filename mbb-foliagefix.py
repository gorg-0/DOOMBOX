import os
import win32api
import shutil

def empty_input():
    try:
        input("Press Enter to continue...")
    except:
        pass

def create_folder(dir):
    try:
        os.makedirs(dir)
    except:
        pass

increase_foliage_draw_distance_times = 2
enable_smooth_lod = True

def edit_config(file_path):
    config = open(file_path, "r")
    data = config.read()
    config.close()
    if enable_smooth_lod:
        data = data.replace("<flag name=\"do_not_use_smooth_lod\" value=\"true\"/>", "<flag name=\"do_not_use_smooth_lod\" value=\"false\"/>")
    start = 0
    while data.find("view_distance=", start) != -1:
        start = data.find("view_distance=", start) + 1
        value_end = data.find(".", start)
        print("increased view distance value on char_n: " + str(start) + " from: " + str(int(data[start+14:value_end])) + " to: " + str(int(data[start+14:value_end])*increase_foliage_draw_distance_times))
        data = data[:start+14] + str(int(data[start+14:value_end])*increase_foliage_draw_distance_times) + data[value_end:]

    config_new = open(file_path, "w")
    config_new.writelines(data)
    config_new.close()

def find_bannerlord_foliage_config():
    steam_paths = ["Program Files (x86)\\Steam\\", "Steam Library\\", "SteamLibrary\\"]
    bannerlord_config_path = "steamapps\\common\\Mount & Blade II Bannerlord\\Modules\\Native\\ModuleData\\flora_kinds.xml"
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    for drive in drives:
        for path in steam_paths:
            if os.path.exists(drive+path+bannerlord_config_path):
                return True, drive+path+bannerlord_config_path
    return False, "nope"

def back_up_config_file(config_path):
    create_folder(os.path.expanduser("~\\Documents\\Mount and Blade II Bannerlord\\Foliage Config Backup\\"))
    shutil.copy(config_path, os.path.expanduser("~\\Documents\\Mount and Blade II Bannerlord\\Foliage Config Backup\\flora_kinds.xml"))
    print("foliage config was backed up -path:")
    print(os.path.expanduser("~\\Documents\\Mount and Blade II Bannerlord\\Foliage Config Backup\\flora_kinds.xml"))

if __name__ == '__main__':
    config_path_tuple = find_bannerlord_foliage_config()
    if config_path_tuple[0]:
        back_up_config_file(config_path_tuple[1])
        edit_config(config_path_tuple[1])
    else:
        print("steam folder not found")

    empty_input()