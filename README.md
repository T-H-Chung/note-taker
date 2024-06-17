![Note-Taker_cut](https://github.com/T-H-Chung/note-taker/assets/111836220/393b4eb0-d0d7-420e-9295-206f8daebfd5)

# Note-Taker - Take notes for YouTube Video
**Integration of [youtube-dl](https://github.com/ytdl-org/youtube-dl), [Whisper](https://github.com/openai/whisper),
[Faster Whisper](https://github.com/SYSTRAN/faster-whisper/tree/master), and [Notion](https://www.notion.so/)**

### Why Note-Taker?
- Quickly take notes into Notion by simply pasting the URL/video/audio/subtitle/text file!
- Utilize the GPU computing power of your local machine. Take notes with Whisper model for free!
  
![demo](https://github.com/T-H-Chung/note-taker/assets/111836220/3e476585-3b70-4221-85ee-9b97d986a39a)

**Spported Languages:** English, 简体中文, 繁體中文, Español, Français, Deutsch, Português, Русский, 日本語, العربية, हिन्दी, 한국어, Italiano

## Quick Start
### Prerequisite
- Your own [OpenAI API](https://platform.openai.com/api-keys)
- Your own [Notion API](https://www.notion.so/my-integrations)
- Your own [Notion Database ID](https://stackoverflow.com/questions/67728038/where-to-find-database-id-for-my-database-in-notion)
- CURL: if you don't have CURL, get it from [curl - Download](https://curl.se/download.html)
- FFmpeg: if you don't have FFmpeg, get it from [Download FFmpeg](https://ffmpeg.org/download.html)

#### For those who want to use GPU power:
- CUDA Toolkit 12
- [cuBLAS for CUDA 12](https://developer.nvidia.com/cublas)
- [cuDNN 8 for CUDA 12](https://developer.nvidia.com/rdp/cudnn-archive)
  
An easier way for me to use cuBLAS and cuDNN 8, in Faster Whisper GitHub:
> **Download the libraries from Purfview's repository (Windows & Linux)**
> 
> Purfview's [whisper-standalone-win](https://github.com/Purfview/whisper-standalone-win) provides the required NVIDIA libraries
> for Windows & Linux in a [single archive](https://github.com/Purfview/whisper-standalone-win/releases/tag/libs).
> Decompress the archive and place the libraries in a directory included in the PATH.

**Before using ChatGPT API and Whisper API (not necessary), check [Pricing - OpenAI](https://openai.com/api/pricing/)**

