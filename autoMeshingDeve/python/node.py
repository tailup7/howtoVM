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

    def __str__(self):
        return f"NodeAny(id={self.id}, x={self.x}, y={self.y}, z={self.z})"
    
    def append_correspondcenterlinenodeid(self,nodes_centerline):
        min_distance_square = float("inf")
        for node_centerline in nodes_centerline:
            distance_square = (self.x-node_centerline.x)**2 + (self.y-node_centerline.y)**2 + (self.z-node_centerline.z)**2
            if distance_square < min_distance_square:
                min_distance_square = distance_square
                self.correspond_centerlinenode_id = node_centerline.id
        # self.correspondcenterlineid = correspondcenterlineid
    
    def append_correspondcenterlineedgeid(self,nodes_centerline):
        aaa=1

class NodesAny:
    def __init__(self):
        self.nodes_any=[]
    def append(self,node_any):
        self.nodes_any.append(node_any)