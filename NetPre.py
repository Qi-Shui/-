from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
import random

import pandas as pd
from mpl_toolkits.mplot3d import Axes3D

from Sensor import Sensor
from Sink import Sink

pd.set_option('display.max_rows', None)
np.set_printoptions(threshold=np.inf)
pd.set_option('expand_frame_repr', False)
plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示汉字
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

net_size = 5000
node_num = 500
e_ini = 0.1
np.random.seed(6)
data = np.random.uniform(0, net_size, (node_num, 3))
x = data[:, 0]
y = data[:, 1]
z = data[:, 2]
T = np.arctan2(y, x)


# 初始化节点
def initSensors():
    sensor_map = {
        0: Sink(node_id=0, node_x=net_size / 2, node_y=net_size / 2, node_z=0, net_length=net_size, net_width=net_size,
                net_height=net_size, node_type='sink_node', e_ini=e_ini)}
    for index in range(0, node_num):
        sensor_map[index + 1] = Sensor(node_id=index + 1, node_x=x[index], node_y=y[index], node_z=-z[index],
                                       sink_x=net_size / 2, sink_y=net_size / 2, sink_z=0, node_type='sensor_node',
                                       net_length=net_size, net_width=net_size, net_height=net_size, e_ini=e_ini)
    return sensor_map


def showImage(show_sensors, **show_type):
    # 初始化簇头后的图像
    head3D_x = []  # 簇头位置集合
    head3D_y = []
    head3D_z = []
    sensor3D_x = []  # 非簇头位置集合
    sensor3D_y = []
    sensor3D_z = []
    head_count_num = 0
    ax = plt.axes(projection='3d')
    for show_sensor in show_sensors.values():
        if show_sensor.node_type == "head_node":
            head_count_num += 1
            head3D_x.append(show_sensor.node_x)
            head3D_y.append(show_sensor.node_y)
            head3D_z.append(show_sensor.node_z)
            # ax.scatter3D(sensor.node_x, sensor.node_y, sensor.node_z, c='r', alpha=0.5)
            # plt.scatter(sensor.node_x, sensor.node_y, s=50, c="r", alpha=0.5)
        if show_sensor.node_type == "sensor_node" and show_sensor.state == 1:
            sensor3D_x.append(show_sensor.node_x)
            sensor3D_y.append(show_sensor.node_y)
            sensor3D_z.append(show_sensor.node_z)
            # ax.scatter3D(sensor.node_x, sensor.node_y, sensor.node_z, c='g', alpha=0.5)
            # plt.scatter(sensor.node_x, sensor.node_y, s=50, c="g", alpha=0.5)
    # plt.scatter(0, net_size / 2, s=80, c="b", alpha=0.5)
    print(head_count_num)
    ax.scatter3D(head3D_x, head3D_y, head3D_z, c='#768dd1', alpha=0.8)
    ax.scatter3D(sensor3D_x, sensor3D_y, sensor3D_z, c='#a7d691', alpha=0.8)
    ax.scatter3D(net_size / 2, net_size / 2, 0, s=30, c='#fac857', alpha=1)
    if len(show_type) > 0:
        for show_sensor in show_sensors.values():
            if show_sensor.node_type == "sensor_node":
                if show_type["what"] >= 1:
                    plt.plot([show_sensor.node_x, show_sensor.head_x], [show_sensor.node_y, show_sensor.head_y],
                             [show_sensor.node_z, show_sensor.head_z], c='#a7d691', alpha=0.3)
            if show_sensor.node_type == "head_node":
                if show_type["what"] >= 2:
                    plt.plot([show_sensor.node_x, show_type["route_map"][show_sensor.node_id].node_x],
                             [show_sensor.node_y, show_type["route_map"][show_sensor.node_id].node_y],
                             [show_sensor.node_z, show_type["route_map"][show_sensor.node_id].node_z], c='#768dd1', alpha=0.8)
    plt.show()


sensors = initSensors()
total_energy = pd.DataFrame([0, node_num * e_ini], index=['x', 'y'], columns=[1], dtype=np.float64)
total_survival = pd.DataFrame([0, node_num], index=['x', 'y'], columns=[1], dtype=np.float64)

episode = 1
flag = {"1": 0, "30%": 0, "50%": 0, "90%": 0, "100%": 0}
sink = sensors[0]
ave_energy_list = np.zeros(sensors[0].total_layer + 1)
ave_head_energy_list = np.zeros(sensors[0].total_layer + 1)
while 1:



    layer_count = np.zeros(6)
    for sensor in sensors.values():
        if sensor.node_type != "sink_node" and sensor.node_type != "dead_node":
            sensor.new_episode()  # 新一轮重置数据
            layer_count[sensor.layer] += 1  # 统计每层传感器个数
        # for node in sensors.values():  # 计算各传感器竞争半径内的传感器个数
        #     if sqrt((sensor.node_x - node.node_x) ** 2 + (sensor.node_y - node.node_y) ** 2 + (
        #             sensor.node_z - node.node_z) ** 2) < sensor.comp_radius:
        #         sensor.in_comp_radius_sensor_count += 1

    # 计算传感器的度
    # for sensor in sensors.values():
    #     if layer_count[sensor.layer] == 0:
    #         continue
    #     sensor.degree = sensor.in_comp_radius_sensor_count / layer_count[sensor.layer]

    showImage(sensors)

    if episode == 1:
        l1 = int(layer_count[1] * sink.heads_proportion)
        l2 = int(layer_count[2] * sink.heads_proportion)
        l3 = int(layer_count[3] * sink.heads_proportion)
        l4 = int(layer_count[4] * sink.heads_proportion)
        l5 = int(layer_count[5] * sink.heads_proportion)
        sink.head_num = [0, l1, l2, l3, l4, l5]
        # 第一次竞选簇头
        for sensor in sensors.values():
            if sensor.node_type != "sink_node":
                if sensor.layer == 1:
                    sink.sensors_of_layer_1[sensor.node_id] = 0
                if sensor.layer == 2:
                    sink.sensors_of_layer_2[sensor.node_id] = 0
                if sensor.layer == 3:
                    sink.sensors_of_layer_3[sensor.node_id] = 0
                if sensor.layer == 4:
                    sink.sensors_of_layer_4[sensor.node_id] = 0
                if sensor.layer == 5:
                    sink.sensors_of_layer_5[sensor.node_id] = 0
        line_1 = sink.sensors_of_layer_1.sample(n=l1, replace=False, axis=1).columns
        line_2 = sink.sensors_of_layer_2.sample(n=l2, replace=False, axis=1).columns
        line_3 = sink.sensors_of_layer_3.sample(n=l3, replace=False, axis=1).columns
        line_4 = sink.sensors_of_layer_4.sample(n=l4, replace=False, axis=1).columns
        line_5 = sink.sensors_of_layer_5.sample(n=l5, replace=False, axis=1).columns
        for i in range (0,l1):
            sensors[line_1[i]].node_type = "head_node"
        for i in range (0,l2):
            sensors[line_2[i]].node_type = "head_node"
        for i in range (0,l3):
            sensors[line_3[i]].node_type = "head_node"
        for i in range (0,l4):
            sensors[line_4[i]].node_type = "head_node"
        for i in range (0,l5):
            sensors[line_5[i]].node_type = "head_node"
        break
    else:
        # 非第一次选簇头
        sensors[0].clear_layer_sensors()
        for sensor in sensors.values():
            if sensor.node_type != "sink_node" and sensor.node_type != "dead_node":
                sensors[0].sensors_of_layer[sensor.node_id] = 0

    # 初始化簇头后的图像
    showImage(sensors)

    for sensor in sensors.values():
        # 非簇头节点选择簇头广播信号更强的那个,并且记录该簇头id和距离该簇头的距离
        if sensor.node_type == "sensor_node":
            for find_head in sensors.values():
                if find_head.node_type == "head_node" or find_head.node_type == "sink_node":
                    d_head = sqrt((sensor.node_x - find_head.node_x) ** 2 + (sensor.node_y - find_head.node_y) ** 2 + (
                            sensor.node_z - find_head.node_z) ** 2)
                    if d_head < sensor.d_head:
                        sensor.d_head = d_head
                        sensor.head_id = find_head.node_id
                        sensor.head_x = find_head.node_x
                        sensor.head_y = find_head.node_y
                        sensor.head_z = find_head.node_z
            # 非簇头节点确定簇头节点后，向簇头节点发送确认成簇广播数据包
            # sensor.send_energy(sensor.broadcast_data, sensor.d_head)
            # 增加簇头节点的簇间传感器数量
            sensors[sensor.head_id].intra_sensor_count += 1
            # print(sensor.layer, sensor.head_id, sensor.d_head)

    # showImage(sensors, what=1)

    for sensor in sensors.values():
        if sensor.node_type == "sensor_node":  # 簇间节点向簇头节点发送数据包，计算非簇头节点的能耗
            sensor.send_energy(sensor.transport_data, sensor.d_head)
        if sensor.node_type == "head_node":  # 簇头节点接收簇间节点发送的数据包，计算簇头节点的能耗
            sensor.receive_energy(sensor.transport_data * sensor.intra_sensor_count)

    # 获取簇头节集合，以方便强化学习寻找路由
    heads = {0: sensors[0]}
    for sensor in sensors.values():
        if sensor.node_type == "head_node":
            heads[sensor.node_id] = sensors[sensor.node_id]

    for learn_round in range(500):
        for head in heads.values():
            if head.node_type != 'sink_node':
                next_head_id = head.choose_action(heads)  # 获得下一跳头节点的id
                head.learn(heads[next_head_id])
        print("\repisode of learn:{}".format(learn_round), end='')
    print("\repisode:{}".format(episode), end='')
    print()
    # for head in heads.values():
    #     print(head.q_table)
    route_map = {}
    # 根据每个头节点的q表，建立路由网络
    for head in heads.values():
        head_q = head.q_table.iloc[0]
        next_head_id = np.random.choice(head_q[head_q == head_q.max()].index)
        route_map[head.node_id] = heads[next_head_id]

    # if episode >= 200:
    #     showImage(sensors, what=2, route_map=route_map)

    # 根据路由网络，计算各个头节点需要中继的数据量
    for head in heads.values():
        next_id = route_map[head.node_id].node_id
        press = 0.5
        while next_id != 0:
            route_map[next_id].total_data_size += heads[head.node_id].intra_sensor_count * head.transport_data * press
            next_id = route_map[next_id].node_id


    # 一轮结束后，移除能量耗尽的节点
    for key in list(sensors.keys()):
        if sensors[key].energy < 0:
            print(sensors[key].node_id, "号传感器节点在第", episode, "轮能量耗尽")
            sensors[key].node_type = "dead_node"
            sensors[key].energy = 0

    #     # 一轮结束后，计算每层平均剩余能量，存储在sink节点中
    # layer_node_count = np.zeros(5)
    # for sensor in sensors.values():
    #     if sensor.node_type != "sink_node" and sensor.state == 1:
    #         layer_node_count[sensor.layer] += 1
    # print(layer_node_count)

    # 一轮结束后，计算每层平均剩余能量，存储在sink节点中

    layer_node_count = np.zeros(sensors[0].total_layer + 1)
    survival_count = 0
    remain_energy = 0
    for sensor in sensors.values():
        if sensor.node_type != "sink_node" and sensor.node_type != "dead_node":
            if sensor.node_type == "head_node":
                ave_head_energy_list[sensor.layer] += sensor.energy
            remain_energy += sensor.energy
            ave_energy_list[sensor.layer] += sensor.energy
            layer_node_count[sensor.layer] += 1
            survival_count += 1
    # 统计总能量
    total_energy.loc['x', episode] = episode
    total_energy.loc['y', episode] = remain_energy
    total_survival.loc['x', episode] = episode
    total_survival.loc['y', episode] = survival_count
    if survival_count <= node_num - 1 and flag["1"] == 0:  # 第一个节点死亡
        flag["1"] = episode
    if survival_count <= node_num * 0.7 and flag["30%"] == 0:
        flag["30%"] = episode
    if survival_count <= node_num * 0.5 and flag["50%"] == 0:
        flag["50%"] = episode
    if survival_count <= node_num * 0.1 and flag["90%"] == 0:
        flag["90%"] = episode
    if survival_count == 0:
        flag["100%"] = episode

    for i in range(1, layer_node_count.size):
        if layer_node_count[i] == 0:
            ave_energy_list[i] = 0
            break
        ave_energy_list[i] /= layer_node_count[i]
        ave_head_energy_list[i] /= sink.head_num[i]
    sensors[0].layer_ave_energy_list = ave_energy_list
    print("每层存活传感器平均能量", ave_energy_list)
    print("每层存活传感器数量", layer_node_count)
    for sensor in sensors.values():
        if sensor.node_type != "sink_node" and sensor.node_type != "dead_node":
            sensor.layer_ave_energy = sensors[0].layer_ave_energy_list[sensor.layer]
    if survival_count == 0:
        print("所有传感器节点能量耗尽，当前轮次为", episode)
        break
    episode += 1
    # if episode >= 200:


print(flag)
x_data = total_energy.loc['x', :]  # X轴数据 int类型数据
y_data = total_energy.loc['y', :]  # Y轴数据
plt.title("网络能耗情况")  # 折线图标题
plt.xlabel("仿真时间/轮")  # X轴名称
plt.ylabel("网络节点总能量/J")  # Y轴名称

plt.plot(x_data, y_data)  # 绘制折线图
plt.legend(['LEACH'])  # 设置折线名称
plt.show()  # 显示折线图

x_data = total_survival.loc['x', :]  # X轴数据 int类型数据
y_data = total_survival.loc['y', :]  # Y轴数据
plt.title("节点存活情况")  # 折线图标题4
plt.xlabel("仿真时间/轮")  # X轴名称
plt.ylabel("存活节点数")  # Y轴名称

plt.plot(x_data, y_data)  # 绘制折线图
plt.legend(['LEACH'])  # 设置折线名称
plt.show()  # 显示折线图


# for sensor in sensors.values():
#     print(sensor.node_id, "state: ", sensor.state, "layer", sensor.layer, "node_type: ", sensor.node_type,
#           "energy: ",
#           sensor.energy,
#           "count: ", sensor.intra_sensor_count, "head_id: ", sensor.head_id, "radius", sensor.comp_radius)

# map测试分层
# sensors = initSensors()
# a = np.zeros(11)
# b = np.zeros(11)
# min_comp = 900
# max_comp = 0
# sum = 0
# for sensor in sensors.values():
#     if sensor.node_type == "head_node":
#         a[sensor.layer] += 1
#     if sensor.node_type != "sink_node":
#         min_comp = min(sensor.comp_radius, min_comp)
#     max_comp = max(sensor.comp_radius, max_comp)
#     if sensor.node_type != "sink_node":
#         sum += sensor.comp_radius
#     b[sensor.layer] += 1
#     print(sensor.node_id, "layer", sensor.layer, "comp_radius", sensor.comp_radius)
# print(a)
# print(b)
# print(min_comp, max_comp, sum / 500)

# 列表测试分层
# sensors = initSensors()
# a = np.zeros(11)
# b = np.zeros(11)
# min_comp = 900
# max_comp = 0
# sum = 0
# for sensor in sensors:
#     if sensor.node_type == "head_node":
#         a[sensor.layer] += 1
#     if sensor.node_type != "sink_node":
#         min_comp = min(sensor.comp_radius, min_comp)
#     max_comp = max(sensor.comp_radius, max_comp)
#     if sensor.node_type != "sink_node":
#         sum += sensor.comp_radius
#     b[sensor.layer] += 1
#     print(sensor.node_id, "layer", sensor.layer, "comp_radius", sensor.comp_radius)
# print(a)
# print(b)
# print(min_comp, max_comp, sum / 500)
