import requests
import json
import time


def callApi(url, data, headers=None, method=None):
  """
  调用接口返回json数据(字典)
  """
  if method == 'GET':
      result = requests.get(url=url, params=data, headers=headers).text
      return json.loads(result)
  elif method == 'POST':
      result = requests.post(url=url, data=data, headers=headers).text
      return json.loads(result)


def getAccessToken():
  """
  获取accessToken
  :return:accessToken
  """
  accessToken = callApi(
      urls['getAccessToken'].format(informationOfDispatch['accessKeyId'], informationOfDispatch['accessKeySecret']),
      None, {'Content-Type': 'application/x-www-form-urlencoded'}, method[0])['data']['accessToken']
  print('已获取accessToken：{}'.format(accessToken))
  print('-----------------------帅气的分割线-------------------------\n')
  return accessToken


def getClientData(accessToken):
  """
  获取客户端状态（connected:已连接 idle:空闲 running:运行中 allocated:已分配 abnormal:异常 offline:离线）
  :return:clientStatus
  """
  headers = {'Content-Type': 'application/json', 'authorization': 'Bearer {}'.format(accessToken)}
  data = json.dumps({
      "accountName": informationOfDispatch["accountName"]
  })
  clientStatus = callApi(urls['queryClient'], data, headers, method[1])['data']['status']
  print('已获取clientStatus：' + clientStatus)
  if clientStatus == 'offline':
      print('请注意！检查是否已开启调度模式！')
  print('-----------------------帅气的分割线-------------------------\n')
  return clientStatus


def startJob(accessToken,informationOfrobot):
  """
  启动任务，并返回jobUuid
  :return:jobUuid
  """
  data = json.dumps({
      "accountName": informationOfDispatch["accountName"],
      "robotUuid": informationOfDispatch["robotUuid"],
      "params": informationOfrobot
  })
  headers = {'Content-Type': 'application/json', 'authorization': 'Bearer {}'.format(accessToken)}
  jobUuid = callApi(urls['startJob'], data, headers, method[1])['data']['jobUuid']
  print('已获取jobUuid：' + jobUuid)
  print('-----------------------帅气的分割线-------------------------\n')
  return jobUuid


def stopJob(accessToken):
  """
  停止任务，并返回jobUuid
  :return:
  """
  data = json.dumps({
      "jobUuid": informationOfDispatch["jobUuid"],
  })
  headers = {'Content-Type': 'application/json', 'authorization': 'Bearer {}'.format(accessToken)}
  result = callApi(urls['stopJpb'], data, headers, method[1])["success"]
  print("停止成功："+str(result))
  print('-----------------------帅气的分割线-------------------------\n')
  return result



def query(accessToken, jobUuid):
  """
  查询应用启动结果
  :return:
  """
  data = json.dumps({
    "jobUuid": jobUuid,
  })
  headers = {'Content-Type': 'application/json', 'authorization': 'Bearer {}'.format(accessToken)}
  # while True:
  response = callApi(urls['query'], data, headers, method[1])['data']['status']
  print(response)

  if response == 'error':
    print('应用运行异常！请检查入参或者指令！\n')
    # break
  elif response == 'finish':
    print('应用运行完成，调度结束！\n')
    # break
  elif response == 'stopped':
    print('应用已暂停\n')
  else:
    print('应用还在运行中.......\n')

  print('-----------------------帅气的分割线-------------------------\n')
  time.sleep(2)
    

def queryRoot(accessToken, rootName):
  '''
  查询应用列表
  :return:应用id
  '''
  data = {
    "accurateRobotName": rootName,
  }

  headers = {'Content-Type': 'application/json', 'authorization': 'Bearer {}'.format(accessToken)}
  result = callApi(urls['queryRobot'], data, headers,method[0])

  for i in result["data"]:
      if i["ownerName"] == informationOfDispatch["accountName"]:
          robotUuid = i["robotUuid"]

  print(rootName+"的id是："+robotUuid)
  print('-----------------------帅气的分割线-------------------------\n')
  
  return robotUuid

# 调用的接口网址
urls = {
    'getAccessToken': 'https://api.winrobot360.com/oapi/token/v2/token/create?accessKeyId={}&accessKeySecret={}',
    'startJob': 'https://api.winrobot360.com/oapi/dispatch/v2/job/start',
    'startTask':'https://api.winrobot360.com/oapi/dispatch/v2/task/start',
    'stopJpb':'https://api.winrobot360.com/oapi/dispatch/v2/job/stop',
    'stoptask':'https://api.winrobot360.com/oapi/dispatch/v2/task/stop',
    'query':'https://api.winrobot360.com/oapi/dispatch/v2/job/query',
    'queryClient': 'https://api.winrobot360.com/oapi/dispatch/v2/client/query',
    'queryRobot':'https://api.winrobot360.com/oapi/robot/v2/query'
}



# 请求方法
method = ['GET', 'POST']

# todo -------------------------改变调度相关信息和应用入参即可------------------------------------------
# 调度相关信息
informationOfDispatch = {
    'accessKeyId': '',
    'accessKeySecret': '',
    "accountName": "",
    "robotUuid": "",
    "jobUuid":"",
    "taskUuid":''
}


if __name__ == '__main__':

  # 应用入参
  informationOfrobot = [
    {
      "name":"group", #//应用参数名称
      "value":None, #// 应用参数值
      "type":"str" #//参考应用运行参数枚举说明
      },
      {
        "name":"trade",
        "value":"RPA",
        "type":"str"
        }
  ]

  accessToken = getAccessToken()

  clientStatus = getClientData(accessToken)

  if clientStatus != "abnormal" and clientStatus != "offline":

    robotUuid = queryRoot(accessToken,"写报告")

    informationOfDispatch["robotUuid"] = robotUuid

    jobUuid = startJob(accessToken,informationOfrobot)

    informationOfDispatch["jobUuid"] =jobUuid

    # query(accessToken, jobUuid)

    time.sleep(5)

    query(accessToken, jobUuid)

    # time.sleep(1)
    # stopJob(accessToken)