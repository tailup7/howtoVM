import mygmsh
import node 
import cell
import myio
import config
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
nodes_centerline, node_centerline_dict = myio.read_txt_centerline(filepath_centerline)
nodes_any = node.NodesAny()
node.coords_to_nodes(nodeids,coords,nodes_any)
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
filepath_vtk = mygmsh.surfacemesh(filepath_stl)
surfacenodes,surfacetriangles = myio.read_vtk_outersurface(filepath_vtk)
surfacenode_dict={}
for surfacenode in surfacenodes.nodes_any:
    surfacenode.find_closest_centerlinenode(nodes_centerline.nodes_centerline)
    surfacenode.find_projectable_centerlineedge(nodes_centerline.nodes_centerline)
    surfacenode.set_edgeradius(edgeradii)
    surfacenode.set_scalar_forlayer(edgeradii)
    surfacenode_dict[surfacenode.id] = surfacenode

# 一番内側の層を作る
num_of_nodes=0
temp = set()
mostinnersurfacenode_dict={}
for surfacetriangle in surfacetriangles.triangles:
    surfacetriangle.calc_unitnormal(node_centerline_dict)

    nodes = [surfacetriangle.node0, surfacetriangle.node1, surfacetriangle.node2]
    for onenode in nodes:
        if onenode.id in temp:
            mostinnersurfacenode_dict[onenode.id].x += surfacetriangle.unitnormal_in[0]*config.boundarylayer_ratio*onenode.scalar_forlayer
            mostinnersurfacenode_dict[onenode.id].y += surfacetriangle.unitnormal_in[1]*config.boundarylayer_ratio*onenode.scalar_forlayer
            mostinnersurfacenode_dict[onenode.id].z += surfacetriangle.unitnormal_in[2]*config.boundarylayer_ratio*onenode.scalar_forlayer
            mostinnersurfacenode_dict[onenode.id].sumcountor += 1
        else:
            x =  surfacetriangle.unitnormal_in[0]*config.boundarylayer_ratio*onenode.scalar_forlayer
            y =  surfacetriangle.unitnormal_in[1]*config.boundarylayer_ratio*onenode.scalar_forlayer
            z =  surfacetriangle.unitnormal_in[2]*config.boundarylayer_ratio*onenode.scalar_forlayer
            mostinnersurfacenode = node.NodeAny(onenode.id, x, y, z)
            mostinnersurfacenode_dict[onenode.id] = mostinnersurfacenode
            temp.add(onenode.id)
            num_of_nodes += 1
print("num of mostinnersurface nodes =",num_of_nodes)
mostinnersurfacenodes=[]
for i in range(num_of_nodes):
    mostinnersurfacenode_dict[i].x = surfacenode_dict[i].x + mostinnersurfacenode_dict[i].x/mostinnersurfacenode_dict[i].sumcountor
    mostinnersurfacenode_dict[i].y = surfacenode_dict[i].y + mostinnersurfacenode_dict[i].y/mostinnersurfacenode_dict[i].sumcountor
    mostinnersurfacenode_dict[i].z = surfacenode_dict[i].z + mostinnersurfacenode_dict[i].z/mostinnersurfacenode_dict[i].sumcountor
    mostinnersurfacenodes.append(mostinnersurfacenode_dict[i])
mostinnersurfacenode_sorted = sorted(mostinnersurfacenodes, key=lambda obj: obj.id)

mostinnersurfacetriangles=[]
mostinnersurfacetriangle_dict={}
for surfacetriangle in surfacetriangles.triangles:
    node0 = mostinnersurfacenode_dict[surfacetriangle.node0.id]
    node1 = mostinnersurfacenode_dict[surfacetriangle.node1.id]
    node2 = mostinnersurfacenode_dict[surfacetriangle.node2.id]
    node0.find_closest_centerlinenode(nodes_centerline.nodes_centerline)
    node1.find_closest_centerlinenode(nodes_centerline.nodes_centerline)
    node2.find_closest_centerlinenode(nodes_centerline.nodes_centerline)
    mostinnersurfacetriangle = cell.Triangle(surfacetriangle.id,node0,node1,node2)
    mostinnersurfacetriangle.calc_unitnormal(node_centerline_dict)
    mostinnersurfacetriangle_dict[surfacetriangle.id] = mostinnersurfacetriangle
    mostinnersurfacetriangles.append(mostinnersurfacetriangle)

print("info_main    :surfacetriangle unitnormal_out sample is",surfacetriangles.triangles[10].unitnormal_out)

myio.write_stl_mostinnersurface(mostinnersurfacetriangles)
