import threading
import logging

_LOGGER = logging.getLogger(__name__)

class SetInterval:
    def __init__(self, interval: int, callback: callable):
        self.interval = interval  # 间隔时间（秒）
        self.callback = callback  # 要重复执行的函数
        self.timer = None         # 定时器对象
        self.is_running = False   # 运行状态标记

    def __del__(self):
        """Stop interval"""
        _LOGGER.info("Stop interval %s", self.interval)

    def _run(self):
        """执行回调并重新调度下一次"""
        self.is_running = True
        try:
            if self.callback is not None:
                self.callback()  # 执行目标函数
        finally:
            # 无论回调是否报错，都重新创建定时器（保证循环）
            self.timer = threading.Timer(self.interval, self._run)
            self.timer.start()

    def start(self):
        """启动定时器（类似 Node.js 的 setInterval 调用）"""
        if not self.is_running:
            self._run()

    def pause(self):
        """停止定时器（类似 Node.js 的 clearInterval）"""
        self.is_running = False
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def stop(self):
        self.is_running = False
        """停止定时器（类似 Node.js 的 clearInterval）"""
        if self.timer:
            self.timer.cancel()
            self.timer = None
        self.callback = None

