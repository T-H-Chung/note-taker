import os
import yt_dlp
import logging
from faster_whisper import WhisperModel
import sys
import tiktoken
import requests
import platform
from openai import OpenAI


language_dict = {
    "简体中文": [
        "zh",
        "zh-Hans",
        "zh-CN",
        "zh-SG",
        "zh-Hant",
        "zh-HK",
        "zh-MO",
        "zh-TW",
    ],
    "繁體中文": [
        "zh",
        "zh-Hans",
        "zh-CN",
        "zh-SG",
        "zh-Hant",
        "zh-HK",
        "zh-MO",
        "zh-TW",
    ],
    "English": [
        "en",
        "en-AU",
        "en-BZ",
        "en-CA",
        "en-029",
        "en-HK",
        "en-IN",
        "en-IE",
        "en-JM",
        "en-MY",
        "en-NZ",
        "en-PH",
        "en-SG",
        "en-ZA",
        "en-TT",
        "en-AE",
        "en-GB",
        "en-US",
        "en-ZW",
    ],
    "Español": [
        "es",
        "es-AR",
        "es-VE",
        "es-BO",
        "es-CL",
        "es-CO",
        "es-CR",
        "es-CU",
        "es-DO",
        "es-EC",
        "es-SV",
        "es-GT",
        "es-HN",
        "es-419",
        "es-MX",
        "es-NI",
        "es-PA",
        "es-PY",
        "es-PE",
        "es-PR",
        "es-ES",
        "es-US",
        "es-UY",
    ],
    "Français": [
        "fr",
        "fr-BE",
        "fr-CI",
        "fr-CM",
        "fr-CA",
        "fr-029",
        "fr-CD",
        "fr-FR",
        "fr-HT",
        "fr-LU",
        "fr-ML",
        "fr-MA",
        "fr-MC",
        "fr-RE",
        "fr-SN",
        "fr-CH",
    ],
    "Deutsch": ["de", "de-AT", "de-DE", "de-LI", "de-LU", "de-CH"],
    "Português": ["pt", "pt-BR", "pt-PT"],
    "Русский": ["ru", "ru-MD", "ru-RU"],
    "日本語": ["ja", "ja-JP"],
    "العربية": [
        "ar",
        "ar-DZ",
        "ar-BH",
        "ar-EG",
        "ar-IQ",
        "ar-JO",
        "ar-KW",
        "ar-LB",
        "ar-LY",
        "ar-MA",
        "ar-OM",
        "ar-QA",
        "ar-SA",
        "ar-SY",
        "ar-TN",
        "ar-AE",
        "ar-YE",
    ],
    "हिन्दी": ["hi", "hi-IN"],
    "한국어": ["ko", "ko-KR"],
    "Italiano": ["it", "it-IT", "it-CH"],
}


def find_matching_item(a, b):
    set_b = set(b)
    for item in a:
        if item in set_b:
            return item
    return None


def get_video_info(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title")
        subtitles = info.get("subtitles")

    return title, subtitles


def download_subtitle(
    url, lang="en", preferred_formats=["srt", "vtt", "ass"], logger=None
):
    if logger is None:
        logger = logging.getLogger(__name__)
    title, subtitles = get_video_info(url)

    if not subtitles or lang not in subtitles:
        logger.info(f"No subtitles available in the requested language: {lang}")
        return None, None

    illegal_characters = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    for char in illegal_characters:
        title = title.replace(char, "")

    # Check for formats
    available_subs = subtitles[lang]
    for fmt in preferred_formats:
        for sub in available_subs:
            if sub["ext"] == fmt:
                ydl_opts = {
                    "quiet": True,
                    "skip_download": True,
                    "writesubtitles": True,
                    "subtitlesformat": fmt,
                    "subtitleslangs": [lang],
                    "outtmpl": title,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                logger.info(f"Subtitle downloaded and saved as '{title}.{lang}.{fmt}'")
                return f"{title}.{lang}.{fmt}", fmt
    return None, None


def convert_ass_to_text(ass_file):
    transcription = []
    with open(ass_file, "r", encoding="utf-8") as file:
        for line in file:
            if not line.startswith("Dialogue:"):
                continue
            line = line.split(",", 9)[-1]
            transcription.append(line.strip())

    return " ".join(transcription)


def convert_srt_vtt_to_text(srt_vtt_file):
    transcription = []
    with open(srt_vtt_file, "r", encoding="utf-8") as file:
        for line in file:
            if (
                line.strip()
                and not line.startswith("WEBVTT")
                and "Kind: captions" not in line
                and "Language:" not in line
            ):
                if not line.strip().isdigit() and "-->" not in line:
                    transcription.append(line.strip())

    return " ".join(transcription)


def download_audio(url, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)

    title, subtitles = get_video_info(url)
    illegal_characters = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    for char in illegal_characters:
        title = title.replace(char, "")
    ydl_opts = {"format": "bestaudio", "outtmpl": f"{title}.%(ext)s", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info = ydl.extract_info(url, download=False)
        ext = info.get("ext")

    logger.info(f"Audio downloaded and saved as '{title}.{ext}'")
    return f"{title}.{ext}"


def whisperAPITranscribe(audio_file, language, api_token, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)
    transcription = None
    # try:
    client = OpenAI(api_key=api_token)
    with open(audio_file, "rb") as audio:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio, language=language, response_format="text"
        )

    print(transcription, "gfdgfdgdg")

    # except Exception as e:
    #     logger.error(e)

    return transcription


def fasterWhisperTranscribe(
    file_path,
    language,
    model_size="medium.en",
    update_progress_bar=None,
    logger=None,
    file_remove=True,
):
    if logger is None:
        logger = logging.getLogger(__name__)

    compute_type = "float32" if platform.system() == "Darwin" else "float16"
    model = WhisperModel(model_size, device="auto", compute_type=compute_type)

    if model_size.endswith(".en"):
        segments, info = model.transcribe(file_path, beam_size=5, language="en")
    else:
        segments, info = model.transcribe(file_path, beam_size=5, language=language)

    transcription = ""
    total_duration = round(info.duration, 2)

    for segment in segments:
        transcription += segment.text
        if update_progress_bar is not None:
            update_progress_bar(round(segment.end / total_duration * 0.9, 2))

    with open(file_path + ".txt", "w", encoding="utf-8") as file:
        file.write(transcription)

    if file_remove:
        os.remove(file_path)

    return transcription


def split_text_by_token_limit_tiktoken(text, token_limit=3000, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    chunks = []

    for i in range(0, len(tokens), token_limit):
        chunk_tokens = tokens[i : i + token_limit]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks


def parse_input(input_string):
    lines = input_string.strip().split("\n")
    blocks = []

    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("- "):
            blocks.append(
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {"type": "text", "text": {"content": line_strip[2:]}}
                        ]
                    },
                }
            )
        elif line_strip.startswith("* "):
            blocks.append(
                {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {"type": "text", "text": {"content": line_strip[2:]}}
                        ]
                    },
                }
            )

    return blocks


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def check_property_exists(database_id, property_name, headers):
    url = f"https://api.notion.com/v1/databases/{database_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        database = response.json()
        return property_name in database["properties"]
    else:
        return False


def add_property_to_database(
    database_id, property_name, property_type, headers, logger=None
):
    if logger is None:
        logger = logging.getLogger(__name__)
    url = f"https://api.notion.com/v1/databases/{database_id}"
    update_payload = {
        "properties": {property_name: {"type": property_type, property_type: {}}}
    }
    response = requests.patch(url, headers=headers, json=update_payload)
    if response.status_code == 200:
        logger.info(f"Property '{property_name}' added to the database.")
    else:
        logger.warning(
            f"Failed to add property to database: {response.status_code}, {response.text}"
        )
