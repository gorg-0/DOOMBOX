import os
import sys
import shutil
import gimpfu

input_dir_path = ""

def create_folder(dir):
    try: #GIMP raises OSError ignoring exist_ok
        os.makedirs(dir)
    except:
        pass

for file in os.listdir(input_dir_path):
    if file[-3:] == "dds":
        dds_input_path = input_dir_path + file
        dds_backup_dir = input_dir_path + "dds_backup\\"
        dds_backup_path = dds_backup_dir + file
        png_output_dir = input_dir_path + "png_export\\"
        png_output_path = png_output_dir + file[:-3] + "png"
        create_folder(png_output_dir)
        create_folder(dds_backup_dir)
        shutil.copy(dds_input_path, dds_backup_path)
        input_image = pdb.gimp_file_load(dds_input_path, dds_input_path, run_mode=gimpfu.RUN_NONINTERACTIVE)
        drawable_layer= input_image.active_layer
        pdb.plug_in_colors_channel_mixer(input_image, drawable_layer, 0, 0,0,1, 0,1,0, 1,0,0, run_mode=gimpfu.RUN_NONINTERACTIVE)
        pdb.file_png_save(input_image, drawable_layer, png_output_path, png_output_path, 0, 9, 1, 1, 1, 1, 1, run_mode=gimpfu.RUN_NONINTERACTIVE)
        pdb.file_dds_save(input_image, drawable_layer, dds_input_path, dds_input_path, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, run_mode=gimpfu.RUN_NONINTERACTIVE)