from dynamixel_sdk import *

# 通信参数
DEVICENAME = '/dev/ttyUSB0'
BAUDRATE = 57600
PROTOCOL_VERSION = 2.0

# 控制表地址
ADDR_ID = 7
BROADCAST_ID = 254
NEW_ID = 12

# 初始化
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# 打开串口
if not portHandler.openPort():
    print("❌ 串口打开失败")
    quit()
portHandler.setBaudRate(BAUDRATE)

# 写入新 ID
dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, BROADCAST_ID, ADDR_ID, NEW_ID)
if dxl_comm_result != COMM_SUCCESS:
    print("❌ 通信失败:", packetHandler.getTxRxResult(dxl_comm_result))
elif dxl_error != 0:
    print("⚠️ 错误:", packetHandler.getRxPacketError(dxl_error))
else:
    print("✅ 舵机ID已设置为:", NEW_ID)

portHandler.closePort()
