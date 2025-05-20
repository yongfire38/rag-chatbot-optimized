"""
최적화된 RAG 챗봇 메인 애플리케이션
증분 인덱싱과 캐싱으로 성능 최적화
"""
import streamlit as st
import logging
from pathlib import Path

from llama_index.llms.llama_cpp import LlamaCPP

from config.settings import *
from core.index_manager import IndexManager
from utils.performance_monitor import performance_monitor

# 로깅 설정
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Streamlit 페이지 설정
st.set_page_config(
    page_title="최적화된 RAG 챗봇",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 RAG 챗봇: 최적화된 인덱싱")
st.markdown("PDF, CSV, Markdown, DOCX, JSON 문서를 기반으로 빠르게 답변합니다.")

# 사이드바 - 설정 및 상태
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 인덱스 관리 버튼
    if st.button("🔄 인덱스 업데이트", help="새로운 또는 수정된 문서만 인덱싱"):
        with st.spinner("인덱스 업데이트 중..."):
            st.session_state.force_index_update = True
            st.success("인덱스 업데이트가 예약되었습니다.")
    
    if st.button("🔥 인덱스 강제 재빌드", help="모든 문서를 다시 인덱싱"):
        with st.spinner("인덱스 재빌드 중..."):
            st.session_state.force_index_rebuild = True
            st.success("인덱스 재빌드가 예약되었습니다.")
    
    if st.button("🗑️ 캐시 초기화", help="인덱스와 임베딩 캐시 삭제"):
        st.session_state.clear_cache = True
        st.success("캐시 초기화가 예약되었습니다.")


# LLM 로드 (캐시됨)
@st.cache_resource(show_spinner="🧠 LLM 모델 로드 중...")
def load_llm():
    """LLM 모델 로드"""
    return LlamaCPP(
        model_path=str(LLM_MODEL_PATH),
        temperature=LLM_TEMPERATURE,
        max_new_tokens=LLM_MAX_NEW_TOKENS,
        context_window=LLM_CONTEXT_WINDOW,
        verbose=False
    )

# 인덱스 매니저 초기화
@st.cache_resource(show_spinner="📚 인덱스 매니저 초기화 중...")
def load_index_manager():
    """인덱스 매니저 로드"""
    return IndexManager()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 강제 작업 처리
if st.session_state.get("clear_cache", False):
    with st.spinner("캐시 초기화 중..."):
        index_manager = load_index_manager()
        index_manager.clear_cache()
        st.cache_resource.clear()
        st.session_state.messages = []
        st.session_state.clear_cache = False
    st.success("캐시가 초기화되었습니다.")
    st.rerun()

# 컴포넌트 로드
llm = load_llm()
index_manager = load_index_manager()

# 인덱스 생성/업데이트
force_rebuild = st.session_state.get("force_index_rebuild", False)
if force_rebuild:
    st.session_state.force_index_rebuild = False

with performance_monitor.measure_time("인덱스 생성/업데이트"):
    try:
        index = index_manager.create_or_update_index(force_rebuild=force_rebuild)
        if index is None:
            st.error("⚠️ 인덱싱할 문서가 없습니다. `docs/` 폴더에 지원되는 파일을 추가해주세요.")
            st.stop()
        
        query_engine = index_manager.get_query_engine(llm)
        
    except Exception as e:
        st.error(f"❌ 인덱스 초기화 실패: {e}")
        logger.error(f"인덱스 초기화 실패: {e}")
        st.stop()

# 상태 정보 표시
with st.sidebar:
    st.header("📊 시스템 상태")
    
    # 인덱스 통계
    index_stats = index_manager.get_index_stats()
    if "total_vectors" in index_stats:
        st.metric("인덱싱된 벡터", index_stats["total_vectors"])
        st.metric("인덱싱된 파일", index_stats["indexed_files"])
    
    # 성능 정보
    perf_summary = performance_monitor.get_performance_summary()
    system_info = perf_summary["system_info"]
    
    st.metric("CPU 사용률", f"{system_info['cpu_percent']:.1f}%")
    st.metric("메모리 사용률", f"{system_info['memory_percent']:.1f}%")
    st.metric("사용 가능 메모리", f"{system_info['available_memory_gb']:.1f}GB")

# 메인 채팅 인터페이스
st.header("💬 채팅")

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📄 출처 문서"):
                st.write(", ".join(message["sources"]))

# 새 메시지 입력
if prompt := st.chat_input("질문을 입력해주세요..."):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            try:
                # 성능 모니터링과 함께 쿼리 실행
                with performance_monitor.measure_time("질의 응답"):
                    response = query_engine.query(prompt)
                
                # 답변 표시
                st.write(response.response)
                
                # 출처 정보 추출
                sources = []
                if hasattr(response, 'source_nodes'):
                    sources = [node.node.metadata.get("source", "Unknown") for node in response.source_nodes]
                
                # 출처 표시
                if sources:
                    with st.expander("📄 출처 문서"):
                        st.write(", ".join(set(sources)))  # 중복 제거
                
                # 세션에 저장
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response.response,
                    "sources": sources
                })
                
            except Exception as e:
                error_message = f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {str(e)}"
                st.error(error_message)
                logger.error(f"쿼리 처리 오류: {e}")
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_message,
                    "sources": []
                })

# 하단 정보
st.markdown("---")
with st.expander("ℹ️ 사용법 및 정보"):
    st.markdown("""
    ### 📝 지원 파일 형식
    - PDF: 자동 텍스트 추출
    - CSV: Name, Purchase 컬럼 우선 처리
    - Markdown: HTML 변환 후 처리
    - DOCX: 문단 텍스트 추출
    - JSON: 구조화된 데이터 처리
    
    ### 🚀 최적화 기능
    - 증분 인덱싱: 새로운/수정된 파일만 처리
    - 임베딩 캐시: 중복 계산 방지
    - FAISS IVF: 빠른 유사도 검색
    - 성능 모니터링: 실시간 시스템 상태 추적
    
    ### 💡 사용 팁
    - `docs/` 폴더에 문서 추가 후 "인덱스 업데이트" 클릭
    - 대량 문서 추가 시 "강제 재빌드" 권장
    - 정기적인 캐시 초기화로 최적 성능 유지
    """)