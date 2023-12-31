'''
utils.pLog and pObj supports two levels of logging:
P1, or Long-Term storage logging, is to be printed on console as well as saved in
workflows / Log.json (DevLog.json for devt which is .gitignored)
P2, or Short-Term logging, is just to be printed on console

Logging messages have to be stored as a JSON string before calling writeLog
'''

import json
import os
import datetime

from dotenv import load_dotenv

load_dotenv()

if os.environ.get('IS_DEV') == 'True':
    Is_Dev = True
else:
    Is_Dev = False

Is_Dev = True if os.environ.get('IS_DEV') == 'True' else False
Save_Logs = True if os.environ.get('SAVE_LOGS') == 'True' else False

# False if default to deployment, True if default to still developing

def pLog(
        msg: str = "",
        id: int = 1,
        user: str = "system",
        p1: bool = False
) -> None:
    time = datetime.datetime.now()
    logStr = f"[ {time} | {id} | {user} ] : \t {msg}"
    print(logStr)
    if p1 and Save_Logs: writeStr(logStr)


def pObj(
        obj: object,
        name: str = "",
        p1: bool = False
):
    time = datetime.datetime.now()
    blob = {}
    print(time)
    blob["Time"] = str(time)
    print(blob)

    blob[name] = obj

    to_print = json.dumps(blob, indent=2)
    print(to_print)
    if p1 and Save_Logs: logObj(blob, name, self_called=True)

def writeStr(str):
    # Remove isDev = True to isDev = False when deploying
    log_file_name = 'workflows/DevLog.txt' if Is_Dev else 'workflows/Log.txt'
    
    with open(log_file_name, "a") as log:
        log.write("\n" + str)

def logObj(obj,
           name: str = "",
           self_called: bool = False):
    # If self_called is false, then it comes from other parts of the code, not ut.pObj
        
    # Remove isDev = True to isDev = False when deploying
    log_file_name = 'workflows/DevObjs.json' if Is_Dev else 'workflows/Objs.json'
    
    if not self_called:
        blob = {}
        blob["Time"] = str(datetime.datetime.now())
        blob[name] = obj
    else:
        blob = obj

    with open(log_file_name, "a") as log:
        log.write("\n")
        json.dump(blob, log, ensure_ascii=False, indent=2)

def clearLogs():
    log_file_names = ['workflows/DevObjs.json',
                      'workflows/Objs.json',
                      'workflows/DevLog.txt',
                      'workflows/Log.txt']
    for log in log_file_names:
        with open(log, "w") as log:
            log.write("")