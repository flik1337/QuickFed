from bridge import Bridge
import message_pb2
import time

class _send_msg:
    def __init__(self, fifo_name):
        # 获取当前文件（bridge.py）的目录路径
        self.ensure_fifo_exists()

def main():
    # 初始化Bridge
    bridge = Bridge('mypipe.fifo')

    while True:
        # 创建消息
        message = message_pb2.SimpleMessage()
        message.content = f"Hello from sender at {time.ctime()}"

        # 发送消息
        bridge.send(message)
        print(f"Message sent at {time.ctime()}")

        # 每10秒发送一次
        time.sleep(2)


if __name__ == "__main__":
    main()
