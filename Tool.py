from configparser import ConfigParser

import matplotlib.pyplot as plt
import numpy as np
from math import sqrt
from Net import NetWork

plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示汉字
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

config = ConfigParser()
config.read("enviro.ini", encoding="utf-8")


def show_image(show_sensors, **show_type):
    # 非簇头位置集合
    sensor3D_x = []
    sensor3D_y = []
    sensor3D_z = []
    sensor_count = 0
    ax = plt.axes(projection='3d')
    for show_sensor in show_sensors.values():
        if show_sensor.node_type == "Sensor":
            sensor_count += 1
            sensor3D_x.append(show_sensor.node_x)
            sensor3D_y.append(show_sensor.node_y)
            sensor3D_z.append(show_sensor.node_z)
            ax.text(show_sensor.node_x, show_sensor.node_y, show_sensor.node_z, "ID:" + str(show_sensor.node_id) + "V:" + str(show_sensor.v))
    ax.scatter3D(sensor3D_x, sensor3D_y, sensor3D_z, c='#768dd1', alpha=0.8)
    ax.scatter3D(NetWork.length / 2, NetWork.width / 2, 0, s=30, c='#fac857', alpha=1)
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
                             [show_sensor.node_z, show_type["route_map"][show_sensor.node_id].node_z], c='#768dd1',
                             alpha=0.8)
    plt.show()


def show_route_line(node1, node2, show_sensors):
    # 非簇头位置集合
    sensor3D_x = []
    sensor3D_y = []
    sensor3D_z = []
    sensor_count = 0
    ax = plt.axes(projection='3d')
    for show_sensor in show_sensors.values():
        if show_sensor.node_type == "Sensor" and show_sensor.node_id != node2.node_id:
            sensor_count += 1
            sensor3D_x.append(show_sensor.node_x)
            sensor3D_y.append(show_sensor.node_y)
            sensor3D_z.append(show_sensor.node_z)
    ax.scatter3D(sensor3D_x, sensor3D_y, sensor3D_z, c='#768dd1', alpha=0.8)
    ax.scatter3D(node2.node_x, node2.node_y, node2.node_z, c='r', alpha=0.8)
    ax.scatter3D(NetWork.length / 2, NetWork.width / 2, 0, s=30, c='#fac857', alpha=1)
    plt.plot([node1.node_x, node2.node_x],
             [node1.node_y, node2.node_y],
             [node1.node_z, node2.node_z], c='#768dd1',
             alpha=0.8)
    plt.show()


def show_v_change(node):
    x = np.arange(len(node.v_list))
    fig, ax = plt.subplots()
    plt.ylim(config["learn"].getint("constant_punishment") * -2 - 1, 0)
    ax.plot(x, node.v_list, c='#768dd1')
    ax.set_xlabel("数据传输轮数")
    ax.set_ylabel("V值")
    plt.title("Node ID: " + str(node.node_id))
    plt.show()


def show_v_ave_change(v_list):
    x = np.arange(len(v_list))
    plt.ylim(config["learn"].getint("constant_punishment") * -2 - 1, 0)
    fig, ax = plt.subplots()
    ax.plot(x, v_list, c='#768dd1')
    ax.set_xlabel("发送数据包数量")
    ax.set_ylabel("V值")
    plt.title("V值变化图")
    plt.show()


def all_node_energy_image():
    x = np.arange(len(NetWork.all_node_energy_list))
    print(NetWork.all_node_energy_list)
    print(x)
    print(len(x))
    print(len(NetWork.all_node_energy_list))
    fig, ax = plt.subplots()
    ax.plot(x, NetWork.all_node_energy_list, c='#768dd1')
    ax.set_xlabel("数据传输轮数")
    ax.set_ylabel("节点总能量")
    plt.show()





def init_train(rounds):
    nodes_map = NetWork.nodes_map
    nodes_map[-1] = NetWork.sink
    for train_round in range(rounds):
        for node in nodes_map.values():
            if node.node_type != 'Sink':
                neighbor_list = node.choose_action()  # 获得存活的邻居节点列表
                # node.learn(neighbor_list)
        print("\repisode of train:{}".format(train_round), end='')





def calcu_distance(node, destination):
    result = sqrt((node.node_x - destination.node_x) ** 2 + (node.node_y - destination.node_y) ** 2 + (
            node.node_z - destination.node_z) ** 2)
    return result

