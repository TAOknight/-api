import logging
import json
import base64
import test

def common_reply(reply, result_type, parameter_name, intent_id, gw_commands):
    response = {
        "isBase64Encoded": "false",
        "statusCode": "200",
        "headers": {"content-type": "application/json"},
        "body": {
            "returnCode": "0",
            "returnErrorSolution": "",
            "returnMessage": "",
            "returnValue": {
                "reply": reply,
                "resultType": result_type,
                "executeCode": "SUCCESS",
                "msgInfo": "",
                "askedInfos": [
                    {
                        "parameterName": parameter_name,
                        "intentId": intent_id
                    }
                ],
                "gwCommands": gw_commands
            }
        }
    }
    return response


def ask_reply(reply, parameter_name, intent_id):
    return common_reply(reply, 'ASK_INF', parameter_name, intent_id, None)


def result_reply(reply):
    return common_reply(reply, 'RESULT', None, None, None)


def tpl_reply(reply, city, detail):
    gw_commands = [
        {
            "commandDomain": "AliGenie.Speaker",
            "commandName": "Speak",
            "payload": {
                "type": "text",
                "text": reply
            }
        }, {
            "commandDomain": "AliGenie.Screen",
            "commandName": "Render",
            "payload": {
                "pageType": "TPL.RenderTemplate",
                "data": {
                    "template": "aligenie_weather_tpl_demo",
                    "pageTitle": "天气小助手",
                    "dataSource": {
                        "city": city,
                        "imageUrl": "https://ailabs-iot.aligenie.com/iap/platform3.0/weather-banner.png",
                        "minTemperature": "36°",
                        "maxTemperature": "38°",
                        "detail": detail
                    }
                }
            }
        }
    ]
    return common_reply(None, 'RESULT', None, None, gw_commands)


def weather_tpl_reply(reply, city):
    return tpl_reply(reply, city, reply)


def air_tpl_reply(reply, city):
    return tpl_reply(reply, city, reply)


def handler(event, context):
    request = json.loads(event)
    logger = logging.getLogger()
    body = base64.b64decode(request['body']).decode()
    data = json.loads(body)

    logger.info('request body:' + body)

    # 从请求中获取意图参数以及参数值
    intent_name = data['intentName']
    openId=str(data)

    if "deviceUnionIds" in data["requestData"].keys():
        openId = data["requestData"]["deviceUnionIds"]
    # try:
    #   openId = data["requestData"]["deviceUnionIds"]
    # except expression as identifier:
    #   pass


    # screen_status = getattr(data['requestData'], 'screenStatus', 'offline')
    # screen_status = 'online'


    reply = None

    # 处理名称为 guide 的意图
    if intent_name == "guide":
        reply = '好的主人，您可以跟精灵说：写新闻稿或者运行流程'
        return ask_reply(reply,None, data['intentId'])

    # 处理名称为 trade_rport 的意图
    elif intent_name == "trade_rport":

        for slot in data['slotEntities']:
            if slot['intentParameterName'] == "trade":
                trade = "关于"+slot['slotValue']

            elif slot['intentParameterName'] == "group":
                group = slot['slotValue']

        if trade =="关于自由发挥":
            trade ='' 
            reply = '好的,开始写新闻稿。'
        else:
            reply = '好的,开始写'+trade+"的新闻稿。"

        # 应用入参
        informationOfrobot = [
          {
          "name":"group", #//应用参数名称
          "value":group, #// 应用参数值
          "type":"str" #//参考应用运行参数枚举说明
          },
          {
          "name":"trade",
          "value":trade,
          "type":"str"
          },
          {
          "name":"deviceOpenId",
          "value":openId,
          "type":"str",
          },
          {
          "name":"req",
          "value":str(data),
          "type":"str",
          }          
        ]

        accessToken = test.getAccessToken()

        robotUuid = test.queryRoot(accessToken, "写报告")

        test.informationOfDispatch["robotUuid"] = robotUuid

        test.startJob(accessToken,informationOfrobot)
        
        return result_reply(reply)

    # 处理名称为 start_robot 的意图
    elif intent_name == "start_robot":

        rpa_name = None
        for slot in data['slotEntities']:
            if slot['intentParameterName'] == "rpa_name":
                rpa_name = slot['slotValue']
        reply = '好的,开始启动'+rpa_name

        accessToken = test.getAccessToken()

        robotUuid = test.queryRoot(accessToken, rpa_name)

        test.informationOfDispatch["robotUuid"] = robotUuid

        test.startJob(accessToken,None)

        return result_reply(reply)

    reply = '请检查意图名称是否正确，或者新增的意图没有在代码里添加对应的处理分支。'

    return result_reply(reply)

