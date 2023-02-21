#@title Install prerequisites
!apt install ffmpeg
!pip install setuptools-rust
!pip install git+https://github.com/openai/whisper.git

#@title Connect GDrive / Upload file
import os
source_file_in_gdrive = True #@param {type:"boolean"}
gdrive_path_and_filename = "/Whisper/file.mp4" #@param {type:"string"}
save_results_to_gdrive = True #@param {type:"boolean"}
if (source_file_in_gdrive or save_results_to_gdrive) and not os.path.exists("drive"):
  from google.colab import drive
  drive.mount('/drive')
  print("GDrive mounted successfully")
  !mkdir /content/drive/MyDrive/Whisper
if source_file_in_gdrive:
  file = "/content/drive/MyDrive" + gdrive_path_and_filename
  print("File path is: " + file)
if not source_file_in_gdrive:
  from google.colab import files
  files.upload()

  from os import listdir
  from os.path import isfile, join
  files = [file for file in listdir() if isfile(join("", file))]
  file = files[0]

  #@title Select Languages and Translation Engine
translation_needed = True #@param {type:"boolean"}
translated_language = 'en' #@param ["ja","en","auto"]
target_language = 'ru' #@param ["en","ru"]
translation_engine = 'yandex' #@param ["google","bing","reverso","deepl","yandex"]
seconds_between_requests = 5 #@param {type:"integer"}
if translation_needed:
    !pip install translators
    import translators
    def translate(string):
        return eval(("translators."+translation_engine)+"(string,from_language=translated_language,to_language=target_language,sleep_seconds=seconds_between_requests)")
  
!pip install goslate
import goslate
gs = goslate.Goslate()
def translate(string):
  return gs.translate(string, 'ru')

#@title Transcription settings
transcription_language = 'en' #@param ["en","ja"]
transcription_model = 'large' #@param ["tiny","base","small","medium","large"]
if (transcription_model in ["tiny","base","small","medium"]) and (transcription_language == 'en'):
  transcription_model = transcription_model + "." + transcription_language

!whisper {file} --model {transcription_model} --task transcribe --language {transcription_language}

with open(file+".srt") as subtitles_file:
    subtitles_lines = subtitles_file.readlines()

import re
import numpy
from tqdm import tqdm
translated_lines = subtitles_lines
continue_next = False
for counter in tqdm(range(2,(len(subtitles_lines)-1),4)):
  if continue_next:
    continue_next = False
    continue
  if not re.search("(\.\ |\.$|\.\n)", subtitles_lines[counter]):
    translated_lines[counter] = translate((subtitles_lines[counter] + subtitles_lines[counter+4]).replace('\n', ' ')) + '\n'
    translated_lines[counter+4] = subtitles_lines[counter]
    continue_next = True
  else:
    translated_lines[counter] = translate((subtitles_lines[counter] + subtitles_lines[counter+4]).replace('\n', ' ')) + '\n'
translated = open(file+".translated.srt", "w+")
for line in translated_lines:
  translated.write(line)
translated.close()

