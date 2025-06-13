from dynamixel_sdk import *

# 配置参数
DEVICENAME = "/dev/ttyUSB0"
BAUDRATE = 57600
PROTOCOL_VERSION = 2.0

OLD_ID = 12  # 出厂默认电机ID，修改电机ID后可修改参数验证是否成功修改ID

# 初始化端口
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# 打开串口
if not portHandler.openPort():
    print("❌ 无法打开串口")
    exit()
if not portHandler.setBaudRate(BAUDRATE):
    print("❌ 无法设置波特率")
    exit()

# Ping 旧 ID
dxl_model_number, dxl_comm_result, dxl_error = packetHandler.ping(portHandler, OLD_ID)
if dxl_comm_result != COMM_SUCCESS:
    print("❌ 未检测到电机，检查连接！")
else:
    print(f"✅ 发现电机，ID: {OLD_ID}, 型号: {dxl_model_number}")

# 关闭端口
portHandler.closePort()
