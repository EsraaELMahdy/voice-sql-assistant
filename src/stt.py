from faster_whisper import WhisperModel

from src import config

_model = None


def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
    return _model


def transcribe(audio_path, language=None, prompt=None):
    segments, info = get_model().transcribe(
        str(audio_path),
        language=language,
        initial_prompt=prompt,
        beam_size=config.WHISPER_BEAM_SIZE,
        vad_filter=True,
    )
    text = " ".join(segment.text.strip() for segment in segments)
    return {"text": text.strip(), "language": info.language}

