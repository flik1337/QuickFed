import requests
import time

# master节点的服务地址
master_url = "http://master-service:5000/message"

# 向master节点周期性发送信息
while True:
    try:
        response = requests.post(master_url, json={"message": "Hello from slave"})
        print("Message sent to master", response.text)

    except:
        print("Failed to send message")
    time.sleep(10)  # 每10秒发送一次信息
