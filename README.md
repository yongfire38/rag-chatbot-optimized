# rag-chatbot-optimized
Python 기반의 최적화된 RAG(Retrieval-Augmented Generation) 챗봇을 구현

## 준비물

- 운영체제: Windows, macOS, Linux 어디든 OK!

- Python: 3.8 이상 (3.10 추천).

- 하드웨어: 최소 8GB RAM (16GB 권장), GPU가 있다면 금상첨화.

- 텍스트 에디터: VS Code나 PyCharm 같은 편리한 도구.

- 테스트 문서: PDF, CSV, Markdown, DOCX, JSON 파일 각각 1개씩.

- 예: sample.pdf (회사 매뉴얼), data.csv (고객 데이터), notes.md (노트), report.docx (보고서), config.json (설정 파일).

## 프로젝트 구조
```
rag_chatbot_optimized/
├── app.py                    # 메인 Streamlit 애플리케이션
├── config/
│   ├── __init__.py           # 설정 모듈 export, 메타데이터
│   └── settings.py           # 설정 관리
├── core/
│   ├── __init__.py           # 핵심 클래스 export, 초기화 로직
│   ├── document_manager.py   # 문서 관리 및 변경 감지
│   ├── index_manager.py      # 인덱스 생성/로드/업데이트
│   └── embedding_cache.py    # 임베딩 캐시 관리
├── loaders/
│   ├── __init__.py           # 로더 클래스 export, 형식 지원 정보
│   └── custom_loaders.py     # 커스텀 문서 로더
├── utils/
│   ├── __init__.py           # 유틸리티 함수 export, 로깅 설정
│   ├── file_utils.py         # 파일 유틸리티
│   └── performance_monitor.py # 성능 모니터링
├── storage/                  # 인덱스 저장소
├── docs/                     # 문서 디렉토리
├── models/                   # LLM 모델 파일
├── requirements.txt
└── README.md
```
## 구동 방법

### 필요한 의존성들 설치 

```
pip install llama-index llama-index-llms-llama-cpp llama-index-embeddings-huggingface llama-index-vector-stores-faiss pymupdf streamlit python-docx pandas markdown

# 윈도우에서는 gpu가 안 된다
pip install faiss-cpu

# 윈도우 외의 환경에서는 사용 가능
pip install faiss-gpu
```

### 로컬 LLM 설정: Llama.cpp
온프레미스에서 LLM을 돌리기 위해 Llama.cpp를 활용

```
pip install llama-cpp-python
```

### 프로젝트 루트에다가 models 디렉토리 만들고 파일 넣기
-> 예제에서는 [ggml-model-Q4_0.gguf](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF) 를 사용. 다른 모델을 사용해도 무방할 것으로 보임

### 프로젝트 루트에 docs 디렉토리 만들고 파일 넣기
- sample.pdf: 회사 매뉴얼
- data.csv: 고객 데이터 (Name, Email, Purchase)
- notes.md: 프로젝트 노트
- report.docx: 프로젝트 보고서
- config.json: 설정 데이터

### `C:\Users\사용자 이름\.streamlit` 경로에 config.toml 만들고 다음과 같이 작성

```
[server]
runOnSave = false
fileWatcherType = "none"
```

### 가상 환경에서 실행
```
streamlit run app.py --global.developmentMode=false
```

## 출처
[LlamaIndex와 Streamlit으로 온프레미스 RAG 챗봇 구축하기](https://tilnote.io/pages/682abc6cb1620287202c38e1)
