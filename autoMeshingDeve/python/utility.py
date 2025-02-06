import node
import sys
import numpy as np

def can_P_project_to_AB(P,A,B):

#             OK !                                        NO...
#
#                  P                                                     P
#                  |                                                     |
#                  |                                                     |
#                  |                                                     |  
#      A---------- H -----B                A------------------B          H
#       \     t    /                         \                          /
#                                                          t
    vector_AP = np.array(P.x-A.x,  P.y-A.y,  P.z-A.z)
    vector_AB = np.array(B.x-A.x,  B.y-A.y,  B.z-A.z)
    vector_AB_square = np.dot(vector_AB, vector_AB)
    t = np.dot(vector_AP,vector_AB) / vector_AB_square
    if 0 <= t and t <= 1:
        return True

def calculate_PH_length(P,A,B):
    vector_AP = np.array(P.x-A.x,  P.y-A.y,  P.z-A.z)
    vector_AB = np.array(B.x-A.x,  B.y-A.y,  B.z-A.z)
    vector_AB_square = np.dot(vector_AB, vector_AB)
    t = np.dot(vector_AP,vector_AB) / vector_AB_square
    vector_AH = t*vector_AB
    vector_PH = vector_AH - vector_AP
    return(np.linalg.norm(vector_PH))


# gmsh.model.mesh.getNodes() で得られる全Nodeのx,y,z座標成分はまとめて1つのリストになっているので、nodeごとにリストに分割する
def coords_to_nodes(coords, nodes_any):
    if len(coords)%3!=0:
        print("mylib_info   : coords_to_nodes error.")
        sys.exit()
    else:
        for i in range(len(coords)):
            if i%3==0:
                x = coords[i]
            elif i%3==1:
                y = coords[i]
            else:
                z = coords[i]
                node_any = node.NodeAny((i+1)//3-1,x,y,z)
                nodes_any.append(node_any)
    print(f"info_utility   : node count after postprocess gmsh is {len(nodes_any.nodes_any)}")


