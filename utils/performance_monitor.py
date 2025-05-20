"""
성능 모니터링 유틸리티
시스템 성능 추적 및 병목 지점 식별
"""
import time
import psutil
import logging
from functools import wraps
from typing import Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    @contextmanager
    def measure_time(self, operation_name: str):
        """시간 측정 컨텍스트 매니저"""
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_time = time.time() - start_time
            self.metrics[operation_name] = elapsed_time
            logger.info(f"{operation_name}: {elapsed_time:.2f}초")
    
    def monitor_performance(self, func_name: str = None):
        """함수 성능 모니터링 데코레이터"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                operation_name = func_name or f"{func.__module__}.{func.__name__}"
                
                # 메모리 사용량 (시작)
                process = psutil.Process()
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
                
                # 시간 측정
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed_time = time.time() - start_time
                    memory_after = process.memory_info().rss / 1024 / 1024  # MB
                    memory_diff = memory_after - memory_before
                    
                    # 메트릭 저장
                    self.metrics[operation_name] = {
                        'execution_time': elapsed_time,
                        'memory_before': memory_before,
                        'memory_after': memory_after,
                        'memory_diff': memory_diff
                    }
                    
                    logger.info(
                        f"{operation_name} - 실행시간: {elapsed_time:.2f}초, "
                        f"메모리 변화: {memory_diff:+.1f}MB"
                    )
            return wrapper
        return decorator
    
    def get_system_info(self) -> Dict[str, Any]:
        """시스템 정보 조회"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'available_memory_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보"""
        total_time = time.time() - self.start_time
        return {
            'total_runtime': total_time,
            'operations': self.metrics,
            'system_info': self.get_system_info()
        }
    
    def reset_metrics(self):
        """메트릭 초기화"""
        self.metrics.clear()
        self.start_time = time.time()

# 글로벌 모니터 인스턴스
performance_monitor = PerformanceMonitor()