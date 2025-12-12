import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 환경 변수에서 DB URL 로드
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://easyfin:easyfin@db:3306/easyfin_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB 접속 세션 관리 (FastAPI Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. 자산 모델 (FR-010: 총 자산, 자산 비중 표시)
class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    asset_type = Column(String(50), index=True) # 예: 주식, 예금, 현금
    amount = Column(Float)
    account_name = Column(String(100)) # 계좌 이름
    financial_company = Column(String(100)) # 금융사

# 2. 마켓 상품 모델 (FR-021: 상품 리스트 제공)
class MarketProduct(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    code = Column(String(50), unique=True)
    category = Column(String(50)) # 공모주, ETF, 채권, 리츠 (FR-020)
    risk_level = Column(String(20)) # 위험도
    expected_return = Column(Float)
    schedule = Column(String(255)) # 일정 정보 (FR-022)

# 3. 커뮤니티 게시글 모델 (FR-040: 게시글 목록)
class CommunityPost(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    content = Column(String(1000))
    author = Column(String(100))
    created_at = Column(DateTime, default=func.now())

# DB 스키마 생성 및 초기 데이터 삽입
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 초기 데이터 삽입 (가상 데이터)
    if db.query(Asset).count() == 0:
        db.add_all([
            Asset(asset_type="주식", amount=3500000.0, account_name="미래에셋 주식 계좌", financial_company="미래에셋"),
            Asset(asset_type="예금", amount=1200000.0, account_name="생활비 통장", financial_company="카카오뱅크"),
            Asset(asset_type="현금", amount=500000.0, account_name="EasyPay 잔액", financial_company="EasyPay"),
        ])
    
    if db.query(MarketProduct).count() == 0:
        db.add_all([
            MarketProduct(name="글로벌 AI 반도체 ETF", code="K001", category="ETF", risk_level="높음", expected_return=15.5, schedule="매일 거래 가능"),
            MarketProduct(name="2026년 만기 국고채", code="B001", category="채권", risk_level="낮음", expected_return=4.2, schedule="2026.12.31 만기"),
            MarketProduct(name="테크 스타트업 공모주", code="I001", category="공모주", risk_level="매우 높음", expected_return=None, schedule="2025.12.20 청약"),
        ])

    if db.query(CommunityPost).count() == 0:
        db.add_all([
            CommunityPost(title="AI 브리핑 기능 너무 편리하네요!", content="아침마다 자산 요약을 해주니 출근길에 확인하기 좋아요.", author="박지현"),
            CommunityPost(title="포트폴리오 진단 기능 써보신 분?", content="DIY 투자형인데 분석 리포트가 꽤 정확합니다.", author="김도훈"),
            CommunityPost(title="생활형 금융 기능 업데이트가 시급해요!", content="지출 관리가 기존 앱보다 아직 부족한 것 같아요.", author="최수정"),
        ])
    
    db.commit()
    db.close()