from py_libs.comm.bridge import Bridge

def main():
    # 初始化Bridge
    bridge = Bridge('mypipe.fifo')

    # 持续监听消息
    print("Waiting for messages...")
    while True:
        received_message = bridge.receive()
        print(f"Received message: {received_message.content}")


if __name__ == "__main__":
    main()