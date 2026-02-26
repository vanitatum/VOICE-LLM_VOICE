import requests
import json


url = "http://localhost:11434/api/generate"

AiModel = "gemma2:9b" # AI 엔진

# AI 패킷 전송 함수, return : AI 응답
def api(prompt):
    payload = { # AI API에 패킷 전송
        "model": AiModel,
        "prompt": f"{prompt}",
        "stream": False
    }

    try: # AI 대답 패킷 응답
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
    
        respon = result["response"]

        return respon

    except requests.RequestException as e: # API 죽었을 경우 예외 처리
        print("API 오류:", e)
    if respon is None:
        exit()