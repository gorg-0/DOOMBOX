import os
import shutil
import sys
import exif
import zipfile
import tarfile
import datetime
import time

cache_findings_dir = "D:\\cache findings\\"

def find_in_array(array, searched):
  for index in range(len(array)):
    if str(array[index]) == str(searched):
      return index
  return -1

def create_dir(path):
  try:
    os.makedirs(path)
  except:
    pass

def embedded_question_mark(byte_array):
  counter = 0
  for signature in compressed_sigs:
    if signature in byte_array:
      counter = counter + 1
  return counter

firefox_cache_meta_start = b'\x4F\x5E\x70\x61\x72\x74\x69\x74\x69\x6F\x6E\x4B\x65\x79' #O^partitionKey

end_signature_png = b'\x49\x45\x4E\x44\xAE\x42\x60\x82'
end_signature_jpg_spiff = b'\xFF\xE8'
end_signature_jpg_exif = b'\xFF\xE1' #start actually
end_signature_jpg_jpeg = b'\xFF\xE0'
end_signature_jpeg_cannon = b'\xFF\xE2'
end_signature_jpeg_samsung = b'\xFF\xE3'

image_end_signatures = [end_signature_png,end_signature_jpg_spiff,end_signature_jpg_exif,end_signature_jpg_jpeg,end_signature_jpeg_cannon,end_signature_jpeg_samsung]

misc_zip_signature = b'\x50\x4B'
win_zip_signature = b'\x57\x69\x6E\x5A\x69\x70'
tar_signature = b'\x75\x73\x74\x61\x72'
tar_lzw_signature = b'\x1F\x9D'
tar_lzh_signature = b'\x1F\xA0'
bz2_signature = b'\x42\x5A\x68'
lzip_signature = b'\x4C\x5A\x49\x50'
rar_signature = b'\x52\x61\x72\x21\x1A\x07'
seven_z_signature = b'\x37\x7A\xBC\xAF\x27\x1C'
gzip_signature = b'\x1F\x8B'
quick_zip_signature = b'\x52\x53\x56\x4B\x44\x41\x54\x41'

compressed_sigs = [misc_zip_signature, win_zip_signature, tar_signature, tar_lzw_signature, tar_lzh_signature, bz2_signature, lzip_signature, rar_signature, seven_z_signature, gzip_signature, quick_zip_signature]

def firefox_cache_dir():
  firefox_profiles = "~\\AppData\\Local\\Mozilla\\Firefox\\Profiles"
  partial_path = os.path.expanduser(firefox_profiles)
  for dir in os.listdir(os.path.expanduser(firefox_profiles)):
    if dir.find("default-release")+1:
      cache_path = partial_path + "\\" + dir + "\\cache2\\entries\\"
      return(cache_path)
  print("firefox cache dir not found")
  sys.exit()

def check_dir(path):
  hashes_temp = open(cache_findings_dir + "hashes", "a")
  hashes_temp.writelines(str(datetime.date.today()) + "\n")
  hashes_temp.close()
  exif_meta = []
  hash_file = open(cache_findings_dir + "hashes", "rb").read()
  for file in os.listdir(path):
    if str(hash(file)) in str(hash_file):
      continue
    else:
      hashes = open(cache_findings_dir + "hashes", "a")
      hashes.write(str(hash(file))+"\n")
      hashes.close()
    cache_file_path = path + file
    if os.path.isfile(cache_file_path):
      cache_file = open(cache_file_path,"rb").read()
      byte_array = bytearray(cache_file)
      firefox_meta_only = byte_array[byte_array.find(firefox_cache_meta_start):]
      no_firefox_meta = byte_array[:byte_array.find(firefox_cache_meta_start)]
      if str(firefox_meta_only).find("image/jpeg") != -1 or str(firefox_meta_only).find("image/png") != -1:
        if embedded_question_mark(no_firefox_meta) != -1:
          if zipfile.is_zipfile(cache_file_path) or tarfile.is_tarfile(cache_file_path):
            shutil.copy(cache_file_path, cache_findings_dir + "EMBEDDED-" + file)
          else:
            #shutil.copy(cache_file_path, cache_findings_dir + "MAYBE-EMBEDDED-" + file)
            pass
        try:
          exif_meta = exif.Image(cache_file).list_all()
        except:
          pass
        if find_in_array(exif_meta, "gps_latitude") != -1:
          shutil.copy(cache_file_path, cache_findings_dir + "GPS-"+file)


create_dir(cache_findings_dir)

while True:
  check_dir(firefox_cache_dir())
  time.sleep(1)