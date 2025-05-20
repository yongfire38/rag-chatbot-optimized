"""
애플리케이션 설정 관리
전역 변수와 상수를 중앙화하여 관리
"""
import os
from pathlib import Path

# 기본 경로 설정
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"
STORAGE_DIR = BASE_DIR / "storage"
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / ".cache"

# 인덱싱 설정
CHUNK_SIZE = 256
CHUNK_OVERLAP = 50
SIMILARITY_TOP_K = 2

# 벡터 저장소 설정
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 차원
FAISS_NLIST = 100
FAISS_NPROBE = 10

# LLM 설정
LLM_MODEL_PATH = MODELS_DIR / "llama-2-7b-chat.Q4_K_M.gguf"
LLM_TEMPERATURE = 0.7
LLM_MAX_NEW_TOKENS = 512
LLM_CONTEXT_WINDOW = 2048

# 캐시 설정
DOCUMENT_CACHE_TTL = 3600  # 1시간
EMBEDDING_CACHE_SIZE = 1000

# 로깅 설정
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 지원하는 파일 확장자
SUPPORTED_EXTENSIONS = {'.pdf', '.csv', '.md', '.docx', '.json'}