
import paho.mqtt.client as mqtt
import logging
import json
from .event_emitter import EventEmitter
from homeassistant.util.ssl import get_default_context  # 官方提供的异步安全 SSL 上下文创建工具

_LOGGER = logging.getLogger(__name__)

class Transport(EventEmitter):
    def __init__(self, account: str, user_id: str, broker: str, port: int):
        super().__init__()
        self._account = account
        self._user_id = user_id
        self._broker = broker
        self._port = port
        self._client_id = user_id.lower()
        _LOGGER.info(f"self._client_id: {self._client_id}, account: {account}")
        self._client = mqtt.Client(client_id=self._client_id, clean_session=True, transport="websockets")
        self._client.on_connect = self.on_connect
        self._client.on_connect_fail = self.on_connect_fail
        self._client.on_subscribe = self.on_subscribe
        self._client.on_message = self.on_message
        self._client.on_disconnect = self.on_disconnect
        self._client.ws_set_options(path="/mqtt")
        # self._client.tls_set()
        # 关键修改：用官方工具创建 SSL 上下文（自动在 executor 中加载证书）
        ssl_context = get_default_context()  # 内部已处理阻塞 I/O，安全运行在异步环境
        self._client.tls_set_context(ssl_context)  # 使用创建好的上下文，避免直接调用 tls_set()
        self._client.username_pw_set(account, account)
        self.connect()

    def __del__(self):
        """Stop transport"""
        _LOGGER.info("Stop transport")

    def connect(self):
        """连接到MQTT服务器"""
        _LOGGER.info("connecting")
        try:
            self._client.connect_async(self._broker, self._port, keepalive=30)
            self._client.loop_start()
            return True
        except Exception as e:
            _LOGGER.info(f"连接出错: {e}")
            return False

    def on_connect(self, client, userdata, flags, rc):
        """连接回调方法"""
        if rc == 0:
            self._connected = True
            _LOGGER.info(f"成功连接到 {self._broker}:{self._port}")
            self._client.subscribe(f"/app/forward/cg/wx/{self._client_id}/set", qos=0)
        else:
            self._connected = False
            _LOGGER.info(f"连接失败，错误代码: {rc}")

    def on_connect_fail(self, client, userdata, rc):
        """连接失败回调方法"""
        self._connected = False
        _LOGGER.info(f"连接失败，错误代码: {rc}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """
        订阅结果回调
        :param mid: 订阅请求的消息 ID（与 on_connect 中返回的 mid 对应）
        :param granted_qos: 服务器授予的 QoS 列表（与订阅时的顺序一致）
        """
        _LOGGER.info(f"订阅结果 - 消息 ID: {mid}")
        # 遍历每个订阅的 QoS 结果
        for i, qos in enumerate(granted_qos):
            if qos == 0x80:  # 0x80 表示订阅失败
                _LOGGER.error(f"主题 {i+1} 订阅失败")
            else:
                _LOGGER.info(f"主题 {i+1} 订阅成功，授予的 QoS: {qos}")
                self.emit('subscribed')

    def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
        """消息接收回调方法"""
        try:
            payload = msg.payload.decode('utf-8')
            json_payload: dict = json.loads(payload)
            Params: dict = json_payload.get('Params', {})
            forward_id = Params.get('forward_id', '')
            if forward_id == "":
                return
            self.emit('message', forward_id, Params)
        finally:
            """确保在任何情况下都调用"""


    def on_disconnect(self, client, userdata, rc):
        """断开连接回调方法"""
        self._connected = False
        _LOGGER.info(f"与服务器断开连接，代码: {rc}")
        if rc != 0:
            _LOGGER.info("意外断开连接，尝试重连...")
            self.connect()

    def stop(self):
        """Stop transport"""
        self._client.on_connect = None
        self._client.on_connect_fail = None
        self._client.on_subscribe = None
        self._client.on_message = None
        self._client.on_disconnect = None
        self._client.loop_stop()
        self._client.disconnect()
