import socket
import json
import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# 1. 定义 LSTM 模型结构（必须与训练时一致）
class LSTMModel(torch.nn.Module):
    def __init__(self, input_size=8, hidden_size=64, output_size=1, num_layers=1):
        super(LSTMModel, self).__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])  # 只取最后一个时间步输出


# 2. 超参数（必须和训练时一致）
seq_length = 3
input_size = 8
hidden_size = 64
num_layers = 1
output_size = 1
batch_size = 4
epochs = 100
lr = 0.001

# 3. 加载模型和 scaler（假设你在训练时保存了这些）
checkpoint = torch.load('lstm_model.pth', weights_only=False)

model = LSTMModel(input_size, hidden_size, output_size, num_layers)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()  # 设置为评估模式

scaler_x = checkpoint['scaler_x']  # 输入特征标准化器
scaler_y = checkpoint['scaler_y']  # 输出目标反标准化器


# 4. 封装推理逻辑为函数
def predict_headroom(data_dict):
    """
    接收来自 NS-3 的完整字典数据，返回 headroomRate (float)
    data_dict 格式:
    {
        "port": int,
        "qIndex": int,
        "length": float,
        "time": float,
        "pfcStopStatus": int,
        "qGrowRate": float,
        "qGrowRate20": float,
        "qGrowRate10": float
    }
    """
    df_input = pd.DataFrame([data_dict])
    features = ['port', 'qIndex', 'length', 'time', 'pfcStopStatus', 'qGrowRate', 'qGrowRate20', 'qGrowRate10']
    X_new = df_input[features].values

    X_scaled = scaler_x.transform(X_new)

    history = np.tile(X_scaled, (seq_length - 1, 1))
    current = X_scaled
    X_seq = np.vstack([history, current])

    X_tensor = torch.tensor(X_seq[-seq_length:], dtype=torch.float32).unsqueeze(0)  # (1, seq_length, 8)

    with torch.no_grad():
        output = model(X_tensor)

    predicted_value = scaler_y.inverse_transform(output.numpy())[0][0]
    headroomRate = predicted_value / 1024 / 100 / 8  # 转换公式根据需要调整

    return headroomRate


# 5. 启动 Socket 服务端
HOST = '127.0.0.1'
PORT = 65432

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"Socket 服务已启动，监听 {HOST}:{PORT} ...")

while True:
    conn, addr = server.accept()
    print(f"连接来自: {addr}")

    while True:
        try:
            data = conn.recv(4096).decode('utf-8')
            if not data:
                break

            # 解析 JSON
            payload = json.loads(data.strip())
            headroom = predict_headroom(payload)

            # 返回结果
            conn.sendall(f"{headroom:.6f}\n".encode('utf-8'))

        except Exception as e:
            print("错误:", e)
            break

    conn.close()