"""
인덱스 생성, 로드, 증분 업데이트 관리
최적화된 인덱싱 전략으로 성능 향상
"""
import os
import time
from pathlib import Path
from typing import List, Optional
import logging

import faiss
from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from config.settings import (
    STORAGE_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_DIM, 
    FAISS_NLIST, FAISS_NPROBE, SIMILARITY_TOP_K
)
from core.document_manager import DocumentManager
from core.embedding_cache import EmbeddingCache
from loaders.custom_loaders import CustomDocumentLoader

logger = logging.getLogger(__name__)

class IndexManager:
    """인덱스 생성 및 관리 클래스"""
    
    def __init__(self, storage_dir: Path = STORAGE_DIR):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # 컴포넌트 초기화
        self.doc_manager = DocumentManager()
        self.embedding_cache = EmbeddingCache()
        self.loader = CustomDocumentLoader()
        
        # 설정 적용
        Settings.chunk_size = CHUNK_SIZE
        Settings.chunk_overlap = CHUNK_OVERLAP
        
        # 인덱스 상태
        self._index: Optional[VectorStoreIndex] = None
        self._embed_model: Optional[HuggingFaceEmbedding] = None
    
    def _get_embed_model(self) -> HuggingFaceEmbedding:
        """임베딩 모델 로드 (lazy loading)"""
        if self._embed_model is None:
            logger.info("임베딩 모델 로드 중...")
            start_time = time.time()
            self._embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info(f"임베딩 모델 로드 완료: {time.time() - start_time:.2f}초")
        return self._embed_model
    
    def _create_vector_store(self) -> FaissVectorStore:
        """FAISS 벡터 저장소 생성"""
        # IVF (Inverted File) 인덱스 생성으로 빠른 검색
        quantizer = faiss.IndexFlatL2(EMBEDDING_DIM)
        faiss_index = faiss.IndexIVFFlat(quantizer, EMBEDDING_DIM, FAISS_NLIST)
        faiss_index.nprobe = FAISS_NPROBE
        
        return FaissVectorStore(faiss_index=faiss_index)
    
    def _load_existing_index(self) -> Optional[VectorStoreIndex]:
        """기존 인덱스 로드"""
        try:
            if not (self.storage_dir / "docstore.json").exists():
                return None
            
            logger.info("기존 인덱스 로드 중...")
            start_time = time.time()
            
            storage_context = StorageContext.from_defaults(persist_dir=str(self.storage_dir))
            index = load_index_from_storage(
                storage_context, 
                embed_model=self._get_embed_model()
            )
            
            logger.info(f"인덱스 로드 완료: {time.time() - start_time:.2f}초")
            return index
            
        except Exception as e:
            logger.error(f"인덱스 로드 실패: {e}")
            return None
    
    def _create_new_index(self, documents: List[Document]) -> VectorStoreIndex:
        """새 인덱스 생성"""
        logger.info(f"새 인덱스 생성 중... ({len(documents)}개 문서)")
        start_time = time.time()
        
        vector_store = self._create_vector_store()
        embed_model = self._get_embed_model()
        
        # 임베딩 캐시 활용한 인덱스 생성
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            embed_model=embed_model,
            show_progress=True
        )
        
        # 인덱스 저장
        index.storage_context.persist(persist_dir=str(self.storage_dir))
        
        logger.info(f"인덱스 생성 완료: {time.time() - start_time:.2f}초")
        return index
    
    def _update_index_incremental(self, index: VectorStoreIndex, new_documents: List[Document]) -> VectorStoreIndex:
        """증분 인덱스 업데이트"""
        if not new_documents:
            return index
        
        logger.info(f"증분 인덱스 업데이트 중... ({len(new_documents)}개 문서)")
        start_time = time.time()
        
        # 새 문서를 기존 인덱스에 추가
        for doc in new_documents:
            index.insert(doc)
        
        # 업데이트된 인덱스 저장
        index.storage_context.persist(persist_dir=str(self.storage_dir))
        
        logger.info(f"증분 업데이트 완료: {time.time() - start_time:.2f}초")
        return index
    
    def create_or_update_index(self, force_rebuild: bool = False) -> VectorStoreIndex:
        """
        인덱스 생성 또는 업데이트
        
        Args:
            force_rebuild: 강제 재빌드 여부
            
        Returns:
            VectorStoreIndex: 생성/업데이트된 인덱스
        """
        # 문서 변경사항 스캔
        new_files, modified_files, deleted_files = self.doc_manager.scan_documents()
        
        # 기존 인덱스 로드 시도
        existing_index = None if force_rebuild else self._load_existing_index()
        
        # 인덱스 생성/업데이트 전략 결정
        if existing_index is None or deleted_files:
            # 새 인덱스 생성 (삭제된 파일이 있거나 기존 인덱스 없음)
            all_files = self.doc_manager.get_all_indexed_files()
            if all_files:
                documents = self.loader.load_documents(all_files)
                self._index = self._create_new_index(documents)
            else:
                logger.warning("인덱싱할 문서가 없습니다.")
                return None
        
        elif new_files or modified_files:
            # 증분 업데이트
            files_to_update = new_files + modified_files
            new_documents = self.loader.load_documents(files_to_update)
            self._index = self._update_index_incremental(existing_index, new_documents)
            
            # 인덱싱 완료 표시
            for file_path in files_to_update:
                self.doc_manager.mark_as_indexed(file_path)
        
        else:
            # 변경사항 없음
            logger.info("문서 변경사항이 없어 기존 인덱스를 사용합니다.")
            self._index = existing_index
        
        return self._index
    
    def get_query_engine(self, llm, similarity_top_k: int = SIMILARITY_TOP_K):
        """쿼리 엔진 생성"""
        if self._index is None:
            raise ValueError("인덱스가 생성되지 않았습니다. create_or_update_index()를 먼저 호출하세요.")
        
        return self._index.as_query_engine(
            llm=llm,
            similarity_top_k=similarity_top_k
        )
    
    def get_index_stats(self) -> dict:
        """인덱스 통계 정보"""
        if self._index is None:
            return {"status": "인덱스 없음"}
        
        # 벡터 저장소 통계
        vector_store = self._index._vector_store
        if hasattr(vector_store, '_faiss_index'):
            faiss_index = vector_store._faiss_index
            return {
                "total_vectors": faiss_index.ntotal,
                "dimension": faiss_index.d,
                "is_trained": faiss_index.is_trained,
                "indexed_files": len(self.doc_manager.get_all_indexed_files())
            }
        
        return {"status": "통계 정보 없음"}
    
    def clear_index(self):
        """인덱스 및 캐시 초기화"""
        logger.info("인덱스 및 캐시 초기화 중...")
        
        # 인덱스 파일 삭제
        if self.storage_dir.exists():
            import shutil
            shutil.rmtree(self.storage_dir)
            self.storage_dir.mkdir(exist_ok=True)
        
        # 캐시 초기화
        self.embedding_cache.clear_cache()
        
        # 인스턴스 변수 초기화
        self._index = None
        
        logger.info("초기화 완료")