import json


def pLog(
        msg: str = "",
        id: int = 1,
        user: str = "system"
):

    print(f"[ {id} | {user} ] : \t {msg}")

def pObj(
        obj: object
):
    print(json.dumps(obj, indent=2))