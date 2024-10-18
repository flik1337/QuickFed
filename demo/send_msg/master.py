import flask
from flask import request

app = flask.Flask(__name__)

# 路径用于接收来自slave节点的信息
@app.route('/message', methods=['POST'])
def message():
    data = request.get_json()
    print(f"Received message from slave: {data['message']}")
    app.logger.info(f"Received message from slave: {data['message']}")
    return "Message received"

# 启动服务
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
