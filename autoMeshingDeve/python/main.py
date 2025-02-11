import mygmsh
import node 
import myio
import utility
import os

# parameter for tetraprism
N=4     # num of layers
r=1.4   # growth rate of layer's thickness
h=0.12  # first layer thickness

# parameter for background mesh
meshsize = 0.5 
scaling_factor = 0.2

# parameter for boundarylater
first_layer_ratio = 0.015 # % of diameter
growth_rate = 1.2
num_of_layers = 6

# input file
filepath_stl = os.path.join("input", "WALL.stl")
filepath_centerline = os.path.join("input", "centerline.txt")
filepath_edgeradii = os.path.join("input", "radius.txt")  # TODO : radius.txtを読み込むのではなく、入力されたSTLと中心線から計算するように変更

# backgroundmeshを作成
nodeids, coords = mygmsh.generate_bgm(meshsize,filepath_stl)

# スカラー値(半径)を backgroundmesh にセットし、bgm.posとして出力
nodes_centerline = node.NodesCenterline()
myio.read_txt_centerline(nodes_centerline,filepath_centerline)
nodes_any = node.NodesAny()
utility.coords_to_nodes(nodeids,coords,nodes_any)
edgeradii = myio.read_txt_edgeradii(filepath_edgeradii)   
nodeany_dict={}
for node_any in nodes_any.nodes_any:
    nodeany_dict[node_any.id] = node_any  
    node_any.find_closest_centerlinenode(nodes_centerline.nodes_centerline)
    node_any.find_projectable_centerlineedge(nodes_centerline.nodes_centerline)
    node_any.set_edgeradius(edgeradii)
    node_any.set_scalar_forbgm(edgeradii,scaling_factor)
tetra_list = myio.read_msh_tetra()
myio.write_pos_bgm(tetra_list,nodeany_dict)

# bgm.posを参照し、メッシュサイズが非一様なテトラ・プリズムメッシュを生成
mygmsh.tetraprism_mutable(filepath_stl,N,r,h)

# bgm.posを参照し、表面メッシュが非一様なstlをVTK形式で出力
mygmsh.surfacemesh(filepath_stl)