# Speech-to-Text Project

This project is focused on transcribing audio into text using advanced speech recognition technology. The primary goal is to create high-quality text datasets from audio files for:

- Training Text-to-Speech (TTS) models.
- Fine-tuning Large Language Models (LLMs) on domain-specific data.

---

## Features

- **Arabic Speech Recognition**: Supports transcription of Arabic audio, including various dialects.
- **GPU Acceleration**: Leverages GPUs for faster processing using the Whisper model.

---

## Requirements

### Prerequisites
Ensure the following tools are installed:

- Python 3.8 or higher
- NVIDIA GPU with CUDA support (optional for acceleration)

### Dependencies
Install the required Python packages:

```bash
pip install git+https://github.com/openai/whisper.git torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```
2. Set up the Python environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```
3. Verify GPU availability (optional):
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

---

## Future Plans

- Add support for batch processing of audio files.
- Develop detailed usage examples and scripts.
- Explore integration with TTS and LLM fine-tuning pipelines.

---

## Contributing

Contributions are welcome! Feel free to suggest improvements or new features by opening an issue or submitting a pull request.

---

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the underlying ASR technology.

