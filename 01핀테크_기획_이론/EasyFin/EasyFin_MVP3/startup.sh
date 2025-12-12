#!/bin/sh
# 데이터베이스가 준비될 때까지 잠시 대기
sleep 10
# FastAPI 서버 실행
# --host 0.0.0.0으로 설정해야 Docker 외부에서 접근 가능합니다.
uvicorn backend.main:app --host 0.0.0.0 --port 8000