"""
핵심 RAG 시스템 패키지

이 패키지는 RAG 챗봇의 핵심 기능을 제공합니다:
- 문서 관리 및 변경 감지
- 인덱스 생성/로드/업데이트 
- 임베딩 캐시 관리

Example:
    from core import IndexManager, DocumentManager, EmbeddingCache
    
    # 인덱스 매니저 초기화
    index_manager = IndexManager()
    index = index_manager.create_or_update_index()
    
    # 문서 변경 감지
    doc_manager = DocumentManager()
    new_files, modified_files = doc_manager.scan_documents()
"""

# 핵심 클래스들을 패키지 레벨로 import
from .document_manager import DocumentManager
from .index_manager import IndexManager
from .embedding_cache import EmbeddingCache

# 패키지 초기화 시 로깅 설정
import logging

# 패키지 로거 설정
logger = logging.getLogger(__name__)
logger.info("Core RAG system package initialized")

# 패키지 메타데이터
__version__ = "1.0.0"
__author__ = "RAG Chatbot Team"
__description__ = "Core functionality for RAG chatbot system"

# 공개 API 정의 - 이 리스트의 클래스들만 'from core import *'로 가져올 수 있음
__all__ = [
    "DocumentManager",
    "IndexManager", 
    "EmbeddingCache",
]

# 패키지 레벨 상수
CORE_VERSION = "1.0.0"
SUPPORTED_OPERATIONS = [
    "document_scan",
    "index_creation", 
    "index_update",
    "embedding_cache",
    "performance_monitor"
]

# 패키지 레벨 설정
DEFAULT_INDEX_CONFIG = {
    "chunk_size": 256,
    "chunk_overlap": 50,
    "similarity_top_k": 2
}

# 초기화 시 필요한 디렉토리 생성
def _ensure_directories():
    """필요한 디렉토리들이 존재하는지 확인하고 생성"""
    from config import STORAGE_DIR, CACHE_DIR
    import os
    
    dirs_to_create = [STORAGE_DIR, CACHE_DIR]
    
    for directory in dirs_to_create:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

# 패키지 로드 시 디렉토리 확인
_ensure_directories()

# 패키지 레벨 유틸리티 함수
def get_core_info():
    """코어 패키지 정보 반환"""
    return {
        "version": __version__,
        "description": __description__,
        "supported_operations": SUPPORTED_OPERATIONS,
        "default_config": DEFAULT_INDEX_CONFIG
    }