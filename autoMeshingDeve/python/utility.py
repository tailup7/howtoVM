import node
import sys
import numpy as np
import gmsh

def can_P_project_to_AB(P,A,B):

#             projectable !                       Not projectable...
#
#                  P                                                     P
#                  |                                                     |
#                  |                                                     |
#                  |                                                     |  
#      A---------- H -----B                A------------------B          H
#       \     t    /                         \                          /
#                                                          t
    vector_AP = np.array([P.x-A.x,  P.y-A.y,  P.z-A.z])
    vector_AB = np.array([B.x-A.x,  B.y-A.y,  B.z-A.z])
    vector_AB_square = np.dot(vector_AB, vector_AB)
    t = np.dot(vector_AP,vector_AB) / vector_AB_square
    if 0 <= t and t <= 1:
        return True

def calculate_PH_length(P,A,B):
    vector_AP = np.array([P.x-A.x,  P.y-A.y,  P.z-A.z])
    vector_AB = np.array([B.x-A.x,  B.y-A.y,  B.z-A.z])
    vector_AB_square = np.dot(vector_AB, vector_AB)
    t = np.dot(vector_AP,vector_AB) / vector_AB_square
    vector_AH = t*vector_AB
    vector_PH = vector_AH - vector_AP
    return(np.linalg.norm(vector_PH))

# gmsh.model.mesh.getNodes() の1つめの返り値は、得られた全Nodeのid のリスト。
# 2つめの返り値は、得られる全Nodeのx,y,z座標成分をまとめたリスト。これらをnodeごとの情報に整理する
def coords_to_nodes(nodeids, coords, nodes_any):
    if len(coords)%3!=0:
        print("mylib_info   : coords_to_nodes error.")
        sys.exit()
    else:
        for i in range(len(nodeids)):
            x = coords[3*i]
            y = coords[3*i+1]
            z = coords[3*i+2]
            id = nodeids[i]
            node_any = node.NodeAny(id,x,y,z)
            nodes_any.append(node_any)
    print(f"info_utility   : node count after postprocess gmsh is {len(nodes_any.nodes_any)}")

def gmsh_gui_setting():
    # 1がON/0がOFF
    # 2次元メッシュの可視化ON/OFF
    gmsh.option.setNumber("Mesh.SurfaceFaces", 1)
    
    gmsh.option.setNumber("Mesh.Lines", 1)
    # 0次元のEntityの可視化ON?OFF
    gmsh.option.setNumber("Geometry.PointLabels", 1)
    # メッシュの線の太さを指定
    gmsh.option.setNumber("Mesh.LineWidth", 4)
    # gmshではマウスのホイールのズーンオン/ズームオフがparaviewとは逆なので、paraviewと一緒にする
    gmsh.option.setNumber("General.MouseInvertZoom", 1)
    # モデルのサイズが簡単に確認できるように、モデルを囲む直方体メモリを表示
    gmsh.option.setNumber("General.Axes", 3)
    
    gmsh.option.setNumber("General.Trackball", 0)
    # GUIが表示された時の、目線の方向を(0,0,0)に指定
    gmsh.option.setNumber("General.RotationX", 0)
    gmsh.option.setNumber("General.RotationY", 0)
    gmsh.option.setNumber("General.RotationZ", 0)
    # gmshのターミナルに情報を表示
    gmsh.option.setNumber("General.Terminal", 1)
