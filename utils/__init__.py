"""
유틸리티 패키지

RAG 시스템의 보조 기능들을 제공합니다:
- 파일 처리 유틸리티
- 성능 모니터링
- 로깅 설정
- 공통 헬퍼 함수

Example:
    from utils import performance_monitor, file_utils
    
    # 성능 모니터링
    with performance_monitor.measure_time("작업명"):
        # 시간을 측정할 작업
        pass
    
    # 파일 유틸리티
    files = file_utils.find_files_by_extension("/path", [".pdf", ".docx"])
"""

# 주요 모듈들 import
from .performance_monitor import PerformanceMonitor, performance_monitor
from . import file_utils

# 패키지 레벨 상수
SUPPORTED_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

DEFAULT_PERFORMANCE_CONFIG = {
    "enable_monitoring": True,
    "log_performance": True,
    "track_memory": True,
    "track_cpu": True
}

# 패키지 메타데이터
__version__ = "1.0.0"
__author__ = "RAG Chatbot Team" 
__description__ = "Utility functions and performance monitoring"

# 공개 API
__all__ = [
    "PerformanceMonitor",
    "performance_monitor",
    "file_utils",
    "setup_logging",
    "get_system_info",
    "format_bytes",
    "format_duration"
]

# 로깅 설정 함수
def setup_logging(log_level: str = "INFO", log_format: str = None):
    """애플리케이션 로깅 설정
    
    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 커스텀 로그 포맷
    """
    import logging
    
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("llama_index").setLevel(logging.INFO)

# 시스템 정보 조회 함수
def get_system_info():
    """현재 시스템 정보 반환"""
    import psutil
    import platform
    
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk_total_gb": round(psutil.disk_usage("/").total / (1024**3), 2)
    }

# 유틸리티 함수들
def format_bytes(bytes_value: int) -> str:
    """바이트를 읽기 쉬운 형식으로 변환
    
    Args:
        bytes_value: 바이트 값
        
    Returns:
        str: 포맷된 문자열 (예: "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_duration(seconds: float) -> str:
    """초를 읽기 쉬운 형식으로 변환
    
    Args:
        seconds: 시간(초)
        
    Returns:
        str: 포맷된 문자열 (예: "2분 30초")
    """
    if seconds < 60:
        return f"{seconds:.1f}초"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}분 {remaining_seconds:.1f}초"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}시간 {remaining_minutes}분"

def ensure_directory(directory_path):
    """디렉토리가 존재하지 않으면 생성
    
    Args:
        directory_path: 생성할 디렉토리 경로
    """
    import os
    from pathlib import Path
    
    path = Path(directory_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory created: {path}")

# 패키지 초기화
import logging
logger = logging.getLogger(__name__)

# 기본 로깅 설정 적용
setup_logging()

logger.info("Utils package initialized")

# 패키지 레벨 인스턴스 생성 (Singleton 패턴)
# 애플리케이션 전체에서 하나의 성능 모니터 인스턴스 사용
_global_performance_monitor = None

def get_performance_monitor():
    """글로벌 성능 모니터 인스턴스 반환"""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor()
    return _global_performance_monitor

# 편의를 위해 글로벌 인스턴스를 performance_monitor로 alias
performance_monitor = get_performance_monitor()