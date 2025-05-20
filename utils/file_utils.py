"""
파일 처리 유틸리티

파일 시스템 작업을 위한 헬퍼 함수들을 제공합니다.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def find_files_by_extension(directory: Path, extensions: Set[str]) -> List[Path]:
    """지정된 확장자의 파일들을 재귀적으로 찾기
    
    Args:
        directory: 검색할 디렉토리
        extensions: 찾을 파일 확장자 집합 (예: {'.pdf', '.docx'})
        
    Returns:
        List[Path]: 찾은 파일들의 경로 리스트
    """
    directory = Path(directory)
    found_files = []
    
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return found_files
    
    # 확장자를 소문자로 정규화
    extensions = {ext.lower() for ext in extensions}
    
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            found_files.append(file_path)
    
    logger.info(f"Found {len(found_files)} files with extensions {extensions} in {directory}")
    return found_files

def get_file_size(file_path: Path) -> int:
    """파일 크기 반환 (바이트)
    
    Args:
        file_path: 파일 경로
        
    Returns:
        int: 파일 크기 (바이트)
    """
    try:
        return file_path.stat().st_size
    except (OSError, FileNotFoundError):
        logger.error(f"Cannot get size of file: {file_path}")
        return 0

def get_directory_size(directory: Path) -> int:
    """디렉토리 전체 크기 계산 (바이트)
    
    Args:
        directory: 디렉토리 경로
        
    Returns:
        int: 디렉토리 크기 (바이트)
    """
    total_size = 0
    try:
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += get_file_size(file_path)
    except Exception as e:
        logger.error(f"Error calculating directory size: {e}")
    
    return total_size

def safe_file_copy(source: Path, destination: Path, overwrite: bool = False) -> bool:
    """안전한 파일 복사
    
    Args:
        source: 원본 파일 경로
        destination: 대상 파일 경로  
        overwrite: 덮어쓰기 허용 여부
        
    Returns:
        bool: 복사 성공 여부
    """
    try:
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            logger.error(f"Source file does not exist: {source}")
            return False
        
        if destination.exists() and not overwrite:
            logger.warning(f"Destination already exists and overwrite=False: {destination}")
            return False
        
        # 대상 디렉토리 생성
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 복사
        shutil.copy2(source, destination)
        logger.info(f"File copied: {source} -> {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        return False

def safe_file_move(source: Path, destination: Path, overwrite: bool = False) -> bool:
    """안전한 파일 이동
    
    Args:
        source: 원본 파일 경로
        destination: 대상 파일 경로
        overwrite: 덮어쓰기 허용 여부
        
    Returns:
        bool: 이동 성공 여부
    """
    try:
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            logger.error(f"Source file does not exist: {source}")
            return False
        
        if destination.exists() and not overwrite:
            logger.warning(f"Destination already exists and overwrite=False: {destination}")
            return False
        
        # 대상 디렉토리 생성
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 이동
        shutil.move(str(source), str(destination))
        logger.info(f"File moved: {source} -> {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Error moving file: {e}")
        return False

def safe_directory_delete(directory: Path, force: bool = False) -> bool:
    """안전한 디렉토리 삭제
    
    Args:
        directory: 삭제할 디렉토리 경로
        force: 강제 삭제 여부 (비어있지 않아도 삭제)
        
    Returns:
        bool: 삭제 성공 여부
    """
    try:
        directory = Path(directory)
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return True
        
        if not directory.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return False
        
        # 디렉토리가 비어있지 않은 경우
        if any(directory.iterdir()) and not force:
            logger.warning(f"Directory is not empty and force=False: {directory}")
            return False
        
        # 디렉토리 삭제
        shutil.rmtree(directory)
        logger.info(f"Directory deleted: {directory}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting directory: {e}")
        return False

def create_backup(file_path: Path, backup_suffix: str = ".backup") -> Optional[Path]:
    """파일 백업 생성
    
    Args:
        file_path: 백업할 파일 경로
        backup_suffix: 백업 파일 접미사
        
    Returns:
        Optional[Path]: 백업 파일 경로 (실패 시 None)
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return None
        
        # 백업 파일 경로 생성
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
        
        # 백업 파일이 이미 존재하면 숫자 추가
        counter = 1
        while backup_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}{backup_suffix}.{counter}")
            counter += 1
        
        # 백업 생성
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None

def cleanup_old_files(directory: Path, max_age_days: int, pattern: str = "*") -> int:
    """오래된 파일들 정리
    
    Args:
        directory: 정리할 디렉토리
        max_age_days: 최대 보관 일수
        pattern: 파일 패턴 (glob 패턴)
        
    Returns:
        int: 삭제된 파일 수
    """
    import time
    
    try:
        directory = Path(directory)
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        deleted_count = 0
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {e}")
        
        logger.info(f"Cleanup completed: {deleted_count} files deleted from {directory}")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return 0

def get_available_disk_space(path: Path) -> Tuple[int, int, int]:
    """디스크 여유 공간 정보 반환
    
    Args:
        path: 확인할 경로
        
    Returns:
        Tuple[int, int, int]: (총 공간, 사용 공간, 여유 공간) 바이트 단위
    """
    try:
        stat = shutil.disk_usage(path)
        return stat.total, stat.used, stat.free
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return 0, 0, 0

def is_file_locked(file_path: Path) -> bool:
    """파일이 다른 프로세스에 의해 사용 중인지 확인
    
    Args:
        file_path: 확인할 파일 경로
        
    Returns:
        bool: 파일이 잠겨있으면 True
    """
    try:
        with open(file_path, 'r+'):
            pass
        return False
    except IOError:
        return True
    except Exception:
        return True

def normalize_path(path: str) -> Path:
    """경로 정규화 (상대경로를 절대경로로, 경로 구분자 통일)
    
    Args:
        path: 정규화할 경로
        
    Returns:
        Path: 정규화된 경로 객체
    """
    return Path(path).resolve()

def get_file_extension_safely(file_path: Path) -> str:
    """파일 확장자를 안전하게 추출 (소문자로 변환)
    
    Args:
        file_path: 파일 경로
        
    Returns:
        str: 파일 확장자 (점 포함, 소문자)
    """
    return file_path.suffix.lower() if file_path.suffix else ""

def count_files_by_extension(directory: Path) -> dict:
    """디렉토리의 파일을 확장자별로 개수 세기
    
    Args:
        directory: 확인할 디렉토리
        
    Returns:
        dict: {확장자: 개수} 딕셔너리
    """
    directory = Path(directory)
    extension_counts = {}
    
    try:
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                ext = get_file_extension_safely(file_path)
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
    except Exception as e:
        logger.error(f"Error counting files: {e}")
    
    return extension_counts