import sys
import logging
import customtkinter as ctk
from PIL import Image
import json
from core_func import (
    get_transcription_from_url,
    get_transcription_from_audio,
    take_notes_chatgpt,
    create_notes_notion,
)
from utils import resource_path, convert_srt_vtt_to_text, convert_ass_to_text
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

# Configure the logger
log_file = "app_log.txt"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

if getattr(sys, "frozen", False):
    os.environ["PATH"] += os.pathsep + resource_path("ffmpeg.exe")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Note-Taker")
        self.geometry("450x320")
        self.resizable(False, False)
        self.iconbitmap(resource_path("./assets/Note-Taker.ico"))

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True)  # Center the frame in the window

        self.setting_icon_path = resource_path(
            "./assets/gear.png"
        )  # Update this path to your settings icon image file
        self.setting_icon = ctk.CTkImage(Image.open(self.setting_icon_path))

        self.setting = self.load_setting()
        if self.setting.get("chatgpt_api", "") and self.setting.get("notion_api", ""):
            self.main_interface()
        else:
            self.setting_interface()

    def save_setting(self, data):
        with open("setting.json", "w") as file:
            json.dump(data, file)

    def load_setting(self):
        try:
            with open("setting.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            logger.warning("Settings file not found.")
            return {}

    def update_console_output(self, message):
        self.console_output.configure(text=message)
        self.update_idletasks()

    def update_progress_bar(self, progress):
        self.progress_bar.set(progress)
        self.progress_bar.update()

    def main_interface(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1, minsize=35)
        self.main_frame.grid_rowconfigure(6, weight=1, minsize=35)

        setting = self.load_setting()

        # Create entry fields for the main interface
        self.frame1 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame1.grid(row=0, column=0, pady=10, padx=20, sticky="w")
        self.label1 = ctk.CTkLabel(self.frame1, text="URL/File Path:")
        self.label1.grid(row=0, column=0, padx=10)
        self.entry1 = ctk.CTkEntry(
            self.frame1,
            placeholder_text="URL/Video/Audio/Subtitle/Text File",
            width=250,
        )
        self.entry1.grid(row=0, column=1, padx=10)

        self.frame4 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame4.grid(row=1, column=0, pady=10, padx=20, sticky="w")
        self.label4 = ctk.CTkLabel(self.frame4, text="Language:")
        self.label4.grid(row=0, column=0, padx=10)
        self.opt_lan = ctk.CTkOptionMenu(
            self.frame4,
            values=[
                "English",
                "简体中文",
                "繁體中文",
                "Español",
                "Français",
                "Deutsch",
                "Português",
                "Русский",
                "日本語",
                "العربية",
                "हिन्दी",
                "한국어",
                "Italiano",
            ],
            width=150,
        )
        self.opt_lan.set(setting.get("language", "English"))
        self.opt_lan.grid(row=0, column=1, padx=10)

        # Whisper model selection
        self.frame2 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame2.grid(row=2, column=0, pady=10, padx=20, sticky="w")
        self.label2 = ctk.CTkLabel(self.frame2, text="Whisper model:")
        self.label2.grid(row=0, column=0, padx=10)
        self.opt_whisper = ctk.CTkOptionMenu(
            self.frame2,
            values=[
                "small.en",
                "small",
                "medium.en",
                "medium",
                "large-v3",
                "Whisper API",
            ],
            width=150,
        )
        self.opt_whisper.set(setting.get("whisper_model", "medium.en"))
        self.opt_whisper.grid(row=0, column=1, padx=10)

        # GPT model selection
        self.frame3 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame3.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        self.label3 = ctk.CTkLabel(self.frame3, text="GPT model:")
        self.label3.grid(row=0, column=0, padx=10)
        self.opt_gpt = ctk.CTkOptionMenu(
            self.frame3, values=["GPT-4o-mini", "GPT-3.5-turbo", "GPT-4o"], width=150
        )
        self.opt_gpt.set(setting.get("gpt_model", "GPT-4o-mini"))
        self.opt_gpt.grid(row=0, column=1, padx=10)

        # Create buttons for the main interface
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, pady=20, padx=20)

        self.take_notes_button = ctk.CTkButton(
            self.button_frame,
            text="Take Notes",
            width=300,
            height=30,
            command=self.take_notes,
        )
        self.take_notes_button.grid(row=0, column=0, padx=10)

        self.setting_button = ctk.CTkButton(
            self.button_frame,
            image=self.setting_icon,
            text="",
            width=30,
            height=30,
            command=self.switch_to_setting,
        )
        self.setting_button.grid(row=0, column=1, padx=10)

        # Create and hide the console output
        self.console_output = ctk.CTkLabel(
            self.main_frame, text="", anchor="w", width=400, height=30
        )
        self.console_output.grid(row=5, column=0, padx=20, pady=0, sticky="ew")
        self.console_output.grid_propagate(False)
        self.console_output.grid_remove()  # Hide the console output initially

        # Create and hide the progress bar
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=400)
        self.update_progress_bar(0)
        self.progress_bar.grid(row=6, column=0, padx=0, pady=0)
        self.progress_bar.grid_propagate(False)
        self.progress_bar.grid_remove()  # Hide the progress bar initially

    def save_task_setting(self):
        self.setting = {
            "chatgpt_api": self.setting.get("chatgpt_api", ""),
            "notion_api": self.setting.get("notion_api", ""),
            "database_id": self.setting.get("database_id", ""),
            "language": self.opt_lan.get(),
            "whisper_model": self.opt_whisper.get(),
            "gpt_model": self.opt_gpt.get(),
        }
        self.save_setting(self.setting)

    def take_notes(self):
        # Disable buttons
        self.take_notes_button.configure(state="disabled")
        self.setting_button.configure(state="disabled")
        self.entry1.configure(state="disabled")
        self.opt_lan.configure(state="disabled")
        self.opt_whisper.configure(state="disabled")
        self.opt_gpt.configure(state="disabled")

        self.console_output.grid()
        self.progress_bar.grid()
        self.update_idletasks()

        self.save_task_setting()
        self.update_progress_bar(0)
        try:
            user_input = self.entry1.get()
            if user_input.startswith("https"):
                self.update_console_output(
                    "Getting the transcription....                    "
                )
                logger.info("Getting the transcription...")
                transcription, title = get_transcription_from_url(
                    user_input,
                    self.opt_lan.get(),
                    self.opt_whisper.get(),
                    api_token=self.setting.get("chatgpt_api", ""),
                    update_progress_bar=self.update_progress_bar,
                    logger=logger,
                )
            else:
                title = os.path.splitext(os.path.basename(user_input))[0]
                if user_input.endswith(".txt"):
                    with open(user_input, "r", encoding="utf-8") as file:
                        transcription = file.read()
                elif user_input.endswith(".srt") or user_input.endswith(".vtt"):
                    transcription = convert_srt_vtt_to_text(user_input)
                elif user_input.endswith(".ass"):
                    transcription = convert_ass_to_text(user_input)
                else:
                    self.update_console_output(
                        "Getting the transcription....                    "
                    )
                    logger.info("Getting the transcription...")
                    transcription = get_transcription_from_audio(
                        user_input,
                        self.opt_lan.get(),
                        self.opt_whisper.get(),
                        self.setting.get("chatgpt_api", ""),
                        self.update_progress_bar,
                        logger,
                        file_remove=False,
                    )

            self.update_progress_bar(0.9)
            self.update_console_output(
                "Taking the notes by ChatGPT....                    "
            )
            logger.info("Taking the notes by ChatGPT...")
            notes = take_notes_chatgpt(
                transcription,
                self.opt_lan.get(),
                self.setting.get("chatgpt_api", ""),
                model_name = self.opt_gpt.get(),
                logger=logger,
            )
            self.update_progress_bar(1)
            self.update_console_output("Creating Notion page....                    ")
            logger.info("Creating Notion page...")

            create_notes_notion(
                notes,
                title,
                user_input,
                self.setting.get("notion_api", ""),
                self.setting.get("database_id", ""),
                logger=logger,
            )
            self.update_console_output(
                "Note-taking process completed!                    "
            )
            logger.info("Note-taking process completed!")
        except Exception as e:
            self.update_console_output(str(e) + "                    ")
            logger.error("", exc_info=True)

        # Enable buttons
        self.take_notes_button.configure(state="normal")
        self.setting_button.configure(state="normal")
        self.entry1.configure(state="normal")
        self.opt_lan.configure(state="normal")
        self.opt_whisper.configure(state="normal")
        self.opt_gpt.configure(state="normal")

    def switch_to_setting(self):
        self.save_task_setting()
        self.setting_interface()

    def setting_interface(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        setting = self.load_setting()

        # Create entry fields for the setting interface
        self.frame1 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame1.grid(row=0, column=0, pady=10, padx=20, sticky="e")
        self.label1 = ctk.CTkLabel(self.frame1, text="ChatGPT API:")
        self.label1.grid(row=0, column=0, padx=10)
        self.entry1 = ctk.CTkEntry(self.frame1, placeholder_text="API token", width=200)
        self.entry1.insert(0, setting.get("chatgpt_api", ""))
        self.entry1.grid(row=0, column=1, padx=10)

        self.frame2 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame2.grid(row=1, column=0, pady=10, padx=20, sticky="e")
        self.label2 = ctk.CTkLabel(self.frame2, text="Notion API:")
        self.label2.grid(row=0, column=0, padx=10)
        self.entry2 = ctk.CTkEntry(self.frame2, placeholder_text="API token", width=200)
        self.entry2.insert(0, setting.get("notion_api", ""))
        self.entry2.grid(row=0, column=1, padx=10)

        self.frame3 = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame3.grid(row=2, column=0, pady=10, padx=20, sticky="e")
        self.label3 = ctk.CTkLabel(self.frame3, text="Database ID:")
        self.label3.grid(row=0, column=0, padx=10)
        self.entry3 = ctk.CTkEntry(
            self.frame3, placeholder_text="Database ID", width=200
        )
        self.entry3.insert(0, setting.get("database_id", ""))
        self.entry3.grid(row=0, column=1, padx=10)

        self.save_button = ctk.CTkButton(
            self.main_frame, text="Save", command=self.save_api_setting
        )
        self.save_button.grid(row=3, column=0, pady=20, padx=20)

    def save_api_setting(self):
        self.setting = {
            "chatgpt_api": self.entry1.get(),
            "notion_api": self.entry2.get(),
            "database_id": self.entry3.get(),
            "language": self.setting.get("language", "English"),
            "whisper_model": self.setting.get("whisper_model", "medium.en"),
            "gpt_model": self.setting.get("gpt_model", "GPT-3.5-turbo"),
        }
        self.save_setting(self.setting)
        self.main_interface()


if __name__ == "__main__":
    app = App()
    app.mainloop()
