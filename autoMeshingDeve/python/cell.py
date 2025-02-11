import numpy as np

class Triangle:
    def __init__(self,id,node0,node1,node2):
        self.id=id
        self.node0=node0
        self.node1=node1
        self.node2=node2

    def calc_unitnormal(self, node_centerline_dict):
        vector0=np.array([self.node1.x-self.node0.x, self.node1.y-self.node0.y, self.node1.z-self.node0.z])
        vector1=np.array([self.node2.x-self.node0.x, self.node2.y-self.node0.y, self.node2.z-self.node0.z])
        normal = np.cross(vector0,vector1)
        n0 = np.array([self.node0.x,self.node0.y,self.node0.z])
        nc = np.array([ node_centerline_dict[self.node0.closest_centerlinenode_id].x,
                        node_centerline_dict[self.node0.closest_centerlinenode_id].y,
                        node_centerline_dict[self.node0.closest_centerlinenode_id].z ])
        vec_in = nc-n0
        if np.dot(vec_in,normal)<0:
            self.unitnormal_out = normal/np.linalg.norm(normal)
            self.unitnormal_in = -self.unitnormal_out
        else:
            self.unitnormal_in = normal/np.linalg.norm(normal)
            self.unitnormal_out = - self.unitnormal_in

class Triangles:
    def __init__(self):
        self.triangles=[]
    def append(self,triangle):
        self.triangles.append(triangle)
