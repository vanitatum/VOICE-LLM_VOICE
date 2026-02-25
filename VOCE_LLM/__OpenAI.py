import json
import os
import requests
from pathlib import Path #파일 경로 구하기

from datetime import datetime #리얼 타임 구하기

import sounddevice as sd #음성 녹음

import whisper # Speech To Text AI
from scipy.io.wavfile import write #.wav 확장자 라이브러리

import pyttsx3 #Text To Speech

from tqdm import tqdm # 간지용 게이지 바

import time # 대기 함수용 라이브러리

sd.default.device = 1 # 녹음 장치 설정

InputMode = 1 # 1 : Vocie / 2 : Text # 프롬포트 입력 모드 음성, 채팅



url = "http://localhost:11434/api/generate"

engine = pyttsx3.init() # TTs 음성 엔진

base_dir = Path(__file__).parent
Log_path = base_dir / "Log"
files = os.listdir(Log_path)

BeforeFileLen = int(len(files))
AfterFileLen = BeforeFileLen + 1

Before_path = base_dir / "Log" / f"{BeforeFileLen}.txt"
After_path = base_dir / "Log" / f"{AfterFileLen}.txt"

if BeforeFileLen == 0: # 과거 로그 파일이 없을 경우.
    with open(After_path, "w+", encoding="utf-8") as ef:
        ef.write("과거 대화 기록이 없습니다.")
    Before_path = base_dir / "Log" / "1.txt"

Setting_path = base_dir / "Setting.txt"
with open(Setting_path, "r", encoding="utf-8") as Setting:
    Setting = Setting.read()


with open(Before_path, "r", encoding="utf-8") as f:
    output_base = "AI의 마지막 응답 (이것에 대해 먼저 언급하지 말 것.)" + str(f.read())

# Record

def InputRecordStart():
    VoiceSeconds = int(input("녹음 시간(초) 입력 : "))
    if VoiceSeconds >= 1:
        duration = VoiceSeconds # 녹음 시간(s)
        print("녹음 시작")
        recording = sd.rec(int(samplerate * duration), samplerate = samplerate, channels=1, dtype='int16')

        tqdmTick = VoiceSeconds / 100 # 게이지 시간 계산.
        for i in tqdm(range(100)):
            time.sleep(tqdmTick)

        sd.wait() # 녹화 종료 대기
        print("녹음 끝")
        write(fr"{sound_path}", samplerate, recording)
    else:
        exit()
    # STT
    stt_result = model.transcribe(fr"{sound_path}")
    input_prompt = stt_result["text"]

    Choose = input("해당 프롬포트가 맞습니까? \n프롬포트 : " + input_prompt + "\nTrue/False : ") #문자로 변환된 음성 출력 & 질문

    if Choose == "True":
        Choose = True
    else:
        Choose = False

    return input_prompt, Choose


if InputMode == 1: # 음성 녹음 프롬포트

    samplerate = 16000 #샘플링 HZ
    sound_path = base_dir / "voice.wav"

    model = None # 모델을 1회만 부르기 위한 처리 구문. (STT) 구조상 이곳 위치
    if model is None:
        model = whisper.load_model("base")

    While = True
    while While:
        input_prompt, Choose = InputRecordStart()

        if Choose == True:
            last_prompt = Setting, output_base, input_prompt # 최최최종 삽입될 프롬포트

            payload = { # API에게 패킷 전송
                "model": "gemma2:9b",
                "prompt": f"{last_prompt}",
                "stream": False
            }
            While = False
        else:
            time.sleep(0.5)


if InputMode == 2:
    input_prompt = input("프롬포트 : ")
    last_prompt = Setting, output_base, input_prompt

    payload = { # API에게 패킷 전송
        "model": "gemma2:9b",
        "prompt": f"{last_prompt}",
        "stream": False
    }

# input_prompt = input("프롬포트 : ") # 채팅으로 프롬포트 입력

# API 죽어있을 경우 예외 처리 구문

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

# 해당 질문 & 응답 등의 정보를 LOG에 저장
with open(After_path, "w+", encoding="utf-8") as f:
    f.write("프롬포트 : " + input_prompt + "\n응답 : " + respon + "\n응답 시각 : " + str(datetime.now()))


# AI 응답 TTS 출력 구문
engine.say(respon)
engine.runAndWait()

# 테스트용 AI 입력,출력 토큰 출력 구문.
# LastTokenData = ["입력 토큰:", result.get("prompt_eval_count")],["출력 토큰:", result.get("eval_count")]
# print(LastTokenData)
