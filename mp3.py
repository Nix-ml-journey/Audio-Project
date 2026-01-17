import sys
import os 
import yaml
import re
import time 
import logging 
import pygame
from pathlib import Path
from tqdm import tqdm

try:
    import faster_whisper as Whispermodel
except ImportError as e:
    print(f"Error: faster-whisper not installed: {e}")
    print("Install with: pip install faster-whisper")
    sys.exit(1)

def load_config(config_file="mini_config.yml"):
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            logging.getLogger(__name__).warning(f"Config file {config_file} not found")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        if 'audio_translation_language_options' in config:
            config['audio_translation_language_options'] = [tuple(item) for item in config['audio_translation_language_options']]
        if 'timestamp_pattern' in config and isinstance(config['timestamp_pattern'], str):
            config['timestamp_pattern'] = re.compile(config['timestamp_pattern'])

        return config 
    except Exception as e:
        logging.getLogger(__name__).error(f"Error loading config from {config_file}: {e}")
        return {}

_config = load_config()
model_sizes = _config.get('model_sizes', {})
timestamp_pattern = _config.get('timestamp_pattern', re.compile(fr'\[(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})\]'))
audio_translation_language_options = _config.get('audio_translation_language_options', [])
language_prompts = _config.get('language_prompts', {})
input_file = _config.get('input_file', Path.home() / 'input')
output_folder = Path(_config.get('output_folder', Path.home() / 'output'))

def parse_timestamp(time_str):
    match = timestamp_pattern.match(time_str)
    if match:
        start_min, start_sec, end_min, end_sec = match.groups()
        return int(start_min) * 60 + int(start_sec), int(end_min) * 60 + int(end_sec)
    return None, None

def get_model_key(user_input, available_sizes):
    user_input = user_input.lower().strip()
    if user_input in available_sizes:
        return user_input
    return None

def get_output_language(user_input, available_languages):
    user_input = user_input.lower().strip()
    for name, language_code in available_languages:
        if user_input == name.lower() or user_input == language_code.lower():
            return language_code
    return None

def get_user_choice():

    print ("\nSelect an option model size for the list below:")
    for key, size in model_sizes.items():
        print(f" - {key}: {size}")

    while True:
        model_key = input("Enter the model size: ").strip().lower()
        model_key = get_model_key(model_key, model_sizes)
        if model_key is not None:
            break
        print("Invalid model. Please try again.")

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

    return model_key, output_language

def get_language_prompts(output_language):
    prompt = language_prompts.get(output_language, "")
    return prompt

def transcribe_audio(input_file, model_size):
    logger = logging.getLogger(__name__)
    model = Whispermodel.WhisperModel(model_size, device="cpu")

    segments, info = model.transcribe(str(input_file), language=None, 
    beam_size=5, best_of=5, temperature=0, condition_on_previous_text=True,
    compression_ratio_threshold=2.4)

    segments_list = []
    with tqdm(desc="Processing segments", unit="segment") as pbar:
        for segment in segments:
            segments_list.append(segment)
            pbar.update(1)
    
    detected_language = info.language
    logger.info(f"Transcribed {len(segments_list)} segments, detected language: {detected_language}")
    return segments_list, detected_language, info

def save_transcription(segments,input_file):
    logger = logging.getLogger(__name__)

    if isinstance(input_file, Path):
        file_name = input_file.stem
    else:
        file_name = Path(input_file).stem

    transcription_file = output_folder / f"transcription_{file_name}.txt"
    with open(transcription_file, 'w', encoding="utf-8") as f:
        for segment in segments:
            start_min = int(segment.start // 60)
            start_sec = int(segment.start % 60)
            end_min = int(segment.end // 60)
            end_sec = int(segment.end % 60)
            f.write(f"[{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}] {segment.text.strip()}\n")
    logger.info(f"Saved transcription to {transcription_file}")
    return transcription_file
