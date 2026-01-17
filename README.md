# Audio Project

An audio transcription and translation tool that uses Whisper for transcription and supports multiple translation services (Google Translate, DeepL).

## Features

- Audio transcription using Faster Whisper models
- Multi-language translation support
- Support for Google Translate (free) and DeepL (requires API key)
- Configurable model sizes and output languages

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the project**
   - Copy `mini_config.yml.example` to `mini_config.yml`
   - Edit `mini_config.yml` and add your DeepL API key (optional, only if using DeepL)
   - Update the folder paths as needed

3. **Run the application**
   ```bash
   python main.py
   ```

## Configuration

The `mini_config.yml` file contains all configuration settings:
- Input/output folder paths
- DeepL API key (if using DeepL translation)
- Available translation languages
- Whisper model sizes

**Note:** Never commit `mini_config.yml` to version control as it contains sensitive API keys. Use `mini_config.yml.example` as a template.

## Project Structure

```
Gitver Audio_project/
├── input/              # Place your .mp3 audio files here
├── output/             # Transcription files are saved here
├── translated/         # Translated text files are saved here
├── main.py            # Main entry point
├── mp3.py             # Audio transcription module
├── translate.py       # Translation module
├── mini_config.yml    # Configuration file (not in git)
└── requirements.txt   # Python dependencies
```

## Usage

1. Place your audio file (.mp3) in the `input/` folder
2. Run `python main.py`
3. Select your preferred Whisper model size
4. Choose the output language for translation
5. Select translation service (Google or DeepL)
6. Find the transcription in `output/` and translation in `translated/`

## Requirements

- Python 3.7+
- See `requirements.txt` for all dependencies
