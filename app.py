from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import threading
import json

app = Flask(__name__)

# ================= 配置 =================
# 巴法云的 MQTT 地址
BEMFA_BROKER = "bemfa.com"
BEMFA_PORT = 9501
# 填你的私钥 (UID)
BEMFA_UID = "这里填你的巴法云私钥UID"
# 监听的主题 (和板子发的主题一致)
TOPIC = "water"

# 全局变量存储结果
bird_count = 0
latest_msg = "No Data"

# ================= MQTT 回调函数 =================
def on_connect(client, userdata, flags, rc):
    print("Connected to Bemfa Cloud!")
    # 订阅主题
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global bird_count, latest_msg
    try:
        # 假设板子发来的数据格式是: "BirdDetected:1" 
        # 或者如果是图片Hex流，这里需要复杂的拼接逻辑
        payload = msg.payload.decode('utf-8')
        latest_msg = payload
        print(f"Received: {payload}")
        
        # 简单的逻辑：如果板子发来 "Motion", 计数+1
        # 如果你真的传了图片Base64，这里要解码并传给YOLO
        if "Motion" in payload:
            bird_count += 1
            
    except Exception as e:
        print(f"Error: {e}")

# ================= 启动 MQTT 线程 =================
def start_mqtt():
    client = mqtt.Client(client_id=BEMFA_UID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BEMFA_BROKER, BEMFA_PORT, 60)
    client.loop_forever()

# 开启后台线程跑 MQTT，不阻塞 Flask
threading.Thread(target=start_mqtt, daemon=True).start()

# ================= 前端 API 接口 =================
@app.route('/')
def index():
    return "Renesa AI Server is Running!"

# 你的前端网站通过这个接口获取数据
@app.route('/api/data')
def get_data():
    return jsonify({
        "status": "ok",
        "birds": bird_count,
        "raw_msg": latest_msg
    })

if __name__ == '__main__':
    # Render 会通过 PORT 环境变量指定端口
    app.run(host='0.0.0.0', port=10000)
