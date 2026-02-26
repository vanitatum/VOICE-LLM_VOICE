import os
from pathlib import Path # 파일 경로 구하기

from datetime import datetime # 리얼 타임 구하기

import whisper # Speech To Text AI

import pyttsx3 # Text To Speech

import time # 대기 함수용 라이브러리

import AiPacket as AI # AI 패킷 주고받기용 함수

import RecordToText as RTT # 음성 녹음 후 메시지로 받기.



base_dir = Path(__file__).parent

sound_path = base_dir / "voice.wav"


Arrange_Log_path = base_dir / "ArrangeLog"

if not os.path.exists(Arrange_Log_path): # 로그 파일 없을 경우
    os.makedirs(base_dir / "Log")
    os.makedirs(base_dir / "ArrangeLog")
    base_dir = Path(__file__).parent
    Arrange_Log_path = base_dir / "ArrangeLog"




InputMode = 1 # 1 : Vocie / 2 : Text # 프롬포트 입력 모드 음성, 채팅

engine = pyttsx3.init() # TTs 음성 엔진

Log_path = base_dir / "Log"
files = os.listdir(Log_path)

BeforeFileLen = int(len(files))
AfterFileLen = BeforeFileLen + 1

Before_path = base_dir / "Log" / f"{BeforeFileLen}.txt"
After_path = base_dir / "Log" / f"{AfterFileLen}.txt"

Arrange_Log_Token = 3 # x번째 턴마다 최근 x개의 로그를 정리해 요약.

Arrange_Log_Folder_len = len(os.listdir(Arrange_Log_path)) + 1 # 요약 로그 폴더 내 파일 갯수 구하기, 1 = 로그 없는 상태

# 로그 정리 로그 생성 함수
def LogArrange(i): # x : 정리할 최근 로그의 갯수. i = 5 의 경우 최근 5개를 정리 후 저장
    if i > BeforeFileLen: # 로그 갯수가 최근 로그보다 많을 경우
        i = BeforeFileLen # 모든 로그를 범위로 가져감

    # 종합 과거 로그 설정
    TotalBefore_Log = ""
    x = BeforeFileLen

    while i > 0:
        Before_path = base_dir / "Log" / f"{x}.txt"

        with open(Before_path, "r", encoding="utf-8") as Current_Log:
            Current_Log = str(Current_Log.read())

        x = (BeforeFileLen - i) + 1 #가져올 로그 넘버 계산
        y = str(i)

        TotalBefore_Log = f"{TotalBefore_Log}{y} : {Current_Log}\n"

        i -= 1

    AISTR = AI.api(f"해당 기록의 내용을 요약해줘.\n{TotalBefore_Log}") # 요약 내용
    ArrangeLogFile_path = Arrange_Log_path  / f"{Arrange_Log_Folder_len}.txt" # 요약 로그 저장 위치
    
    with open(ArrangeLogFile_path, "w+", encoding="utf-8") as ArrangeLogFile:
        ArrangeLogFile.write(f"{AISTR}")

if BeforeFileLen % Arrange_Log_Token == 0: # 특정 턴마다 로그 요약
    if BeforeFileLen < Arrange_Log_Token: # 최대 토큰보다 로그의 갯수가 적을 경우 제한.
        Arrange_Log_Token = BeforeFileLen
    if BeforeFileLen > 0:
        LogArrange(Arrange_Log_Token)

if Arrange_Log_Folder_len > 1: # 요약 로그가 1개 이상 있을 경우, 가장 최근 요약된 로그 읽어냄
    Arrange_Log = Arrange_Log_path / f"{Arrange_Log_Folder_len}.txt"

    with open(Arrange_Log, "r", encoding="utf-8") as Arrange_Log:
        Arrange_Log = Arrange_Log.read()


if BeforeFileLen == 0: # 과거 로그 파일이 없을 경우.
    with open(After_path, "w+", encoding="utf-8") as ef:
        ef.write("과거 대화 기록이 없습니다.")
    Before_path = base_dir / "Log" / "1.txt"

Setting_path = base_dir / "Setting.txt" # 설정 파일 가져오기
with open(Setting_path, "r", encoding="utf-8") as Setting:
    Setting = Setting.read()

if Arrange_Log_Folder_len > 1: # 가장 최근 요약 로그가 존재할 시 프롬포트에 포함
    with open(Before_path, "r", encoding="utf-8") as f:
        output_base = f"가장 최근 대화 기록 요약 : {Arrange_Log}\nAI의 마지막 응답 (이것에 대해 먼저 언급하지 말 것.)" + str(f.read())
else: # 요약 로그가 없을 경우 프롬포트만 전송.
    with open(Before_path, "r", encoding="utf-8") as f:
        output_base = "AI의 마지막 응답 (이것에 대해 먼저 언급하지 말 것.)" + str(f.read())




if InputMode == 1: # 음성 녹음 프롬포트

    model = None # 모델을 1회만 부르기 위한 처리 구문. (STT) 구조상 이곳 위치
    if model is None:
        model = whisper.load_model("base")

    CurrentLoop = True
    while CurrentLoop == True:
        input_prompt, Choose = RTT.RecordStart(sound_path, model)

        if Choose == True:
            last_prompt = f"{Setting} \n {output_base} \n {input_prompt}" # 최최최종 삽입될 프롬포트

            respon = AI.api(last_prompt)
            CurrentLoop = False
        else:
            time.sleep(0.5)


if InputMode == 2: # 채팅 프롬포트
    input_prompt = input("프롬포트 : ")
    last_prompt = f"{Setting} \n {output_base} \n {input_prompt}"
    respon = AI.api(last_prompt)


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