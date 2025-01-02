# Clip-Crunch

This project is a **YouTube Video Summarizer** that allows users to input the URL of a YouTube video, download the video, transcribe its audio, and generate a summary of the content. It is built using **Python Flask** for the backend, **HTML/CSS** for the frontend, and uses **AWS Transcribe** and **AWS Bedrock** for transcription and summarization. The application is deployed on **Microsoft Azure**.

---

## Features

1. **YouTube Video Download**  
   - Utilizes the `pytube` library to download YouTube videos.

2. **Audio Transcription**  
   - Leverages **AWS Transcribe** to convert the audio of the downloaded video into text.

3. **Summarization**  
   - Employs **AWS Bedrock** for generating concise summaries of the transcribed text.

4. **Web Application**  
   - Frontend is built using **HTML** and **CSS**.
   - Backend is powered by **Python Flask**.

5. **Deployment**  
   - The entire application is deployed on **Azure**, making it accessible via the web.

---

## Installation

### Prerequisites
- Python 3.8 or later
- AWS account with access to **Transcribe** and **Bedrock**
- Microsoft Azure account
- Flask and required Python libraries
- Pytube installed

### Clone the Repository
```bash
git clone https://github.com/your-username/yt-video-summarizer.git
cd yt-video-summarizer
