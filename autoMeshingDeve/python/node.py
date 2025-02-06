import utility

class NodeCenterline:
    def __init__(self,id,x,y,z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"NodeAny(id={self.id}, x={self.x}, y={self.y}, z={self.z})"

class NodesCenterline:
    def __init__(self):
        self.nodes_centerline=[]

    def append(self,node_centerline):
        self.nodes_centerline.append(node_centerline)

class NodeAny:
    def __init__(self,id,x,y,z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.closest_centerlinenode_id = None
        self.projectable_centerlineedge_id = None
        self.edgeradius = None
        self.scalar_forbgm = None

    def __str__(self):
        return f"NodeAny(id={self.id}, x={self.x}, y={self.y}, z={self.z})"
    
    def find_closest_centerlinenode(self,nodes_centerline):
        min_distance_square = float("inf")
        for node_centerline in nodes_centerline:
            distance_square = (self.x-node_centerline.x)**2 + (self.y-node_centerline.y)**2 + (self.z-node_centerline.z)**2
            if distance_square < min_distance_square:
                min_distance_square = distance_square
                self.closest_centerlinenode_id = node_centerline.id
    
    def find_projectable_centerlineedge(self,nodes_centerline):
        ccid = self.closest_centerlinenode_id
        if ccid==0:
            if utility.can_P_project_to_AB(self,nodes_centerline[0],nodes_centerline[1]) == True:
                self.projectable_centerlineedge_id = 0
        elif ccid == len(nodes_centerline)-1:
            if utility.can_P_project_to_AB(self,nodes_centerline[-2],nodes_centerline[-1]) == True:
                self.projectable_centerlineedge_id = nodes_centerline[-2].id
        else:
            distance_temp = float("inf")
            if utility.can_P_project_to_AB(self,nodes_centerline[ccid-1],nodes_centerline[ccid]) == True:
                distance_temp = utility.calculate_PH_length(self, nodes_centerline[ccid-1], nodes_centerline[ccid])
                self.projectable_centerlineedge_id = ccid-1
            if utility.can_P_project_to_AB(self,nodes_centerline[ccid],nodes_centerline[ccid+1]) == True:
                if utility.calculate_PH_length(self, nodes_centerline[ccid], nodes_centerline[ccid+1]) < distance_temp:
                    self.projectable_centerlineedge_id = ccid

    def set_edgeradius(self,edgeradii):
        if self.projectable_centerlineedge_id != None:
            self.edgeradius = edgeradii[self.projectable_centerlineedge_id+1]

    def set_scalar_forbgm(self,edgeradii):
        if self.edgeradius != None:
            self.scalar_forbgm = self.edgeradius
        else:
            average_edgeradius = (edgeradii[self.closest_centerlinenode_id] + edgeradii[self.closest_centerlinenode_id+1])/2
            self.scalar_forbgm = average_edgeradius

class NodesAny:
    def __init__(self):
        self.nodes_any=[]
    def append(self,node_any):
        self.nodes_any.append(node_any)