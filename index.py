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


def handler(event, context):
	
    request = json.loads(event)
    logger = logging.getLogger()
    body = base64.b64decode(request['body']).decode()
    data = json.loads(body)

    logger.info('request body:' + body)

    # 从请求中获取意图参数以及参数值
    intent_name = data['intentName']

    reply = None
	trade = None
	group = None

    # 处理名称为 guide 的意图
    if intent_name == "guide":
		
        reply = '好的主人，您可以跟精灵说：写报告或者运行流程'
        return common_reply(reply, 'ASK_INF', None, data['intentId'])

    # 处理名称为 report 的意图
    elif intent_name == "report":
		
		#提取参数
        for slot in data['slotEntities']:
            if slot['intentParameterName'] == "trade":
                trade = "关于"+slot['slotValue']

            elif slot['intentParameterName'] == "group":
                group = slot['slotValue']

        if trade =="关于自由发挥":
            reply = '好的,开始自由发挥写报告。'
			
        else:
            reply = '好的,开始写'+trade+"的报告。"
			
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
		  }         
		]
		
		accessToken = shadow.getAccessToken()
		
		robotUuid = shadow.queryRoot(accessToken, "写报告")
		
		shadow.informationOfDispatch["robotUuid"] = robotUuid
		
		shadow.startJob(accessToken,informationOfrobot)

		return common_reply(reply, 'RESULT', None, None, None)
		
    reply = '请检查意图名称是否正确，或者新增的意图没有在代码里添加对应的处理分支。'

    return common_reply(reply, 'RESULT', None, None, None)

