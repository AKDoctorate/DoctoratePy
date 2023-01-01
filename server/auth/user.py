import hashlib
from flask import request

from utils import read_json
from constants import CONFIG_PATH
from core.database import userData
from core.Account import Account
from core.function.captcha import sentSmsCode, verifySmsCode

LOG_TOKEN_KEY = "IxMMveJRWsxStJgX"


def userV1NeedCloudAuth():

    data = request.data
    data = {
        "status": 0,
        "msg": "OK"
    }

    return data


def userOAuth2V1Grant():

    data = request.data
    data = {
        "result": 0,
    }

    return data


def userV1GuestLogin():

    data = request.data
    data = {
        "result": 6,
        "message": "禁止游客登录"
    }

    return data


def userAuthenticateUserIdentity():

    data = request.data
    data = {
        "result": 0,
        "message": "OK",
        "isMinor": False
    }

    return data


def userUpdateAgreement():

    data = request.data
    data = {
        "result": 0,
        "message": "OK",
        "isMinor": False
    }

    return data


def userCheckIdCard():

    data = request.data
    data = {
        "result": 0,
        "message": "OK",
        "isMinor": False
    }

    return data


def userSendSmsCode():

    data = request.data
    request_data = request.get_json()

    account = request_data["account"]

    if account:
        sentSmsCode()
        data = {
            "result": 0
        }
        return data


def userRegister():
    
    data = request.data
    request_data = request.get_json()
    
    account = str(request_data["account"])
    password = str(request_data["password"])
    smsCode = str(request_data["smsCode"])

    secret = hashlib.md5((account + LOG_TOKEN_KEY).encode()).hexdigest()
    
    if len(userData.query_account_by_phone(account)) != 0:
        data = {
            "result": 5,
            "errMsg": "该账户已存在，请检查注册信息"
        }
        return data
    
    if not verifySmsCode(smsCode):
        data = {
            "result": 5,
            "errMsg": "验证码错误"
        }
        return data
    
    if userData.register_account(account, hashlib.md5((password + LOG_TOKEN_KEY).encode()).hexdigest(), secret) != 1:
        data = {
            "result": 5,
            "errMsg": "注册失败，未知错误"
        }
        return data
    
    data = {
        "result": 0,
        "uid": 0,
        "token": secret,
        "isAuthenticate": True,
        "isMinor": False,
        "needAuthenticate": False,
        "isLatestUserAgreement": True
    }
    
    return data


def userLogin():
    
    data = request.data
    request_data = request.get_json()

    account = str(request_data["account"])
    password = str(request_data["password"])

    if len(userData.query_account_by_phone(account)) == 0:
        data = {
            "result": 1,
        }
        return data
    
    result = userData.login_account(account, hashlib.md5((password + LOG_TOKEN_KEY).encode()).hexdigest())

    if len(result) != 1:
        data = {
            "result": 1,
        }
        return data

    accounts = Account(*result[0])
    
    data = {
        "result": 0,
        "uid": accounts.get_uid(),
        "token": accounts.get_secret(),
        "isAuthenticate": True,
        "isMinor": False,
        "needAuthenticate": False,
        "isLatestUserAgreement": True
    }

    return data


def userLoginBySmsCode():
    
    data = request.data
    request_data = request.get_json()

    account = str(request_data["account"])
    smsCode = str(request_data["smsCode"])

    if len(userData.query_account_by_phone(account)) == 0:
        data = {
            "result": 1,
        }
        return data
    
    if not verifySmsCode(smsCode):
        data = {
            "result": 5
        }
        return data

    result = userData.query_account_by_secret(hashlib.md5((account + LOG_TOKEN_KEY).encode()).hexdigest())

    if len(result) != 1:
        data = {
            "result": 1,
        }
        return data

    accounts = Account(*result[0])

    data = {
        "result": 0,
        "uid": accounts.get_uid(),
        "token": accounts.get_secret(),
        "isAuthenticate": True,
        "isMinor": False,
        "needAuthenticate": False,
        "isLatestUserAgreement": True
    }

    return data


def userAuth():

    data = request.data
    request_data = request.get_json()

    secret = str(request_data["token"])
    
    if secret is None or len(secret) < 0:
        data = {
            "statusCode": 400,
            "error": "Bad Request",
            "message": "Missing token"
        }
        return data
    
    result = userData.query_account_by_secret(secret)
    
    if len(result) != 1:
        data = {
            "result": 2,
            "error": "此账户不存在"
        }
        return data
    
    accounts = Account(*result[0])
        
    data = {
        "uid": accounts.get_uid(),
        "isMinor": False,
        "isAuthenticate": True,
        "isGuest": False,
        "needAuthenticate": False,
        "isLatestUserAgreement": True
    }
    
    return data