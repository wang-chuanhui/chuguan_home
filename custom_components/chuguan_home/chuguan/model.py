from dataclasses import dataclass

@dataclass
class UserInfo:
	account: str
	lastName: str
	userid: str

	@property
	def nickname(self):
		if self.lastName and self.lastName.strip() != "":
			return self.lastName
		else:
			return self.account


def toUserInfo(dic: dict):
	return UserInfo(dic['account'], dic['lastName'], dic['userid'])

def toUserInfoList(arr: list):
	return [toUserInfo(item) for item in arr]


@dataclass
class HomeInfo:
	HomeId: str
	HomeName: str

@dataclass
class HardwareInfo:
	id: str
	nickname: str
	room: str
	brand: str

def toHomeInfo(dic: dict):
	return HomeInfo(dic['HomeId'], dic['HomeName'])

def toHomeInfoList(arr: list):
	return [toHomeInfo(item) for item in arr]


class Mode(dict):  # 继承 dict 类
    def __init__(self, deviceType: str, value: str):
        # 调用父类 dict 的 __init__ 方法，初始化键值对
        super().__init__(deviceType=deviceType, value=value)
        # 可选：同时绑定为实例属性，方便通过 dot 语法访问（如 obj.deviceType）
        self.deviceType = deviceType
        self.value = value

class ModeValue:
	AirerXiaoDu = Mode("CLOTHES_RACK", "DISINFECT")
	AirerHongGan = Mode("CLOTHES_RACK", "AIR_DRY")
	AirerFengGan = Mode("CLOTHES_RACK", "MUTE")
	AirerLight = Mode("CLOTHES_RACK", "LIGHTING")
	
	AirCool: Mode = Mode("AIR_CONDITION", "COOL")
	AirHeat: Mode = Mode("AIR_CONDITION", "HEAT")
	AirFan: Mode = Mode("AIR_CONDITION", "FAN")
	AirChuShi: Mode = Mode("AIR_CONDITION", "DEHUMIDIFICATION")
	AirAuto: Mode = Mode("AIR_CONDITION", "AUTO")
	
