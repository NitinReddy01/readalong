
# AI Pronunciation Trainer 
This tool uses AI to evaluate your pronunciation so you can improve it and be understood more clearly. 


## Installation 
To run the program locally, you need to install the requirements and run the main python file:
```
pip install -r requirements.txt
python main.py
```

# 🗣️ AI Pronunciation Trainer – API Documentation

This API provides pronunciation evaluation by analyzing audio input against the expected phrase. It returns accuracy scores, phonetic comparisons, and error categories.

## 🚀 Endpoint

**POST** `/GetAccuracyFromRecordedAudio`

---

## 📥 Request

### Headers
```http
Content-Type: application/json
```
## body
```

input
{
  "title": "resonance",
  "language": "en",
  "base64Audio": "data:audio/webm;base64,GkXf59...AAA=="
} 



```
## Response 
```
output 
{
  "real_transcript": "resonance.",
  "ipa_transcript": "\\u02c8r\\u025bz\\u0259n\\u0259ns.",
  "pronunciation_accuracy": "100",
  "real_transcripts": "resonance.",
  "matched_transcripts": "resonance.",
  "real_transcripts_ipa": "\\u02c8r\\u025bz\\u0259n\\u0259ns.",
  "matched_transcripts_ipa": "\\u02c8r\\u025bz\\u0259n\\u0259ns.",
  "pair_accuracy_category": "0",
  "is_letter_correct_all_words": "11111111"
}
```

You'll also need ffmpeg, which you can download from here https://ffmpeg.org/download.html. On Windows, it may be needed to add the ffmpeg "bin" folder to your PATH environment variable. On Mac, you can also just run "brew install ffmpeg".

You should be able to run it locally without any major issues as long as you’re using a recent python 3.X version.  


## Disclaimer 
This is a simple project that I made in my free time with the goal to be useful to some people. It is not perfect, thus be aware that some small bugs may be present. In case you find something is not working, all feedback is welcome, and issues may be addressed depending on their severity.


#### Backend 
As long as your language is supported by Whisper, you need only a database and small changes in key files:

1. Add your language identifier to the "lambdaGetSample.py" file
2. Add a .csv file with your text database in the "./databases" folder, following the naming convention 
3. Add a corresponding phonem model in the "RuleBasedModels.py", you likely need only to give the language code to Epitran and possibly correct some characters with a wrapper 
4. Add your trainer to "lambdaSpeechToScore.py" with the correct language code

If you language is not supported by Whisper, you need to have an Speech-To-Text model and add it to the "getASRModel" function in "models.py", and it needs to implement the "IASRModel" interface. Besides this, you need to do the same as above.
 