import sys
import os 
import yaml
import re
import time 
import logging 
from pathlib import Path
import mp3 
import translate 
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_translation_options():
    print("\nAvailable translation options:")
    print("1. Google Translate (Free API)")
    print("2. DeepL Translate (Requires API Key)")

    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            return "Google"
        if choice == "2":
            return "DeepL"
        else:
            print("Invalid choice. Please re-enter your choice 1 or 2.")

def main():
    logger.info("Starting the functions")
    with tqdm(total=100, desc="Overall progress", unit="%") as pbar:
    
        try:
            pbar.set_description("Getting user choices...")
            model_key, output_language = mp3.get_user_choice()
            translation_service = get_translation_options()
            pbar.update(10)

            pbar.set_description("Finding audio file...")
            input_folder = Path(mp3.input_file)  
            audio_files = list(input_folder.glob("*.mp3"))
            if not audio_files:
                logger.error("No audio files found in input folder")
                return
            input_file = audio_files[0]
            logger.info(f"Processing: {input_file.name}")
            pbar.update(5)

            pbar.set_description("Transcribing audio...")
            segments_list, detected_language, info = mp3.transcribe_audio(input_file, model_key)
            pbar.update(40)

            pbar.set_description("Saving transcription...")
            transcription_file = mp3.save_transcription(segments_list, input_file)
            pbar.update(5)

            pbar.set_description("Loading transcription...")
            transcription_text = translate.load_transcription(transcription_file)
            if not transcription_text:
                logger.error("No transcription found")
                return
            pbar.update(5)

            pbar.set_description(f"Translating using {translation_service}...")
            if translation_service == "DeepL":
                translated_text = translate.deepl_translate_text(transcription_text, detected_language, output_language)
            else:
                translated_text = translate.google_translate_text(transcription_text, detected_language, output_language)
            pbar.update(30)
            
            pbar.set_description("Saving translated file...")
            translate.save_translated_text(translated_text, output_language)
            pbar.update(5)
        
        except Exception as e:
            pbar.set_description("Error occurred")
            logger.error(f"Error in main function: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
