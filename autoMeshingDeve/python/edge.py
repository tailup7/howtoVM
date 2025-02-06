import numpy as np

class EdgeCenterline:
    def __init__(self,node_centerline0,node_centerline1):
        self.id = node_centerline0.id
        self.x_s= node_centerline0.x
        self.y_s= node_centerline0.y
        self.z_s= node_centerline0.z
        self.x_e= node_centerline1.x
        self.y_e= node_centerline1.y
        self.z_e= node_centerline1.z
