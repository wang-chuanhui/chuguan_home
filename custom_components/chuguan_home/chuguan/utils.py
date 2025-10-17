import aiohttp
import json
from .error import InvalidAuth
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


async def submit_data(session: aiohttp.ClientSession, url: str, payload: dict):
    try:
        async with session.post(
            url,
            data=payload,
            timeout=30
        ) as response:
            text = await response.text()
            result: dict = json.loads(text)
            result_code = result.get('resultCode', '10000')
            if result_code == '20000':
                return result.get('resultData')
            if result_code == '10001':
                raise InvalidAuth("登录失效")
            message = result.get('message', '没有数据')
            _LOGGER.info(f"{payload} {result}")
            raise Exception(f"{result_code}, {message}")
    except aiohttp.ClientError as e:
        _LOGGER.error("POST 错误: %s", e)
        raise e;

async def post_data(url: str, payload: dict):
    """POST data to the brand."""
    async with aiohttp.ClientSession() as session:
        return await submit_data(session, url, payload);