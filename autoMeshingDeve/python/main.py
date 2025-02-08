import mygmsh
import node 
import myio
import utility

# backgroundmeshを作成
meshsize = 0.5 
filepath_forbgm = "newdata/WALL.stl"
nodeids, coords = mygmsh.generate_bgm(meshsize,filepath_forbgm)

# スカラー値(半径)を backgroundmesh にセットし、bgm.posとして出力
nodes_centerline = node.NodesCenterline()
myio.read_txt_centerline(nodes_centerline)
nodes_any = node.NodesAny()
utility.coords_to_nodes(nodeids,coords,nodes_any)
edgeradii = myio.read_txt_edgeradii()    # TODO : radius.txtを読み込むのではなく、入力されたSTLと中心線から計算するように変更
nodeany_dict={}
for node_any in nodes_any.nodes_any:
    nodeany_dict[node_any.id] = node_any  
    node_any.find_closest_centerlinenode(nodes_centerline.nodes_centerline)
    node_any.find_projectable_centerlineedge(nodes_centerline.nodes_centerline)
    node_any.set_edgeradius(edgeradii)
    node_any.set_scalar_forbgm(edgeradii)
tetra_list = myio.read_msh_tetra()
myio.write_pos_bgm(tetra_list,nodeany_dict)

# bgm.posを参照し、メッシュサイズが非一様なテトラ・プリズムメッシュを生成
filepath_true = "newdata/cut/WALL_this.stl"
mygmsh.tetraprism_mutable(filepath_true)