import os
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from pydantic import BaseModel
from .database import Asset, MarketProduct, CommunityPost, get_db, init_db
from pydantic import BaseModel

# Pydantic 모델 (API 응답 데이터 구조)
class AssetSummary(BaseModel):
    total_asset: float
    asset_breakdown: List[Dict[str, Any]]
    accounts: List[Dict[str, Any]]
    ai_briefing: str # AI 브리핑 필드 추가 (FR-A01)

class ProductBase(BaseModel):
    id: int
    name: str
    code: str
    category: str
    risk_level: str
    expected_return: float | None
    schedule: str

class PostBase(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str # 응답 시 문자열로 변환

# FastAPI 앱 생성 및 초기 DB 설정
app = FastAPI()
init_db() # worker=1 조건 하에서 최초 실행 시 DB 스키마 생성 및 초기 데이터 삽입

# 홈 화면 - 자산 API (FR-010, FR-011, FR-012)
@app.get("/api/v1/home/assets", response_model=AssetSummary)
def get_asset_summary(db: Session = Depends(get_db)):
    assets = db.query(Asset).all()
    if not assets:
        raise HTTPException(status_code=404, detail="No assets found")

    total_asset = sum(a.amount for a in assets)
    
    # FR-011: 자산 비중 계산
    breakdown_query = db.query(Asset.asset_type, func.sum(Asset.amount).label('total')).group_by(Asset.asset_type).all()
    asset_breakdown = [
        {"type": row.asset_type, "amount": row.total, "percentage": (row.total / total_asset) * 100 if total_asset > 0 else 0}
        for row in breakdown_query
    ]
    # FR-A01: AI 자산 브리핑 (가상 데이터)
    ai_briefing = "AI 브리핑: 지난 7일간 주식 자산이 3.5% 상승했습니다. 특히 ETF 성과가 돋보이며, 리스크 노출은 '보통' 수준입니다. (FR-A01)"
    
    return AssetSummary(
        total_asset=total_asset,
        asset_breakdown=asset_breakdown,
        accounts=accounts,
        ai_briefing=ai_briefing # AI 브리핑 데이터 추가
    )
    # FR-012: 계좌 요약
    accounts = [
        {"financial_company": a.financial_company, "account_name": a.account_name, "balance": a.amount}
        for a in assets
    ]
    
    # FR-A01 (향후): AI 자산 브리핑 (MVP에서는 가상으로 제공)
    ai_briefing = "AI 브리핑: 지난 7일간 주식 자산이 3.5% 상승했습니다. 특히 AETF의 성과가 돋보입니다."
    
    return AssetSummary(
        total_asset=total_asset,
        asset_breakdown=asset_breakdown,
        accounts=accounts,
        ai_briefing=ai_briefing # Pydantic 모델에는 없지만 응답 데이터에 추가
    )

# 마켓 화면 - 상품 목록 API (FR-021, FR-020 필터링)
@app.get("/api/v1/market/products", response_model=List[ProductBase])
def get_market_products(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(MarketProduct)
    if category:
        query = query.filter(MarketProduct.category == category)
    
    products = query.all()
    return products

# 커뮤니티 화면 - 게시글 목록 API (FR-040)
@app.get("/api/v1/community/posts", response_model=List[PostBase])
def get_community_posts(db: Session = Depends(get_db)):
    # 최신 순으로 정렬
    posts = db.query(CommunityPost).order_by(CommunityPost.created_at.desc()).all()
    # Pydantic 모델 호환을 위해 created_at 형식 변경
    return [
        PostBase(
            id=p.id,
            title=p.title,
            content=p.content,
            author=p.author,
            created_at=p.created_at.strftime("%Y-%m-%d %H:%M")
        ) for p in posts
    ]

# 라이브 화면 - 라이브 목록 API (FR-030)
@app.get("/api/v1/live/list")
def get_live_list():
    return {
        " 진행중": [
            {"id": 1, "title": "지금! 엔비디아 주가 폭락, 어떻게 대응할까?", "expert": "김투자 전문가", "status": "LIVE", "viewer": 1500}
        ],
        " 예정": [
            {"id": 2, "title": "퇴근 후 공모주 청약 A-Z", "expert": "최부자 셀러", "status": "2025.12.15 19:00 예정", "viewer": 0}
        ],
        "다시보기": [
            {"id": 3, "title": "2026 국고채, 매수 타이밍 잡기", "expert": "박금융 전문가", "status": "다시보기", "viewer": 3000}
        ],
        # FR-013 추천 라이브용 데이터 추가
        "recommended_live": [
             {"id": 1, "title": "🔴 [LIVE] 엔비디아 주가 폭락, 어떻게 대응할까?", "expert": "김투자 전문가"}
        ]
    }