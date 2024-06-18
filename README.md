![Note-Taker_cut](https://github.com/T-H-Chung/note-taker/assets/111836220/393b4eb0-d0d7-420e-9295-206f8daebfd5)

# Note-Taker - Take Notes for Online Video
**📝 Integration of [yt-dlp](https://github.com/yt-dlp/yt-dlp),
[Faster Whisper](https://github.com/SYSTRAN/faster-whisper/tree/master)(from [Whisper](https://github.com/openai/whisper)), 
[ChatGPT](https://chatgpt.com/), and [Notion](https://www.notion.so/) with GUI!**

### Why Note-Taker?
- Quickly take notes into Notion by simply **pasting the URL/video/audio/subtitle/text file path!**
- Support thousands of sites including **YouTube** and **BiliBili**, check [supported sites](https://www.similarweb.com/zh-tw/website/imdb.com/).
- Utilize the **GPU** computing power of your local machine. Take notes with Whisper model for **free!**

![demo-white](https://github.com/T-H-Chung/note-taker/assets/111836220/af37c44e-ed79-46bd-b15f-192f91c94801)

> [!NOTE]
> **Spported Languages:** English, 简体中文, 繁體中文, Español, Français, Deutsch, Português, Русский, 日本語, العربية, हिन्दी, 한국어, Italiano

> [!NOTE]
> The corresponding subtitles will be downloaded if available. -> No time/GPU comsuming for transcription. \
> **Spported Subtitles:** srt, vtt, ass

## Quick Start
### Prerequisite
- Your own [OpenAI API](https://platform.openai.com/api-keys) (You need to have a balance)
- Your own [Notion API](https://www.notion.so/my-integrations)
- Your own [Notion Database ID](https://stackoverflow.com/questions/67728038/where-to-find-database-id-for-my-database-in-notion)
  ([How to create a database](https://www.notion.so/help/guides/creating-a-database))
- [Permissions of your database for Notion API](https://developers.notion.com/docs/create-a-notion-integration#give-your-integration-page-permissions)
- CURL: if you don't have CURL, get it from [curl - Download](https://curl.se/download.html)
- FFmpeg: if you don't have FFmpeg, get it from [Download FFmpeg](https://ffmpeg.org/download.html)

#### For those who want to use GPU power:
- CUDA Toolkit 12
- [cuBLAS for CUDA 12](https://developer.nvidia.com/cublas)
- [cuDNN 8 for CUDA 12](https://developer.nvidia.com/rdp/cudnn-archive)
  
**You can use CPU and Whisper API if you don't want to use a GPU**
  
> [!TIP]
> An easier way for me to use cuBLAS and cuDNN 8, in Faster Whisper GitHub:
> > **Download the libraries from Purfview's repository (Windows & Linux)**
> > 
> > Purfview's [whisper-standalone-win](https://github.com/Purfview/whisper-standalone-win) provides the required NVIDIA libraries
> > for Windows & Linux in a [single archive](https://github.com/Purfview/whisper-standalone-win/releases/tag/libs).
> > Decompress the archive and place the libraries in a directory included in the `PATH`.
> 
> You can also place the archives in the same folder as the executable or Python code below

> [!NOTE]
> Before using ChatGPT API and Whisper API(not necessary), check [Pricing - OpenAI](https://openai.com/api/pricing/)

## Usage: Executable by [PyInstaller](https://github.com/pyinstaller/pyinstaller) (Windows)
1. [Download Executable](https://drive.google.com/file/d/10KHfc_ePeJANmnRfeksi1xqCk_Vi8qnQ/view?usp=sharing)
2. Run it and setup the APIs
   
![setting](https://github.com/T-H-Chung/note-taker/assets/111836220/8f2de75c-6a98-48a8-83eb-4d8a38372367)

4. Paste the link/file path and then setup link/file language and your preference

![main_page](https://github.com/T-H-Chung/note-taker/assets/111836220/a003d68e-cd08-4823-a1a0-11f45b00985c)

## Usage: Python Usage
![requirements](https://img.shields.io/badge/Python->3.10-3480eb.svg?longCache=true&style=flat&logo=python)
1. Clone the repo
2. Install Python packages
   ```
   pip install -r requirements.txt
   ```
3. Run Python script and setup the APIs by GUI (like in Usage: Executable)
   ```
   python main.py
   ```
4. Paste the link/file path and then setup link/file language and your preference (like in Usage: Executable)

## Known Issues
- App crashes and exits suddenly after transcribing: The app will save transcription into a `.txt` file in the same folder.
  Use it to take notes. Or choose a smaller Whisper model.

<a href="https://www.flaticon.com/free-icons/settings" title="settings icons">Settings icons created by Freepik - Flaticon</a>
  
