import asyncio
import threading
import logging

_LOGGER = logging.getLogger(__name__)

def sync_non_blocking(coro: any):
    """同步方法：非阻塞调用任意异步方法"""

    def _run_async():
        """在子线程中运行事件循环的函数"""
        # 为子线程创建独立事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 运行异步方法（不关心返回结果，只在后台执行）
            loop.run_until_complete(coro)
        except Exception as e:
            _LOGGER.error(f"异步调用{coro.__name__}失败: {e}")
        finally:
            loop.close()

    # 创建并启动子线程，设置为守护线程（随主线程退出）
    thread = threading.Thread(target=_run_async, daemon=True)
    thread.start()
    # 不调用thread.join()，直接返回，实现非阻塞