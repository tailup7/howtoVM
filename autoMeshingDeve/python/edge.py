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

    @staticmethod
    def judge_nodeany_correspondtoedge(node_any,node_centerline0,node_centerline1):
        vector_to_nodeany=np.array(node_any.x-node_centerline0.x, node_any.y-node_centerline0.y, node_any.z-node_centerline1.z)
        vector_edge = np.array(node_centerline1.x-node_centerline0.x, node_centerline1.y-node_centerline0.y, node_centerline1.z-node_centerline0.z)
        vector_edge_square = np.dot(vector_edge,vector_edge)
        projection = np.dot(vector_to_nodeany,vector_edge) / vector_edge_square
        if projection < 0 or 1 < projection:
            return False
        else:
            return True