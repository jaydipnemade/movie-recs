import time
import logging
from functools import wraps

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)

def timed(name: str):
    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                dt = (time.perf_counter() - t0) * 1000
                logger.info(f"[TIMING] {name}: {dt:.2f} ms")
        return wrapper
    return dec
