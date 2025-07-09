import torch 
from transformers import pipeline
from ModelInterfaces import IASRModel
from typing import Union
import numpy as np 

class WhisperASRModel(IASRModel):
    def __init__(self, model_name="openai/whisper-tiny"):
        self.asr = pipeline("automatic-speech-recognition", model=model_name, return_timestamps="word")
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = 16000

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]):
        # 'audio' can be a path to a file or a numpy array of audio samples.
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        result = self.asr(audio[0])
        self._transcript = result["text"]
        self._word_locations = [{"word": word_info["text"], 
                     "start_ts": word_info["timestamp"][0] * self.sample_rate if word_info["timestamp"][0] is not None else None,
                     "end_ts": (word_info["timestamp"][1] * self.sample_rate if word_info["timestamp"][1] is not None else (word_info["timestamp"][0] + 1) * self.sample_rate),
                     "tag": "processed"} for word_info in result["chunks"]]

    def getTranscript(self) -> str:
        return self._transcript

    def getWordLocations(self) -> list:
        
        return self._word_locations

# import openai
# import numpy as np
# import torch
# import tempfile
# import soundfile as sf
# from typing import Union

# # Create a client instance

# class WhisperASRModel:
#     def __init__(self, model_name="whisper-1"):
#         self.model_name = model_name
#         self._transcript = ""
#         self._word_locations = []
#         self.sample_rate = 16000

#     def processAudio(self, audio: Union[np.ndarray, torch.Tensor]):
#         if isinstance(audio, torch.Tensor):
#             audio = audio.detach().cpu().numpy()

#         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
#             sf.write(f.name, audio[0], self.sample_rate)
#             audio_path = f.name

#         with open(audio_path, "rb") as audio_file:
#             response = client.audio.transcriptions.create(
#                 model="whisper-1",
#                 file=audio_file,
#                 response_format="verbose_json",
#                 timestamp_granularities=["word"]
#             )

#         self._transcript = response.text.strip()

#         self._word_locations = [
#             {
#                 "word": word_info["word"],
#                 "start_ts": int(word_info["start"] * self.sample_rate),
#                 "end_ts": int(word_info["end"] * self.sample_rate),
#                 "tag": "processed"
#             }
#             for segment in response.segments or []
#             for word_info in segment.words or []
#         ]

#     def getTranscript(self) -> str:
#         return self._transcript

#     def getWordLocations(self) -> list:
#         return self._word_locations
