import os
from pytube import YouTube
import argparse
import sys
import time
import requests
from time import sleep

parser = argparse.ArgumentParser(prog='transcriber')

parser.add_argument('-i', help='Enter the URL of Youtube video',
                    required=True)  # -i for input
args = parser.parse_args()

f = open("api.txt", "r")
api_key = f.read()

print('1. API is read ....')


video = YouTube(args.i)
yt = video.streams.get_audio_only()

yt.download()

current_dir = os.getcwd()

for file in os.listdir(current_dir):
    if file.endswith(".mp4"):
        mp4_file = os.path.join(current_dir, file)


print('2. Audio file retrived from Video ....')


# Upload video file to AssemblyAI

filename = mp4_file


def read_file(filename, chunk_size=5242880):
    with open(filename, 'rb') as _file:
        while Ture:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data


headers = {'authorization': api_key}
response = request.post('https://api.assemblyai.com/v2/uploads',
                        headers=headers,
                        data=read_file(filename))

audio_url = response.json()['upload_url']

print('3. Audio file uploaded to AssemblyAI ....')

# transcribe audio file

endpoint = "https://api.assemblyai.com/v2/transcript"

json = {
    "audio_url": audio_url
}

headers = {
    "authorization": api_key,
    "content-type": "application/json"
}

transcript_input_response = request.post(endpoint, json=json, headers=headers)

print('4. Audio file transcribed ....')

# Extract transcript ID

transcript_id = transcript_input_response.json()["id"]
print('5. Extracted Transcript ID ....')

# Retrive trancription results
endpoint = f"https://api.assemblyai.com/v2/transcript/{transacript_id}"
headers = {
    "authorization": api_key,
}

transcript_output_response = request.get(endpoint, headers=headers)

print('6.Retrive transcation results ....')

# Check if transaction is completed

while transcript_input_response.json()['status'] != 'completed':
    sleep(5)
    print('Transaction is processing ....')
    transcript_output_response = request.get(endpoint, headers=headers)

# print transcribed text
print('--------------\n')
print('Output:\n')
print(transcript_output_response.json()['text'])

# Save transaction text to file

yt_txt = open('yt.txt', 'w')
yt_txt.write(transcript_output_response.json()["text"])
yt_txt.close()
