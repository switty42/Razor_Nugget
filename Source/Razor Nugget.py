# Project: Razor_Nugget - test GPT's ability to do QA on Razorback Nuggets from Tyson Foods
# Author - Stephen Witty switty@level500.com
# Started 11-10-24
# Description - ask GPT to grade a series of razorback nugget photos from 1 to 100 in quality
# Example used from openai for vision gpt
# To run:
#     tested on ubuntu
#     install ImageMagic to gain access to the "convert" command
#     install Python package numpy
#
# V1 11-10-24   Initial development

import random
import time
import os
import sys
import base64
import requests
import subprocess
import re
import numpy as np
import shutil

# OpenAI API Key
api_key = "XXXXXXXXXXXXXXXXXXXXX"
model = "gpt-4o"

##################### Constants ###########################################################################################
VERSION = 1                                                       # Version of program
TEST_PER_IMAGE = 10                                               # Number of times to run the test per image
MAX_IMAGES = 99                                                   # Maximum number of images to test
PIC_DIR = "/home/switty/Dev/Razor_Nugget/pics"                    # Picture directory  location fully pathed, do not include / on end
PERFECT_PIC = "/home/switty/Dev/Razor_Nugget/Perfect.jpg"         # Reference image
TEMP_PIC = "/home/switty/Dev/Razor_Nugget/RZN.jpg"                # Temp pic to submit after building
LOG_FILE = "/home/switty/Dev/Razor_Nugget/RZN.log"                # Log for results
OUTPUT_PICS = "/home/switty/Dev/Razor_Nugget/output_pics"         # Directory for output pics
LOG_GPT_ANSWER = "/home/switty/Dev/Razor_Nugget/GPT_Answer.log"   # Log GPT answers
DELAY = .5                                                        # Delay time per test run to display results in seconds
MAX_ERRORS = 30                                                   # Max number of GPT errors per test before exit
###########################################################################################################################

PROMPT = "You are a quality control engineer working for Tyson Foods.  \
 You are monitoring a chicken nugget production line producing chicken nuggets in the shape of razorbacks. \
 In the included picture, the left hand image is the picture of the product from the packaging. \
 The right hand image is a sample nugget from the production line.  \
On a scale from 0 to 100, where 100 is perfect, how would you grade this sample image as a razorback nugget?  \
Place the answer between two braces, for instance, if the answer is 75 then the reply should include {75}.  \
Provide back an answer even if it is only your best estimate.  \
If the right image is not a razorback nugget, grade it based on the resemblance to a razorback nugget or razorback nugget qualities."

# Function to encode the image
def encode_image(image_path):
   with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')

# Function to write to a file
def log(text,file_name):
    # Open the file in append mode, creating it if it doesn't exist
    with open(file_name, 'a') as file:
        file.write(text + '\n')  # Append the text and add a newline

print("Razor Nugget Starting, Version: " + str(VERSION))
print("Tests per image: " + str(TEST_PER_IMAGE))
print("Max images to test: " + str(MAX_IMAGES))
print("Picture directory: " + PIC_DIR)
print("Reference picture: " + PERFECT_PIC)
print("Temp pic: " + TEMP_PIC)
print("Log file: " + LOG_FILE)
print("Output pics directory: " + OUTPUT_PICS)
print("GPT answer log: " + LOG_GPT_ANSWER)
print("Delay for results: " + str(DELAY))
print("PROMPT: " + PROMPT)

try:
   filenames_with_path = []  # Store picture names with full path
   filenames_no_path = []    # Store picture names with only the file name
   for entry in os.listdir(PIC_DIR):
      full_path = os.path.join(PIC_DIR,entry)
      if (os.path.isfile(full_path) and (entry.endswith('.JPG') or entry.endswith('.jpg'))):
         filenames_with_path.append(full_path)
         filenames_no_path.append(entry)

except Exception as e:
      print("Error occurred reading pictures: " + str(e))
      print("Exiting")
      os.sys.exit(1)

if (len(filenames_no_path) == 0):
   print("Error no pictures found")
   print("Exiting")
   os.sys.exit(1)

# Put files in order just to make the print out better
filenames_with_path.sort()
filenames_no_path.sort()

print("List of source pictures, total: ",len(filenames_no_path))
print("--------------------------------")
for entry in filenames_with_path:
   print(entry)
print("----------------------------")
for entry in filenames_no_path:
   print(entry)

os.system("rm -f " + LOG_FILE)
if (os.path.exists(LOG_FILE)):
   print("ERROR log file did not delete")
   os.system.exti(1)

os.system("rm -f " + LOG_GPT_ANSWER)
if (os.path.exists(LOG_GPT_ANSWER)):
   print("ERROR GPT answer log did not delete")
   os.system.exti(1)

if (os.path.exists(OUTPUT_PICS)):
   shutil.rmtree(OUTPUT_PICS)

os.makedirs(OUTPUT_PICS)

###################### Main loop #####################################################
index = 0

while (index < MAX_IMAGES and index < len(filenames_with_path)):

   test_number = 0
   web_api_error = 0
   no_answer = 0
   results = []

   while(test_number < TEST_PER_IMAGE):
      if (index > 0 or test_number > 0):
         time.sleep(DELAY)
         process.terminate() # This closes the picture display program that is started later

      if (no_answer == MAX_ERRORS or web_api_error == MAX_ERRORS):
         print("Error max erros reached")
         os.sys.exit(1)

      #   os.system("clear")
      print("******** Image number: " + str(index) + " Test number: " + str(test_number) + " ****************")

      print("Test pic: " + filenames_no_path[index])

      # Put both test images together as one photo to send to GPT
      os.system("rm -f " + TEMP_PIC)
      if (os.path.exists(TEMP_PIC)):
         print("ERROR file did not delete")
         os.system.exti(1)

      # Append both photos with convert
      os.system("convert " + PERFECT_PIC + " " + filenames_with_path[index] + " +append " + TEMP_PIC)
      # Config image to a smaller resolution , this makes for a better screen display and also saves cost on the GPT call
      os.system("convert " + TEMP_PIC + " -resize 800x600 " + TEMP_PIC)
      # Open the image with eog - a Linux image display application
      process = subprocess.Popen(["eog",TEMP_PIC])
      # Delay a little to wait for photo window to open
      time.sleep(.5)
      # Move the display application from the center of the screen to the upper left
      # Need to feed wmctrl the title of the window, which is just the jpg name
      # Seek to end and just get everything after the last /
      os.system("wmctrl -r " + TEMP_PIC.split("/")[-1] + " -e 0,0,0,-1,-1")

      # Path to image to feed to GPT, this matches original GPT example setup
      image_path =  TEMP_PIC

      # Keep a copy of the combined image
      shutil.copy(TEMP_PIC,OUTPUT_PICS + "/" + filenames_no_path[index])

      # Getting the base64 string
      base64_image = encode_image(image_path)
      headers = {
         "Content-Type": "application/json",
         "Authorization": f"Bearer {api_key}"
      }

      # Construct GPT API json, this is from GPT example code
      payload = {
         "model": model,
         "messages": [
            {
               "role": "user",
               "content": [
                  {
                     "type": "text",
                     "text": PROMPT
                  },
                  {
                     "type": "image_url",
                     "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                  }
               }
            ]
         }
      ],
      "max_tokens": 300
      }

      output = {}
      try:
         response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=90)
         output = response.json()
      except Exception as e:
         print("ERROR - Exception on openai web call.")
         print(e)
         web_api_error = web_api_error + 1
         continue

      if (response.status_code != 200  or "error" in output):
         print("ERROR - Received return error from openai web api.  Status code = " + str(response.status_code))
         web_api_error = web_api_error + 1
         if ("error" in output):
            print(output["error"]["message"])
            continue

      if ("choices" not in output):
         print("ERROR - Choices is not in output from GPT")
         web_api_error = web_api_error + 1
         continue

      message = output["choices"][0]["message"]["content"]

      print(message)

#   message = "{no}"  # debug line if needed

################### Extract GPT answer from {} ###################################
# Making several checks to make sure we are getting the answer in the right format
      cnt = 0
      cnt2 = 0
      pos = 0
      for char in message:
         if (char == "{"):
            cnt = cnt + 1
            start = pos
         if (char == "}"):
            cnt2 = cnt2 + 1
            end = pos
         pos = pos + 1

      if (cnt == 0 or cnt2 == 0):
         print("ERROR:  No brackets or incomplete")
         no_answer = no_answer + 1
         continue

      if (cnt > 1 or cnt2 > 1):
         print("ERROR:  Too many brackets in output from GPT")
         no_answer = no_answer + 1
         continue

      if (end < start):
         print("ERROR: Brackets are reversed in output from GPT")
         no_answer = no_answer + 1
         continue

      if ( (end - start) != 1 and (end - start) != 2 and (end - start) != 3):
         print("ERROR: Answer is the wrong size (Either 2 or 3 characters)")
         no_answer = no_answer + 1
         continue

      # Parse out the answer in between {}
      answer = ""
      match = re.search(r'\{(.*?)\}',message)
      answer = match.group(1)
      answer = answer.upper()

      if (not answer.isdigit()):
         print("ERROR: Answer is not a number")
         no_answer = no_answer + 1
         continue

      answer =  int(answer)
      if (answer < 0 or answer > 100):
         print("ERROR: Answer is out of range")
         no_answer = no_answer + 1
         continue

      print("The answer is: " + str(answer))

      results.append(answer)
      results_avg = sum(results) / len(results)
      results_avg = round(results_avg)
      std_dev = np.std(results)
      std_dev = round(std_dev,2)

      log(filenames_no_path[index] + ": " + message,LOG_GPT_ANSWER)

      test_number = test_number + 1

####### Print results from last test ############
   print("Image: " + filenames_no_path[index])
   print("No answer: " + str(no_answer))
   print("Web errors: " + str(web_api_error))
   print("Answers: " + str(results))
   print("Average answer: " + str(results_avg))
   print("Standard Deviation: " + str(std_dev))

   log("Img: " + filenames_no_path[index] + " Ans: " + str(results) + " Avg: " + str(results_avg) + " STD: " +  str(std_dev) + \
" No Ans: " + str(no_answer) + " Web Err: " + str(web_api_error),LOG_FILE)

   index = index + 1

process.terminate()
os.system("rm -f " + TEMP_PIC)
