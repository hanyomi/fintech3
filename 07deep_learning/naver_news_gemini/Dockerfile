FROM python:3.10-slim

# 기본 패키지 업데이트 및 필수 라이브러리 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 앱 디렉토리 생성
WORKDIR /app

# requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY app.py .
COPY .env_gemini .

# 컨테이너에서 웹 서비스 포트 오픈
EXPOSE 7860

# 실행
CMD ["python", "app.py"]
