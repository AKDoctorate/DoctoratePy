import json

import requests
from flask import request

from constants import USER_JSON_PATH
from utils import read_json, write_json


def userCheckIn():

    data = request.data
    data = {
        "result": 0,
        "playerDataDelta": {
            "modified": {},
            "deleted": {}
        }
    }

    return data


def userChangeSecretary():

    data = request.data
    request_data = request.get_json()
    charInstId = request_data["charInstId"]
    skinId = request_data["skinId"]
    data = {
        "playerDataDelta":{
            "modified":{
                "status":{
                    "secretary": "",
                    "secretarySkinId": "",
                }
            },
            "deleted":{}
        }
    }

    if charInstId and skinId:
        data["playerDataDelta"]["modified"]["status"]["secretary"] = skinId.split("@")[0] if "@" in skinId else skinId.split("#")[0]
        data["playerDataDelta"]["modified"]["status"]["secretarySkinId"] = skinId
        return data


def userLogin():

    data = request.data
    data = {
        "accessToken": "1",
        "birth": None,
        "channelId": "",
        "isAuthenticate": True,
        "isLatestUserAgreement": True,
        "isMinor": False,
        "needAuthenticate": False,
        "result": 0,
        "token": "abcd",
        "yostar_username": "Doctorate@doctorate.com",
        "yostar_uid": "1",
        "uid": "1"
    }

    return data


def userOAuth2V1Grant():
    
    data = request.data
    data = {
        "data": {
            "code": "abcd",
            "uid": "1"
        },
        "msg": "OK",
        "status": 0
    }

    return data


def userV1NeedCloudAuth():

    data = request.data
    data = {
        "msg": "OK",
        "status": 0
    }
    
    return data


def userV1getToken():

    data = request.data
    data = {
        "channelUid": "1",
        "error": "",
        "extension": json.dumps({
            "isMinor": False,
            "isAuthenticate": True
        }),
        "isGuest": 0,
        "result": 0,
        "token": "abcd",
        "uid": "1"
    }

    return data


def userAuth():

    data = request.data
    data = {
        "isAuthenticate": True,
        "isGuest": False,
        "isLatestUserAgreement": True,
        "isMinor": False,
        "needAuthenticate": False,
        "uid": "1"
    }

    return data


def userChangeAvatar():

    data = request.data
    avatar = request.get_json()

    saved_data = read_json(USER_JSON_PATH)
    saved_data["user"]["status"]["avatar"] = avatar
    write_json(saved_data, USER_JSON_PATH)

    data = {
        "playerDataDelta": {
            "deleted": {},
            "modified": {
                "status": {
                    "avatar": avatar
                }
            }
        }
    }

    return data


def appGetSettings():

    data = request.data
    data = requests.get("https://passport.arknights.global/app/getSettings").json()
    return data


def appGetCode():

    data = request.data
    data = requests.get("https://passport.arknights.global/app/getCode").json()
    return data


def userYostarCreatelogin():

    data = request.data
    data = {
        "isNew": 0,
        "result": 0,
        "token": "1",
        "uid": "1",
        "yostar_uid": "1",
        "yostar_username": "Doctorate@doctorate.com"
    }

    return data

def userAgreement():

    data = request.data
    data = {
        "data": [
            "¯\_(ツ)_/¯"
        ],
        "version": "4.0.0"
    }

    return data
