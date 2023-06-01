import numpy as np
import pandas as pd
from configparser import ConfigParser
from Node import Node


class Sink(Node):
    def __init__(self, node_id, node_x, node_y, node_z):
        super(Sink, self).__init__(node_id=node_id, node_x=node_x, node_y=node_y, node_z=node_z)
        config = ConfigParser()
        config.read("enviro.ini", encoding="utf-8")
        self.com_range = config["node"].getint("com_range")  # 传输半径
        self.energy = 5  # 节点剩余能量
        self.e_ini = 5  # 初始能量
        self.reward = 0
        self.node_type = "Sink"
        self.layer_ave_energy_list = np.zeros(6)
