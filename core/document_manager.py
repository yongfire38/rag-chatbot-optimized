"""
문서 변경 감지 및 관리 시스템
해시 기반 변경 감지로 불필요한 재처리 방지
"""
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

from config.settings import DOCS_DIR, CACHE_DIR

logger = logging.getLogger(__name__)

class DocumentManager:
    """문서 변경 감지 및 메타데이터 관리"""
    
    def __init__(self, docs_dir: Path = DOCS_DIR):
        self.docs_dir = Path(docs_dir)
        self.cache_dir = Path(CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "document_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """저장된 메타데이터 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning("메타데이터 파일 손상, 새로 생성합니다.")
        return {}
    
    def _save_metadata(self):
        """메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def _get_file_hash(self, filepath: Path) -> str:
        """파일 해시값 계산 (MD5)"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"파일 해시 계산 실패 {filepath}: {e}")
            return ""
    
    def scan_documents(self) -> Tuple[List[Path], List[Path], List[Path]]:
        """
        문서 스캔 및 변경사항 감지
        Returns:
            (새 파일, 수정된 파일, 삭제된 파일)
        """
        current_files = set()
        new_files = []
        modified_files = []
        
        # 현재 디렉토리의 모든 지원 파일 스캔
        for file_path in self.docs_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in {'.pdf', '.csv', '.md', '.docx', '.json'}:
                current_files.add(str(file_path))
                
                # 파일 해시 확인
                current_hash = self._get_file_hash(file_path)
                file_key = str(file_path)
                
                if file_key not in self.metadata:
                    # 새 파일
                    new_files.append(file_path)
                    self.metadata[file_key] = {
                        'hash': current_hash,
                        'last_modified': datetime.now().isoformat(),
                        'size': file_path.stat().st_size
                    }
                elif self.metadata[file_key]['hash'] != current_hash:
                    # 수정된 파일
                    modified_files.append(file_path)
                    self.metadata[file_key].update({
                        'hash': current_hash,
                        'last_modified': datetime.now().isoformat(),
                        'size': file_path.stat().st_size
                    })
        
        # 삭제된 파일 확인
        stored_files = set(self.metadata.keys())
        deleted_files = [Path(f) for f in stored_files - current_files]
        
        # 삭제된 파일 메타데이터 제거
        for deleted_file in deleted_files:
            del self.metadata[str(deleted_file)]
        
        # 메타데이터 저장
        self._save_metadata()
        
        logger.info(f"문서 스캔 완료 - 새 파일: {len(new_files)}, 수정됨: {len(modified_files)}, 삭제됨: {len(deleted_files)}")
        
        return new_files, modified_files, deleted_files
    
    def get_all_indexed_files(self) -> List[Path]:
        """인덱싱된 모든 파일 목록 반환"""
        return [Path(f) for f in self.metadata.keys()]
    
    def mark_as_indexed(self, file_path: Path):
        """파일을 인덱싱 완료로 표시"""
        file_key = str(file_path)
        if file_key in self.metadata:
            self.metadata[file_key]['indexed_at'] = datetime.now().isoformat()
            self._save_metadata()