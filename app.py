import streamlit as st
import os
import sys
import time
import requests

from pytube import YouTube
from time import sleep
from zipfile import ZipFile


st.markdown('# **Trans-Criber App**')
bar = st.progress(0)


# Retrive audio file from Youtube


def get_yt(URL):
    video = YouTube(URL)
    yt = video.streams.get_audio_only()
    yt.download()

    bar.progress(10)

# Upload Youtube file to AssemblyAI


def transcribe_yt():

    current_dir = os.getcwd()

    for file in os.listdir(current_dir):
        if file.endswith(".mp4"):
            mp4_file = os.path.join(current_dir, file)

    filename = mp4_file
    bar.progress(20)

    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data
    headers = {'authorization': api_key}
    response = requests.post('https://api.assemblyai.com/v2/upload',
                             headers=headers,
                             data=read_file(filename))
    audio_url = response.json()['upload_url']
    bar.progress(30)

    # Transcribing uploaded audio file
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {
        "audio_url": audio_url
    }

    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }

    transcript_input_response = requests.post(
        endpoint, json=json, headers=headers)

    bar.progress(40)

    # Extract Transcription ID
    transcript_id = transcript_input_response.json()["id"]
    bar.progress(50)

    # Retrive transactional result
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {
        "authorization": api_key,
    }
    transcript_output_response = requests.get(endpoint, headers=headers)
    bar.progress(60)

    # Check if transcription is complete

    while transcript_output_response.json()['status'] != 'completed':
        sleep(5)
        st.warning('Transaction is processing......')
        transcript_output_response = requests.get(endpoint, headers=headers)

    bar.progress(100)

    # Print transcribed test
    st.header('Output')
    st.success(transcript_output_response.json()["text"])

    # save result to text file

    yt_txt = open('yt.txt', 'w')
    yt_txt.write(transcript_output_response.json()["text"])
    yt_txt.close()

    # save the file as SRT
    srt_endpoint = endpoint + "/srt"
    srt_response = requests.get(srt_endpoint, headers=headers)
    with open("yt.srt", "w") as _file:
        _file.write(srt_response.text)

    zip_file = ZipFile('transcription.zip', 'w')
    zip_file.write('yt.txt')
    zip_file.write('yt.srt')
    zip_file.close()

# Delete previous file


def clear_transcription():
    current_dir = os.getcwd()

    for file in os.listdir(current_dir):
        if file.endswith('.mp4'):
           # os.chmod(current_dir, 0o777)
            del_file = os.path.join(current_dir, file)
            os.chmod(del_file, 0o777)
            os.remove(del_file)


# The App
api_key = st.secrets['api_key']

st.warning('Awaiting URL input in the sidebar.')

# sidebar
st.sidebar.header('Input parameter')

with st.sidebar.form(key='my_form'):
    URL = st.text_input('Enter YouTube video url')
    submit_button = st.form_submit_button(label='Go')
    clear_button = st.form_submit_button(label='Clear')


# Custom Functions
if submit_button:
    get_yt(URL)
    transcribe_yt()

    with open("transcription.zip", "rb") as zip_download:
        btn = st.download_button(label="Download ZIP",
                                 data=zip_download,
                                 file_name="transcription.zip",
                                 mime="application/zip"
                                 )

if clear_button:
    clear_transcription()
