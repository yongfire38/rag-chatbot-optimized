"""
임베딩 결과 캐시 관리
중복 임베딩 계산 방지로 성능 최적화
"""
import pickle
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from config.settings import CACHE_DIR, EMBEDDING_CACHE_SIZE

logger = logging.getLogger(__name__)

class EmbeddingCache:
    """임베딩 결과 캐시 관리 클래스"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR, max_size: int = EMBEDDING_CACHE_SIZE):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "embedding_cache.pkl"
        self.max_size = max_size
        self.cache: Dict[str, Any] = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """캐시 파일 로드"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    cache = pickle.load(f)
                    logger.info(f"임베딩 캐시 로드 완료: {len(cache)}개 항목")
                    return cache
            except Exception as e:
                logger.error(f"캐시 로드 실패: {e}")
        return {}
    
    def _save_cache(self):
        """캐시 파일 저장"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            logger.debug(f"캐시 저장 완료: {len(self.cache)}개 항목")
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
    
    def _get_text_hash(self, text: str) -> str:
        """텍스트 해시값 생성"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """캐시에서 임베딩 조회"""
        text_hash = self._get_text_hash(text)
        return self.cache.get(text_hash)
    
    def store_embedding(self, text: str, embedding: List[float]):
        """임베딩을 캐시에 저장"""
        text_hash = self._get_text_hash(text)
        
        # 캐시 크기 관리 (LRU 방식)
        if len(self.cache) >= self.max_size:
            # 가장 오래된 항목 제거
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug("캐시 크기 초과, 오래된 항목 제거")
        
        self.cache[text_hash] = embedding
        
        # 주기적으로 캐시 저장 (10개마다)
        if len(self.cache) % 10 == 0:
            self._save_cache()
    
    def clear_cache(self):
        """캐시 초기화"""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info("임베딩 캐시 초기화 완료")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계 정보"""
        return {
            'total_entries': len(self.cache),
            'max_size': self.max_size,
            'cache_file_exists': self.cache_file.exists()
        }