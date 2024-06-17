import os
import requests
import json
import logging
from utils import (
    get_video_title,
    download_subtitle,
    get_file_format,
    convert_ass_to_text,
    convert_srt_vtt_to_text,
    download_audio,
    fasterWhisperTranscribe,
    whisperAPITranscribe,
    run_command,
    parse_input,
    split_text_by_token_limit_tiktoken,
    check_property_exists,
    add_property_to_database,
    language_dict,
)


def get_transcription_from_audio(
    audio_file,
    language,
    model_size="medium",
    api_token="",
    update_progress_bar=None,
    logger=None,
):
    if logger is None:
        logger = logging.getLogger(__name__)
    if model_size == "Whisper API":
        transcription = whisperAPITranscribe(
            audio_file, language_dict[language][0], api_token, logger=logger
        )
        os.remove(audio_file)
    else:
        transcription = fasterWhisperTranscribe(
            audio_file,
            language_dict[language][0],
            model_size=model_size,
            update_progress_bar=update_progress_bar,
            logger=logger,
        )
        os.remove(audio_file + ".txt")
    return transcription


def get_transcription_from_url(
    youtube_url,
    language,
    model_size="medium",
    api_token="",
    update_progress_bar=None,
    logger=None,
):
    if logger is None:
        logger = logging.getLogger(__name__)

    title = get_video_title(youtube_url)
    subtitle_file = download_subtitle(
        youtube_url, language=language_dict[language], logger=logger
    )

    if subtitle_file and os.path.exists(subtitle_file):
        subtitle_format = get_file_format(subtitle_file)
        if subtitle_format in [".srt", ".vtt"]:
            transcription = convert_srt_vtt_to_text(subtitle_file)
        elif subtitle_format == ".ass":
            transcription = convert_ass_to_text(subtitle_file)
        else:
            transcription = None
            logger.error("Unsupported subtitle format")
        os.remove(subtitle_file)

    else:
        logger.warning("Subtitle file not found. Downloading the audio....")
        audio_file = download_audio(youtube_url, logger=logger)
        logger.info("Transcribing the audio....")
        transcription = get_transcription_from_audio(
            audio_file, language, model_size, api_token, update_progress_bar, logger
        )

    logger.info("Transcription process completed.")
    return transcription, title


def take_notes_chatgpt(
    transcription,
    language,
    api_token,
    model_name="GPT-3.5-turbo",
    save_reply=False,
    logger=None,
):
    if logger is None:
        logger = logging.getLogger(__name__)
    if save_reply:
        with open("conversation.txt", "w", encoding="utf-8") as file:
            pass

    model = "gpt-3.5-turbo-0125" if model_name == "GPT-3.5-turbo" else "gpt-4o"
    task_hint = f'take the well-structured notes (in {language})(in sequence) including all the detail information (especially the numeric data) in every knowledge point/topic(can be one or many) (especially arguments from both sides of the controversy) in the transcription. (Format the structure with "- " for the topic and "* " for a detail information under its topic, separate each topic with an empty line, for example "- A \n* a\n- B")'
    messages = [{"role": "system", "content": task_hint}]
    user_chunks = split_text_by_token_limit_tiktoken(transcription, token_limit=2000)
    notes = ""
    for idx, chunk in enumerate(user_chunks):
        messages.append({"role": "user", "content": chunk})

        prompt = {"model": model, "messages": messages}
        output_file = "prompt.json"
        with open(output_file, "w") as file:
            json.dump(prompt, file, indent=4)

        command = [
            "curl",
            "https://api.openai.com/v1/chat/completions",
            "-H",
            f"Authorization: Bearer {api_token}",
            "-H",
            "Content-Type: application/json",
            "-d",
            "@prompt.json",
        ]
        chatgpt_reply = run_command(command, logger=logger)
        messages.append(chatgpt_reply["choices"][0]["message"])
        messages.append(
            {
                "role": "system",
                "content": "Following is the next part. Continue the task.",
            }
        )

        if len(messages) > 6:
            messages.pop(1)
            messages.pop(1)
            messages.pop(1)

        if save_reply:
            with open("conversation.txt", "a", encoding="utf-8") as file:
                for index, line in enumerate(messages, start=1):
                    if line["role"] == "assistant":
                        file.write(f"{index}. {line}\n\n")

        if idx == 0:
            notes += chatgpt_reply["choices"][0]["message"]["content"]
        else:
            notes += "\n".join(
                chatgpt_reply["choices"][0]["message"]["content"].split("\n")[1:]
            )
    os.remove("prompt.json")

    logger.info("Note-taking process completed.")
    return notes


def create_notes_notion(
    notes, title, youtube_url, notion_api_token, database_id, logger=None
):
    if logger is None:
        logger = logging.getLogger(__name__)

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {notion_api_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    property_name = "Link"
    if not check_property_exists(database_id, property_name, headers):
        add_property_to_database(database_id, property_name, "url", headers)

    blocks = parse_input(notes)

    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {"title": [{"type": "text", "text": {"content": title}}]},
            "Link": {"url": youtube_url},
        },
        "children": blocks[:99],
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    def append_apge(page_id, append_data):
        append_block_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        append_data = {"children": append_data[:99]}
        response = requests.patch(
            append_block_url, headers=headers, data=json.dumps(append_data)
        )
        if response.status_code == 200:
            if len(append_data) > 99:
                append_apge(page_id, append_data[99:])
        else:
            logger.error(
                "Failed to append page. Status code: %d. Response: %s",
                response.status_code,
                response.text,
            )

    if response.status_code == 200:
        response_data = response.json()
        if len(blocks) > 99:
            page_id = response_data["id"]
            append_apge(page_id, blocks[99:])
        logger.info("Page created successfully!")
    else:
        logger.error(
            "Failed to create page. Status code: %d. Response: %s",
            response.status_code,
            response.text,
        )
