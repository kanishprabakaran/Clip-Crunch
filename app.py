from flask import Flask, request, jsonify, render_template
from pytubefix import YouTube
import time
import json
import boto3
from botocore.exceptions import ClientError
import urllib
import uuid
from io import BytesIO

app = Flask(__name__)

aws_access_key_id = 'Your AWS Acess key ID'
aws_secret_access_key = 'Your AWS Secret Access Key'
aws_region = 'us-east-1'
bucket_name = 'ytbucket-3'

def download_audio(url):
    """Downloads audio from a YouTube video as bytes."""

    vid = YouTube(url)
    audio_stream = vid.streams.get_audio_only()
    unique_id = str(uuid.uuid4())
    audio_file_name = f"{unique_id}.mp3"

    print(f"\nVideo found: {vid.title}\n")
    print("Downloading audio to memory...")

    audio_data = BytesIO()
    audio_stream.stream_to_buffer(audio_data)
    audio_data.seek(0)  

    print("Audio download complete.")

    return audio_data, audio_file_name

def upload_to_s3(file_data, bucket, object_name):
    """Uploads a file in bytes to an S3 bucket."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    try:
        print('Uploading file to S3...')
        # Use upload_fileobj for in-memory file-like objects
        s3_client.upload_fileobj(file_data, bucket, object_name)
        print("File uploaded to S3.")
    except ClientError as e:
        print(f"Failed to upload to S3: {e}")


def transcribe_audio(job_name, file_uri):
    """Transcribes an audio file using Amazon Transcribe."""
    transcribe_client = boto3.client(
        'transcribe',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )
    
    print("Transcription started...")
    while True:
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        status = job['TranscriptionJob']['TranscriptionJobStatus']
        if status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {status}.")
            if status == 'COMPLETED':
                response = urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri'], timeout=30)
                data = json.loads(response.read())
                text = data['results']['transcripts'][0]['transcript']
                print("Transcription complete. Transcript saved.")
            break
        else:
            print("Transcription in progress. Waiting...")
        time.sleep(20)
    return text

def summarize_text(t):
    """Summarizes the transcribed text using Bedrock."""
    model_id = 'us.meta.llama3-2-1b-instruct-v1:0'
    bedrock = boto3.client(
        "bedrock-runtime",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )
    t += " Summarize the above in 3 to 4 lines."
    
    prompt = (
        "You are a content summarization expert. Summarize the given content meaningfully without omitting important details."
        f"\n\nHuman:{t}\n\nAssistant:"
    )

    
    request = json.dumps({"prompt": prompt, "temperature": 0.5})
    response = bedrock.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    summary = model_response["generation"]
    
    print("Your Summary:", summary)
    return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_summary', methods=['POST'])
def get_summary():
    data = request.json
    url = data.get('url')
    if url:

        if url == 'https://youtu.be/NHopJHSlVo4?si=I3fu0S_4Ucwk4afQ':
            s3_uri = f's3://{bucket_name}/83c94bc3-f668-4713-98d1-eb26345d393f.mp3'
            transcription_text = transcribe_audio('83c94bc3-f668-4713-98d1-eb26345d393f', s3_uri)
        elif url == 'https://youtu.be/H14bBuluwB8?si=qA02zqG5T-eIlsoG':
            s3_uri = f's3://{bucket_name}/4b58f6c4-3b61-4ccf-8841-680e18f8572c.mp3'
            transcription_text = transcribe_audio('4b58f6c4-3b61-4ccf-8841-680e18f8572c', s3_uri)
        elif url == 'https://youtu.be/4Bs0qUB3BHQ?si=-cuEJ79cQaNzMrht':
            s3_uri = f's3://{bucket_name}/7882e5c4-b921-4b17-893b-a3a6a3c127e6.mp3'
            transcription_text = transcribe_audio('7882e5c4-b921-4b17-893b-a3a6a3c127e6', s3_uri)
        elif url == 'https://youtu.be/Fzk4KVxt99U?si=OOOSz2gAQkYoMBs0':
            s3_uri = f's3://{bucket_name}/63b97385-3304-4b67-8eff-be9d3b69c471.mp3'
            transcription_text = transcribe_audio('63b97385-3304-4b67-8eff-be9d3b69c471', s3_uri)
        elif url == 'https://youtu.be/0A6fJ13J2Qk?si=AkhaUS7pwntrcMP0':
            s3_uri = f's3://{bucket_name}/cfcb0d86-26a1-4c78-9f64-109252723579.mp3'
            transcription_text = transcribe_audio('cfcb0d86-26a1-4c78-9f64-109252723579', s3_uri)

        else:
            # Process a new URL: download, upload, and transcribe
            audio_file, unique_id = download_audio(url)
            s3_uri = f's3://{bucket_name}/{unique_id}.mp3'
            upload_to_s3(audio_file, bucket_name, f"{unique_id}.mp3")
            transcription_text = transcribe_audio(unique_id, s3_uri)
    if transcription_text:
        summary = summarize_text(transcription_text)
        print(summary)
        return jsonify({"summary": summary})
    else:
        return jsonify({"summary": "Error in transcription or summarization"})



if __name__ == '__main__':
    app.run(debug=True)