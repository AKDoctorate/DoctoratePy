import random
from flask import request
from time import time

from constants import TOWERDATA_PATH, TOWER_TABLE_URL, USER_JSON_PATH

from utils import read_json, write_json, decrypt_battle_data
from core.function.update import updateData


def towerBuildCard(data):
    tower = read_json(TOWERDATA_PATH)
    saved_data = read_json(USER_JSON_PATH)
    cnt = 1
    for slot in data["slots"]:
        tower["tower"]["current"]["cards"][str(cnt)] = {
        "charId": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["charId"],
		"currentEquip": slot["currentEquip"],
		"defaultSkillIndex": slot["skillIndex"],
		"equip": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["equip"],
		"evolvePhase": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["evolvePhase"],
		"favorPoint": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["favorPoint"],
		"instId": f"{cnt}",
		"level": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["level"],
		"mainSkillLvl": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["mainSkillLvl"],
		"potentialRank": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["potentialRank"],
		"relation": slot["charInstId"],
		"skills": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["skills"],
		"skin": saved_data["user"]["troop"]["chars"][str(slot["charInstId"])]["skin"],
		"type": "CHAR"
    }
        cnt += 1
    tower["currentCards"] = cnt
    write_json(tower, TOWERDATA_PATH)

def towerGetCoord(id):
    tower = read_json(TOWERDATA_PATH)
    for index, layer in enumerate(tower["tower"]["current"]["layer"]):
        if layer["id"] == id:
            return index

def towerGetRecruit():
    tower = read_json(TOWERDATA_PATH)
    saved_data = read_json(USER_JSON_PATH)
    candidate = []
    allCards = [str(saved_data["user"]["troop"]["chars"][key]["instId"]) for key in saved_data["user"]["troop"]["chars"]]
    usedCards = [str(tower["tower"]["current"]["cards"][key]["relation"]) for key in tower["tower"]["current"]["cards"]]
    unusedCards = [card for card in allCards if card not in usedCards]
    pickedCards = random.sample(unusedCards, 5)
    for pickedCard in pickedCards:
        candidate.append({
            "groupId": saved_data["user"]["troop"]["chars"][pickedCard]["charId"],
            "type": "CHAR",
            "cards": [{
                "instId": "0",
                "type": "CHAR",
                "charId": saved_data["user"]["troop"]["chars"][pickedCard]["charId"],
                "relation": pickedCard,
                "evolvePhase": saved_data["user"]["troop"]["chars"][pickedCard]["evolvePhase"],
                "level": saved_data["user"]["troop"]["chars"][pickedCard]["level"],
                "favorPoint": saved_data["user"]["troop"]["chars"][pickedCard]["favorPoint"],
                "potentialRank": saved_data["user"]["troop"]["chars"][pickedCard]["potentialRank"],
                "mainSkillLvl": saved_data["user"]["troop"]["chars"][pickedCard]["mainSkillLvl"],
                "skills": saved_data["user"]["troop"]["chars"][pickedCard]["skills"],
                "defaultSkillIndex": saved_data["user"]["troop"]["chars"][pickedCard]["defaultSkillIndex"],
                "currentEquip": saved_data["user"]["troop"]["chars"][pickedCard]["currentEquip"],
                "equip": saved_data["user"]["troop"]["chars"][pickedCard]["equip"],
                "skin": saved_data["user"]["troop"]["chars"][pickedCard]["skin"]
            }]
        })
    tower["tower"]["current"]["halftime"]["candidate"] = candidate
    write_json(tower, TOWERDATA_PATH)

def towerBuildCard_Recruit(data):
    if data["giveUp"] == 1:
        pass
    else:
        tower = read_json(TOWERDATA_PATH)
        saved_data = read_json(USER_JSON_PATH)
        cnt = tower["currentCards"]
        charInstId = str(saved_data["user"]["dexNav"]["character"][data["charId"]]["charInstId"])
        tower["tower"]["current"]["cards"][str(cnt)] = {
            "charId": data["charId"],
            "currentEquip": saved_data["user"]["troop"]["chars"][charInstId]["currentEquip"],
            "defaultSkillIndex": saved_data["user"]["troop"]["chars"][charInstId]["defaultSkillIndex"],
            "equip": saved_data["user"]["troop"]["chars"][charInstId]["equip"],
            "evolvePhase": saved_data["user"]["troop"]["chars"][charInstId]["evolvePhase"],
            "favorPoint": saved_data["user"]["troop"]["chars"][charInstId]["favorPoint"],
            "instId": f"{cnt}",
            "level": saved_data["user"]["troop"]["chars"][charInstId]["level"],
            "mainSkillLvl": saved_data["user"]["troop"]["chars"][charInstId]["mainSkillLvl"],
            "potentialRank": saved_data["user"]["troop"]["chars"][charInstId]["potentialRank"],
            "relation": charInstId,
            "skills": saved_data["user"]["troop"]["chars"][charInstId]["skills"],
            "skin": saved_data["user"]["troop"]["chars"][charInstId]["skin"],
            "type": "CHAR"
        }
        cnt += 1
        tower["currentCards"] = cnt
        write_json(tower, TOWERDATA_PATH)
    
def towerCreateGame():

    data = request.data
    request_data = request.get_json()
    tower_table = updateData(TOWER_TABLE_URL)
    levels = tower_table["towers"][request_data["tower"]]["levels"]
    layer = []
    for level in levels:
        layer.append({"id": level, "try": 0, "pass": False})
    tower = {
        "tower": {
            "current": {
                "status": {
                    "state": "INIT_GOD_CARD",
                    "tower": request_data["tower"],
                    "coord": 0,
                    "tactical": {},
                    "startegy": "OPTIMIZE",
                    "start": round(time()),
                    "isHard": False, # TODO: add hard mode
                },
                "layer": layer,
                "cards": {},
                "godCard": {
                    "id": "",
                    "subGodCardId": ""
                },
                "halftime": {
                    "count": 0,
                    "candidate": [],
                    "canGiveUp": True
                },
                "trap": [],
                "reward": {}
            }
        },
        "currentStage": "",
        "currentCards": "",
        "recruitTimes": ""
    }
    write_json(tower, TOWERDATA_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "tower": read_json(TOWERDATA_PATH)["tower"]
            },
            "deleted": {}
        }
    }
    return data

def towerInitGodCard():

    data = request.data
    request_data = request.get_json()
    tower = read_json(TOWERDATA_PATH)
    tower["tower"]["current"]["status"]["state"] = "INIT_BUFF"
    tower["tower"]["current"]["godCard"]["id"] = request_data["godCardId"]
    write_json(tower, TOWERDATA_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "tower": read_json(TOWERDATA_PATH)["tower"]
            },
            "deleted": {}
        }
    }
    return data

def towerInitGame():

    data = request.data
    request_data = request.get_json()
    tower = read_json(TOWERDATA_PATH)
    tower["tower"]["current"]["status"]["state"] = "INIT_CARD"
    tower["tower"]["current"]["status"]["tactical"] = request_data["tactical"]
    write_json(tower, TOWERDATA_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "tower": read_json(TOWERDATA_PATH)["tower"]
            },
            "deleted": {}
        }
    }
    return data

def towerInitCard():

    data = request.data
    request_data = request.get_json()
    towerBuildCard(request_data)
    tower = read_json(TOWERDATA_PATH)
    tower["tower"]["current"]["status"]["state"] = "STANDBY"
    write_json(tower, TOWERDATA_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "tower": read_json(TOWERDATA_PATH)["tower"]
            },
            "deleted": {}
        }
    }
    return data

def towerBattleStart():

    data = request.data
    request_data = request.get_json()
    tower = read_json(TOWERDATA_PATH)
    tower["tower"]["current"]["status"]["coord"] = towerGetCoord(request_data["stageId"])
    tower["currentStage"] = request_data["stageId"]
    for item in tower["tower"]["current"]["layer"]:
        if item["id"] == request_data["stageId"]:
            item["try"] += 1
    write_json(tower, TOWERDATA_PATH)

    data = {
        "battleId": "abcdefgh-1234-5678-a1b2c3d4e5f6",
        "playerDataDelta": {
            "modified": {
                "tower": read_json(TOWERDATA_PATH)["tower"]
            },
            "deleted": {}
        }
    }
    return data

def towerBattleFinish():

    data = request.data
    request_data = request.get_json()
    BattleData = decrypt_battle_data(request_data["data"], 1672502400)
    tower = read_json(TOWERDATA_PATH)

    if BattleData["completeState"] == 1:
        for item in tower["tower"]["current"]["layer"]:
            if item["id"] == tower["currentStage"]:
                item["try"] += 1
        write_json(tower, TOWERDATA_PATH)

        data = {
            "drop": [],
            "isNewRecord": False,
            "trap": [],
            "playerDataDelta": {
                "modified": {},
                "deleted": {}
        }
    }
    else:
        if tower["currentStage"] == tower["tower"]["current"]["layer"][2]["id"]:
            tower["tower"]["current"]["status"]["state"] = "SUB_GOD_CARD_RECRUIT"
            write_json(tower, TOWERDATA_PATH)
            # TODO: Learn about official card selection times
        elif tower["currentStage"] == tower["tower"]["current"]["layer"][-1]["id"]:
            tower["tower"]["current"]["status"]["state"] = "END"
            write_json(tower, TOWERDATA_PATH)
        else:
            tower["tower"]["current"]["status"]["state"] = "RECRUIT"
            write_json(tower, TOWERDATA_PATH)

        tower["tower"]["current"]["status"]["coord"] += 1
        tower["recruitTimes"] = 0
        for item in tower["tower"]["current"]["layer"]:
            if item["id"] == tower["currentStage"]:
                item["try"] += 1
                item["pass"] = True
        write_json(tower, TOWERDATA_PATH)
        towerGetRecruit()

        data = {
            "isNewRecord": False,
            "drop": [],
            "trap": [],
            "playerDataDelta": {
                "modified": {
                    "tower": read_json(TOWERDATA_PATH)["tower"]
                },
                "deleted": {}
            }
        }

    return data

def towerRecruit():

    data = request.data
    request_data = request.get_json()
    towerBuildCard_Recruit(request_data)
    tower = read_json(TOWERDATA_PATH)
    if tower["recruitTimes"] != 1:
        tower["tower"]["current"]["status"]["state"] = "RECRUIT"
        tower["recruitTimes"] += 1
    else:
        tower["tower"]["current"]["status"]["state"] = "STANDBY"
    write_json(tower, TOWERDATA_PATH)
    towerGetRecruit()

    data = {
        "playerDataDelta": {
            "modified": {
                "tower": read_json(TOWERDATA_PATH)["tower"]
            },
            "deleted": {}
        }
    }
    return data

def towerChooseSubGodCard():

    data = request.data
    request_data = request.get_json()
    tower = read_json(TOWERDATA_PATH)
    tower["tower"]["current"]["status"]["state"] = "STANDBY"
    tower["tower"]["current"]["godCard"]["subGodCardId"] = request_data["subGodCardId"]
    write_json(tower, TOWERDATA_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "tower": read_json(TOWERDATA_PATH)["tower"]
            },
            "deleted": {}
        }
    }
    return data

def towerSettleGame():

    data = request.data
    request_data = request.get_json()
    tower = read_json(TOWERDATA_PATH)

    data = {
        "reward": {
            "high": {
                "cnt": 0,
                "from": 24,
                "to": 24
            },
            "low": {
                "cnt": 0,
                "from": 60,
                "to": 60
            }
        },
        "ts": round(time()),
        "playerDataDelta": {
            "modified": {
                "tower": {
                    "current": {
                        "status": {
                            "state": "NONE",
                            "tower": "",
                            "coord": 0,
                            "tactical": {
                                "PIONEER": "",
                                "WARRIOR": "",
                                "TANK": "",
                                "SNIPER": "",
                                "CASTER": "",
                                "SUPPORT": "",
                                "MEDIC": "",
                                "SPECIAL": ""
                            },
                            "startegy": "OPTIMIZE",
                            "start": 0,
                            "isHard": False
                        },
                        "layer": [],
                        "cards": {},
                        "godCard": {
                            "id": "",
                            "subGodCardId": "",
                        },
                        "halftime": {
                            "count": 0,
                            "candidate": [],
                            "canGiceUp": False
                        },
                        "trap": [],
                        "raward": {}
                    }
                }
            },
            "deleted": {
                "tower": {
                    "current": {
                        "cards": [str(key) for key in tower["tower"]["current"]["cards"]]
                    }
                }
            }
        }
    }
    return data