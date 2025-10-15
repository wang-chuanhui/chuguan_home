

class EventEmitter:
    def __init__(self):
        # 存储事件与回调的映射：{事件名: [回调函数列表]}
        self.events: dict[str, list[callable]] = {}

    def on(self, event: str, callback: callable) -> None:
        """注册事件回调"""
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(callback)

    def emit(self, event: str, *args: any, **kwargs: any) -> None:
        """触发事件，调用所有注册的回调"""
        if event in self.events:
            for callback in self.events[event]:
                # 支持位置参数和关键字参数
                callback(*args, **kwargs)

    def off(self, event: str, callback: callable) -> None:
        """移除事件回调"""
        if event in self.events:
            self.events[event].remove(callback)

    def off(self, event: str):
        """移除所有事件回调"""
        if event in self.events:
            del self.events[event]

    def off(self):
        """移除所有事件回调"""
        self.events.clear()

    def once(self, event: str, callback: callable) -> None:
        """注册一次性事件（触发后自动移除）"""
        def wrapper(*args: any, **kwargs: any) -> None:
            callback(*args, **kwargs)
            self.off(event, wrapper)
        self.on(event, wrapper)