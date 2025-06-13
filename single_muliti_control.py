1#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sys
from dynamixel_sdk import *

# 键盘输入兼容处理
if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import tty, termios, select
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def check_exit():
    if os.name == 'nt':
        return msvcrt.kbhit()
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(dr)

# 通信设置
PROTOCOL_VERSION = 2.0
DXL_IDS = [1, 2, 3, 4, 5, 6]
BAUDRATE = 57600
DEVICENAME = '/dev/ttyUSB0'
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
ADDR_OPERATING_MODE = 11
TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

# 初始化
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_GOAL_POSITION, 4)

# 打开串口
if not portHandler.openPort():
    print("打开串口失败")
    quit()
if not portHandler.setBaudRate(BAUDRATE):
    print("设置波特率失败")
    quit()

# 设置模式和使能舵机
for dxl_id in DXL_IDS:
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_OPERATING_MODE, 3)
    packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

# 控制模式 1：波浪运动
def wave_motion():
    print("\n[模式] 波浪运动")
    while True:
        for i in range(6):
            groupSyncWrite.clearParam()
            for j in range(6):
                pos = 1024 if (i + j) % 2 == 0 else 3072
                param = [
                    DXL_LOBYTE(DXL_LOWORD(pos)),
                    DXL_HIBYTE(DXL_LOWORD(pos)),
                    DXL_LOBYTE(DXL_HIWORD(pos)),
                    DXL_HIBYTE(DXL_HIWORD(pos))
                ]
                groupSyncWrite.addParam(DXL_IDS[j], param)
            groupSyncWrite.txPacket()
            time.sleep(0.3)
            if check_exit(): return

# 控制模式 2：对称开合
def mirror_expand_contract():
    print("\n[模式] 对称开合")
    left = [0, 1, 2]
    right = [5, 4, 3]
    while True:
        for pos in [1024, 3072]:
            groupSyncWrite.clearParam()
            param = [
                DXL_LOBYTE(DXL_LOWORD(pos)),
                DXL_HIBYTE(DXL_LOWORD(pos)),
                DXL_LOBYTE(DXL_HIWORD(pos)),
                DXL_HIBYTE(DXL_HIWORD(pos))
            ]
            for i in range(3):
                groupSyncWrite.addParam(DXL_IDS[left[i]], param)
                groupSyncWrite.addParam(DXL_IDS[right[i]], param)
            groupSyncWrite.txPacket()
            time.sleep(0.5)
            if check_exit(): return

# 控制模式 3：键盘控制单个舵机
def keyboard_control_single_motor():
    print("\n[模式] 键盘控制 1~6 选择舵机, a/d 控制方向, q 退出")
    selected = DXL_IDS[0]
    position_map = {dxl_id: 2048 for dxl_id in DXL_IDS}
    while True:
        key = getch()
        if key in '123456':
            selected = int(key)
            print(f"选择舵机: {selected}")
        elif key == 'a':
            position_map[selected] = max(0, position_map[selected] - 100)
        elif key == 'd':
            position_map[selected] = min(4095, position_map[selected] + 100)
        elif key == 'q':
            break
        else:
            continue

        pos = position_map[selected]
        param = [
            DXL_LOBYTE(DXL_LOWORD(pos)),
            DXL_HIBYTE(DXL_LOWORD(pos)),
            DXL_LOBYTE(DXL_HIWORD(pos)),
            DXL_HIBYTE(DXL_HIWORD(pos))
        ]
        groupSyncWrite.clearParam()
        groupSyncWrite.addParam(selected, param)
        groupSyncWrite.txPacket()
        print(f"舵机 {selected} 移动到位置: {pos}")

# 主入口
if __name__ == "__main__":
    print("\n请选择控制模式：")
    print("1. 波浪运动")
    print("2. 对称开合")
    print("3. 键盘控制单个舵机")
    mode = input("输入 1/2/3 选择模式：")

    try:
        if mode == '1':
            wave_motion()
        elif mode == '2':
            mirror_expand_contract()
        elif mode == '3':
            keyboard_control_single_motor()
        else:
            print("无效输入")
    finally:
        # 关闭力矩和端口
        for dxl_id in DXL_IDS:
            packetHandler.write1ByteTxRx(portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        portHandler.closePort()
        print("已关闭串口和关闭所有舵机力矩")
