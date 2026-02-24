import json
import os
import requests
from pathlib import Path #파일 경로 구하기

from datetime import datetime #리얼 타임 구하기

import sounddevice as sd #음성 녹음

import whisper # Speech To Text AI
from scipy.io.wavfile import write #.wav 확장자 라이브러리

import pyttsx3 #Text To Speech



sd.default.device = 1 # 녹음 장치

url = "http://localhost:11434/api/generate"

engine = pyttsx3.init() # TTs 음성 엔진

base_dir = Path(__file__).parent
Log_path = base_dir / "Log"
files = os.listdir(Log_path)

BeforeFileLen = int(len(files))
AfterFileLen = BeforeFileLen + 1

Before_path = base_dir / "Log" / f"{BeforeFileLen}.txt"
After_path = base_dir / "Log" / f"{AfterFileLen}.txt"

if BeforeFileLen == 0: # 로그 파일이 아에 없을 경우.
    ef = open(After_path, "w+", encoding="utf-8")
    ef.write("과거 대화 기록이 없습니다.")
    Before_path = base_dir / "Log" / "1.txt"
    ef.close()

Setting_path = base_dir / "Setting.txt"
Setting = open(Setting_path, "r", encoding="utf-8")


f = open(Before_path, "r", encoding="utf-8")
output_base = "AI의 마지막 응답 (이것에 대해 먼저 언급하지 말 것.)", f.read()

# Record
samplerate = 16000 #샘플링 HZ
duration = 2 # 녹음 시간(s)

sound_path = base_dir / "voice.wav"

print("녹음 시작")

recording = sd.rec(int(samplerate * duration), samplerate = samplerate, channels=1, dtype='int16')

sd.wait()

print("녹음 끝")

write(fr"{sound_path}", samplerate, recording)

# STT

model = None
if model is None:
    model = whisper.load_model("base")
stt_result = model.transcribe(fr"{sound_path}")
input_prompt = stt_result["text"]

print("프롬포트 : ", input_prompt)

# input_prompt = input("프롬포트 : ") # 채팅으로 프롬포트 입력

last_prompt = Setting.read(), output_base, input_prompt
Setting.close()

payload = {
    "model": "deepseek-r1:8b",
    "prompt": f"{last_prompt}",
    "stream": False
}

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()

    result = response.json()
    
    respon = result["response"]
except requests.RequestException as e:
    print("API 오류:", e)
if respon is None:
    exit()

print("응답:", respon)

f = open(After_path, "w+", encoding="utf-8")
f.write("프롬포트 : " + input_prompt + "\n응답 : " + respon + "\n응답 시각 : " + str(datetime.now()))
f.close()

engine.say(respon)
engine.runAndWait()

# LastTokenData = ["입력 토큰:", result.get("prompt_eval_count")],["출력 토큰:", result.get("eval_count")]
# print(LastTokenData)