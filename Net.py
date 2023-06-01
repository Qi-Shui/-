import time
from configparser import ConfigParser
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt

import Tool
from Node import Node
from Sensor import Sensor
from Sink import Sink


class NetWork:
    """ 网络参数设置 """
    config = ConfigParser()
    config.read("enviro.ini", encoding="utf-8")
    length = config["net"].getint("length")  # Length of the yard
    width = config["net"].getint("width")  # Width of the yard
    high = config["net"].getint("high")  # Width of the yard
    n = config["net"].getint("n")  # total number of nodes
    init_train_round = config["net"].getint("init_train_round")  # total number of nodes
    trans_round = config["net"].getint("trans_round")
    package_id = 1

    # 网络属性
    sink = None  # Sink node
    nodes = None  # All sensor nodes set
    nodes_map = {}
    episode = None

    # 数据包传输参数
    miss_package = 0
    all_package = n * config["net"].getint("trans_round")  # 初始能量

    # Node State in Network
    all_node_energy_list = []
    survivor_count = 0
    n_dead = 0  # The number of dead nodes
    flag_first_dead = 0  # Flag tells that the first node died
    flag_all_dead = 0  # Flag tells that all nodes died
    flag_net_stop = 0  # Flag tells that network stop working:90% nodes died
    time_first_dead = 0  # The time when the first node died
    time_all_dead = 0  # The time when all nodes died
    time_net_stop = 0  # The time when the network stop working
    round_first_dead = config["net"].getint("trans_round")  # The round when the first node died
    round_all_dead = 0  # The round when all nodes died
    round_net_stop = 0  # The round when the network stop working

    def init_node(self):
        """ 初始化节点 """
        np.random.seed(6)
        data = np.random.uniform(0, self.length, (self.n, 3))
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]
        nodes = []
        nodes_map = {}
        for i in range(self.n):
            node = Sensor(i, x[i], y[i], z[i])
            nodes.append(node)
        for node in nodes:
            nodes_map[str(node.node_id)] = node  # 成员为空列表
        self.nodes_map = nodes_map
        # Initial sink node
        sink = Sink('-1', self.length / 2, self.width / 2, 0)
        # Add to NetWork
        self.nodes = nodes
        self.sink = sink
        self.update_all_node_energy()  # 统计所有节点能量和
        print("节点初始化 完成")

    def find_neighbor(self):
        nodes_map = self.nodes_map
        nodes_map[self.sink.node_id] = self.sink
        for node in nodes_map.values():
            # 每个节点以自己的传输半径为距离发送广播节点
            node.send_energy(node.BM, node.com_range)  # 发送广播包
            for neighbor in nodes_map.values():
                distance = Tool.calcu_distance(node, neighbor)
                if neighbor.com_range >= distance and neighbor.node_id != node.node_id:
                    node.neighbors.append(neighbor)
                    neighbor.send_energy(neighbor.CM, distance)  # 发送ACK包
                    neighbor.receive_energy(neighbor.BM)  # 接收广播包
            node.find_alive_neighbor()  # 初始化邻居节点的Q表
            node.receive_energy(node.CM * node.q_table.columns.size)  # 接收ACK包

    def transmission(self, rounds):
        nodes_map = self.nodes_map
        nodes_map[self.sink.node_id] = self.sink
        for train_round in range(rounds):
            self.update_survivor_node(nodes_map)
            for node in nodes_map.values():
                self.package_id += 1
                source_node = node
                node.storage.append(self.package_id)
                # node.pre_node = node.node_id
                while node.node_type != 'Sink':
                    node_id = node.choose_action()  # 选择下一个动作
                    # print(node_id)
                    if node_id == -2:  # 无邻居节点，放弃传输，丢弃包
                        self.miss_package += 1
                        break
                    neighbor = nodes_map[str(node_id)]
                    if self.retransmission(node, neighbor, source_node) == -1:  # 判断重传，-1为传输失败，进行下一个源节点传输数据
                        break
                    neighbor.pre_node = node.node_id
                    node = neighbor
            print("\repisode of transmission:{}".format(train_round), end='')
            self.update_all_node_energy()

    def retransmission(self, node, neighbor, source_node):
        trans_count = 0
        while trans_count <= node.retransmission:
            trans_count += 1
            if node.suc_tran_prob < np.random.random():
                node.send_energy(node.DM, Tool.calcu_distance(node, neighbor))  # 消耗发送数据包的能量
                # print("ID:", node.node_id, "To:", neighbor.node_id, "Miss ", trans_count)
                if trans_count > node.retransmission:  # 记录丢失数据包数，进行下一个源节点的数据传输
                    node.storage.remove(self.package_id)
                    self.miss_package += 1
                    # print("ID:", node.node_id, "To:", neighbor.node_id, "Miss!")
                    return -1
            else:
                # print("ID:", neighbor.node_id, "Storage:", neighbor.storage)
                node.send_energy_suc(node.DM, Tool.calcu_distance(node, neighbor), neighbor, self.package_id)  # 发送数据包
                # print("ID:", neighbor.node_id, "Storage:", neighbor.storage)
                neighbor.receive_energy(neighbor.DM)  # 邻居接收数据包
                if node != source_node:
                    self.send_suc_ack_to_pre(node)
                break
        # print("ID:", node.node_id, "To:", neighbor.node_id, "Success!")
        return 1

    def send_suc_ack_to_pre(self, node):
        self.nodes[node.pre_node].storage.remove(self.package_id)

    def transmission_source_node(self, rounds, source_node):
        nodes_map = self.nodes_map
        nodes_map[self.sink.node_id] = self.sink
        for train_round in range(rounds):
            survivor = 0
            for node in nodes_map.values():  # 统计存活节点
                if node.energy > 0:
                    survivor += 1
            self.survivor_count = survivor
            node = source_node
            while node.node_type != 'Sink':
                node_id = node.choose_action()  # 选择下一个动作
                if node_id == -2:  # 无邻居节点，放弃传输，丢弃包
                    break
                # print(node_id)
                neighbor = nodes_map[str(node_id)]
                # show_route_line(node, neighbor, self.nodes_map)
                node.send_energy(node.DM, Tool.calcu_distance(node, neighbor))  # 发送数据包
                neighbor.receive_energy(neighbor.DM)  # 邻居接收数据包
                node = neighbor
            print("\repisode of transmission:{}".format(train_round), end='')
            # print("\repisode of transmission:{}".format(train_round))
            self.update_all_node_energy()

    def update_survivor_node(self, nodes_map):
        survivor = 0  # 减去一个Sink节点个数
        for node in self.nodes_map.values():  # 统计存活节点
            if node.energy > 0:
                survivor += 1
        self.survivor_count = survivor

    def update_all_node_energy(self):
        self.all_node_energy_list.append(self.get_all_node_energy())

    def get_all_node_energy(self):
        nodes_map = self.nodes_map
        energy = 0
        for node in nodes_map.values():
            if node != self.sink:
                energy += node.energy
        print("   ", energy)
        return energy

