import time

from tqdm import tqdm # 간지용 게이지 바

from pathlib import Path # 파일 경로 구하기

from scipy.io.wavfile import write #.wav 확장자 라이브러리

import sounddevice as sd # 음성 녹음


sd.default.device = 1 # 녹음 장치 설정


samplerate = 16000 #샘플링 HZ


# Record
def RecordStart(sound_path, model):
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

