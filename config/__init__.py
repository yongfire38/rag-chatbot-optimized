"""
설정 관리 패키지

이 패키지는 애플리케이션의 전역 설정과 상수를 관리합니다.

Example:
    from config import settings
    print(settings.CHUNK_SIZE)
    
    # 또는
    from config.settings import CHUNK_SIZE, STORAGE_DIR
"""

# 주요 설정 모듈에서 자주 사용되는 상수들을 패키지 레벨로 가져옴
from .settings import (
    # 경로 설정
    BASE_DIR,
    DOCS_DIR,
    STORAGE_DIR,
    MODELS_DIR,
    CACHE_DIR,
    
    # 인덱싱 설정
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SIMILARITY_TOP_K,
    
    # 벡터 저장소 설정
    EMBEDDING_DIM,
    FAISS_NLIST,
    FAISS_NPROBE,
    
    # LLM 설정
    LLM_MODEL_PATH,
    LLM_TEMPERATURE,
    LLM_MAX_NEW_TOKENS,
    LLM_CONTEXT_WINDOW,
    
    # 지원 파일 형식
    SUPPORTED_EXTENSIONS,
)

# 패키지 메타데이터
__version__ = "1.0.0"
__author__ = "RAG Chatbot Team"
__description__ = "Configuration management for RAG Chatbot"

# 공개 API 정의
__all__ = [
    "BASE_DIR",
    "DOCS_DIR", 
    "STORAGE_DIR",
    "MODELS_DIR",
    "CACHE_DIR",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "SIMILARITY_TOP_K",
    "EMBEDDING_DIM",
    "FAISS_NLIST",
    "FAISS_NPROBE",
    "LLM_MODEL_PATH",
    "LLM_TEMPERATURE",
    "LLM_MAX_NEW_TOKENS",
    "LLM_CONTEXT_WINDOW",
    "SUPPORTED_EXTENSIONS",
]