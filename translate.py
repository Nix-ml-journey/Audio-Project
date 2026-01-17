import sys
import os 
import yaml
import re
import time 
import logging 
from pathlib import Path
import requests 
import deep_translator 
from deep_translator import DeeplTranslator, GoogleTranslator

def load_config(config_file="mini_config.yml"):
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            logging.getLogger(__name__).warning(f"Config file {config_file} not found")
            return {}

        with open(config_path, 'r', encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            return config

    except Exception as e:
        logging.getLogger(__name__).error(f"Error loading config from {config_file}: {e}")
        return {}

def load_transcription(output_file):
    try:
        config_path = Path(output_file)
        if not config_path.exists():
            logging.getLogger(__name__).warning(f"Transcription file {output_file} not found")
            return None
        with open(config_path, 'r', encoding="utf-8") as f:
            transcription = f.read()
        return transcription 
    except Exception as e:
        logging.getLogger(__name__).error(f"Error loading transcription from {output_file}: {e}")
        return None

_config = load_config()
output_folder = Path(_config.get('output_folder', Path.home() / 'output'))
translated_folder = Path(_config.get('translated_folder', Path.home() / 'translated'))
audio_translation_language_options = _config.get('audio_translation_language_options', [])
deepl_api_key = _config.get('deepl_api_key',None)

def get_output_language(user_input, available_languages):
    user_input = user_input.lower().strip()
    for name, language_code in available_languages:
        if user_input == name.lower() or user_input == language_code.lower():
            return language_code
    return None

def get_user_choice():

    print ("\nAvailable output languages for translations:")
    for options in audio_translation_language_options:
        name, language_code = options
        print(f" - {name} ({language_code})")

    while True:
        output_language = input("Enter the output language: ").strip().lower()
        output_language = get_output_language(output_language, audio_translation_language_options)
        if output_language is not None:
            break
        print("Invalid language. Please try again.")

    return output_language

def deepl_translate_text(transcription, source_language, output_language):
    logger = logging.getLogger(__name__)

    if not deepl_api_key:
        raise ValueError("DeepL API key not found in config file")
    
    source_language = source_language.lower()
    output_language = output_language.lower()
    
    try:
        translator = DeeplTranslator(api_key=deepl_api_key, source=source_language, target=output_language)
        translated_text = translator.translate(transcription)
        logger.info(f"Translated {len(translated_text)} characters from {source_language} to {output_language}")
        return translated_text
    except Exception as e:
        if "No support for the provided language" in str(e):
            logger.warning(f"Library validation failed for {source_language}, using direct DeepL API call...")
            if deepl_api_key.endswith(":fx"):
                url = "https://api-free.deepl.com/v2/translate"
            else:
                url = "https://api.deepl.com/v2/translate"

            params = {
                "auth_key": deepl_api_key,
                "text": transcription,
                "source_lang": source_language,
                "target_lang": output_language
            }

            response = requests.post(url, data=params)
            response.raise_for_status()
            result = response.json()
            translated_text = result["translations"][0]["text"]
            logger.info(f"Translated {len(translated_text)} characters from {source_language} to {output_language} (via direct API call)")
            return translated_text 
        else:
            raise 

def google_translate_text(transcription, source_language, output_language):
    logger = logging.getLogger(__name__)
    source_language = source_language.lower()
    output_language = output_language.lower()
    translator = GoogleTranslator(source=source_language, target=output_language)
    translated_text = translator.translate(transcription)
    logger.info(f"Translated {len(translated_text)} characters from {source_language} to {output_language}")
    return translated_text

def save_translated_text(translated_text, output_language):
    logger = logging.getLogger(__name__)
    translated_file = translated_folder / f"translated_{output_language}.txt"
    with open(translated_file, 'w', encoding="utf-8") as f:
        f.write(translated_text)
    logger.info(f"Saved translated text to {translated_file}")
    return translated_file




