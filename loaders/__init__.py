"""
문서 로더 패키지

다양한 파일 형식을 지원하는 커스텀 문서 로더들을 제공합니다.

지원하는 파일 형식:
- PDF: 텍스트 추출 및 메타데이터 처리
- CSV: 선택적 컬럼 처리
- Markdown: HTML 변환 후 처리  
- DOCX: 문단 및 스타일 정보 추출
- JSON: 구조화된 데이터 처리

Example:
    from loaders import CustomDocumentLoader
    
    loader = CustomDocumentLoader()
    documents = loader.load_documents([Path("example.pdf")])
    
    # 지원 형식 확인
    print(SUPPORTED_FILE_EXTENSIONS)
"""

# 주요 로더 클래스 import
from .custom_loaders import CustomDocumentLoader

# 패키지 레벨 상수
SUPPORTED_FILE_EXTENSIONS = {
    '.pdf': 'PDF documents',
    '.csv': 'Comma-separated values',
    '.md': 'Markdown files',
    '.docx': 'Microsoft Word documents', 
    '.json': 'JSON structured data'
}

# 로더별 설정
LOADER_CONFIGS = {
    'pdf': {
        'extract_images': False,
        'extract_tables': True,
        'parsing_strategy': 'auto'
    },
    'csv': {
        'preferred_columns': ['Name', 'Purchase'],
        'encoding': 'utf-8',
        'delimiter': ','
    },
    'markdown': {
        'extensions': ['tables', 'fenced_code'],
        'convert_to_html': True
    },
    'docx': {
        'extract_images': False,
        'preserve_formatting': False,
        'include_headers_footers': False
    },
    'json': {
        'pretty_print': True,
        'max_depth': None,
        'flatten_arrays': False
    }
}

# 패키지 메타데이터
__version__ = "1.0.0"
__author__ = "RAG Chatbot Team"
__description__ = "Document loaders for various file formats"

# 공개 API
__all__ = [
    "CustomDocumentLoader",
    "SUPPORTED_FILE_EXTENSIONS", 
    "LOADER_CONFIGS",
    "get_loader_for_extension",
    "validate_file_support"
]

# 유틸리티 함수
def get_loader_for_extension(file_extension: str) -> str:
    """파일 확장자에 해당하는 로더 타입 반환
    
    Args:
        file_extension: 파일 확장자 (예: '.pdf')
        
    Returns:
        str: 로더 타입 또는 None
    """
    extension_to_loader = {
        '.pdf': 'pdf',
        '.csv': 'csv', 
        '.md': 'markdown',
        '.docx': 'docx',
        '.json': 'json'
    }
    return extension_to_loader.get(file_extension.lower())

def validate_file_support(file_path) -> bool:
    """파일이 지원되는 형식인지 확인
    
    Args:
        file_path: 파일 경로 (str 또는 Path 객체)
        
    Returns:
        bool: 지원 여부
    """
    from pathlib import Path
    
    path = Path(file_path)
    return path.suffix.lower() in SUPPORTED_FILE_EXTENSIONS

def get_file_type_description(file_extension: str) -> str:
    """파일 확장자에 대한 설명 반환
    
    Args:
        file_extension: 파일 확장자
        
    Returns:
        str: 파일 타입 설명
    """
    return SUPPORTED_FILE_EXTENSIONS.get(file_extension.lower(), "Unknown file type")

# 패키지 초기화 로그
import logging
logger = logging.getLogger(__name__)
logger.info(f"Loaders package initialized - Supporting {len(SUPPORTED_FILE_EXTENSIONS)} file types")