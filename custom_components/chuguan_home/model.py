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

def toHomeInfo(dic: dict):
	return HomeInfo(dic['HomeId'], dic['HomeName'])

def toHomeInfoList(arr: list):
	return [toHomeInfo(item) for item in arr]
