
# 2025-10-15 12:16:53.952 INFO (MainThread) [custom_components.chuguan_home] async_setup_entry with entry <ConfigEntry entry_id=01K7GT51AHDQY7M6Z5JSRWW8EV version=1 domain=chuguan_home title=wangchuanhui-我的家@9 state=ConfigEntryState.SETUP_IN_PROGRESS unique_id=None> {'brand': 'cg', 'home_id': '15A20970-A93A-45E7-8D7E-74E0E6F82A9D', 'home_name': '我的家@9', 'nick_name': 'wangchuanhui', 'user_id': '0a7b059f-d835-4af4-a976-22898795c7fd', 'username': 'wangchuanhui', 'uuid': '03d6d715-60dd-48e5-b8aa-0ed7f809a23c'}
from threading import Event
import time
from .transport import Transport
import logging
from .hub import Hub



# 基础配置：输出到控制台，包含时间、日志名、级别、内容
logging.basicConfig(
    level=logging.DEBUG,  # 日志级别（决定哪些日志会被输出）
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志格式
    datefmt="%Y-%m-%d %H:%M:%S"  # 时间格式
)

if __name__ == "__main__":
    h = Hub('cg', '03d6d715-60dd-48e5-b8aa-0ed7f809a23c', 'wangchuanhui', '0a7b059f-d835-4af4-a976-22898795c7fd', '15A20970-A93A-45E7-8D7E-74E0E6F82A9D')

    # h = Hub('cg', 'udvjyz6QJUXVrv1XTIJbxkHn1U8j5Utg', 'wangchuanhui1', 'bd4cc066-9fbf-4530-aafb-72e0c047e352', 'EE5DD040-0CB0-4E18-9F05-1C2311894113')
    stop_event = Event()
    
    try:
        # 保持程序运行
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("用户中断，正在停止...")
        h.stop()
    finally:
        h.stop()