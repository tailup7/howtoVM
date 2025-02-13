import node
import cell
import config
import sys
import os

def read_txt_centerline(filepath):
    if not os.path.isfile(filepath):
            print(f"Error: '{filepath}' does not exist.")
            sys.exit()
    with open(filepath, 'r') as file:
        lines = file.readlines()
    valid_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    nodes_centerline = node.NodesCenterline()
    node_centerline_dict={}
    index = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'): 
            parts = line.split() 
            x, y, z = float(parts[0]), float(parts[1]), float(parts[2]) 
            node_centerline = node.NodeCenterline(index, x, y, z)
            node_centerline_dict[index] = node_centerline
            nodes_centerline.append(node_centerline)
            if index == 0:
                inlet_point = node_centerline
                config.inlet_point=inlet_point
            elif index == len(valid_lines)-1:
                outlet_point = node_centerline
                config.outlet_point=outlet_point
            index += 1
    print(f"info_myio   : centerline nodes count is {len(nodes_centerline.nodes_centerline)}")
    print("info_myio    : please ignore. centerline_node_sample =  ",nodes_centerline.nodes_centerline[6])
    print("info_myio    : inlet_point is", config.inlet_point)
    print("info_myio    : outlet_point is", config.outlet_point)
    return nodes_centerline, node_centerline_dict


def read_txt_edgeradii(filepath):
    if not os.path.isfile(filepath):
            print(f"Error: '{filepath}' does not exist.")
            sys.exit()
    edgeradii = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            edgeradii.append(float(line))
    config.inlet_radius = edgeradii[0]
    config.outlet_radius = edgeradii[-1]
    print(f"info_myio    : num of edges is {len(edgeradii)}")
    return edgeradii

def read_msh_tetra():
    filepath = os.path.join("output", "bgm.msh")
    if not os.path.isfile(filepath):
        print(f"Error: '{filepath}' does not exist.")
        sys.exit()
    tetra_list = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 9 and columns[1] == '4':
                tetra = [int(columns[i]) for i in range(5, 9)]
                tetra_list.append(tetra)
    print("info_myio    : num of tetra is",len(tetra_list))
    return tetra_list

def write_pos_bgm(tetra_list,nodeany_dict):
    filepath = os.path.join("output", "bgm.pos")
    with open(filepath, 'w') as f:
        f.write('View "background mesh" {\n')
        coords_list=[]
        scalars_list=[]
        for tetra in tetra_list:
            coords=[]
            scalars=[]
            for i in range(len(tetra)):
                coords.append(nodeany_dict[tetra[i]].x)
                coords.append(nodeany_dict[tetra[i]].y)
                coords.append(nodeany_dict[tetra[i]].z)
                scalars.append(nodeany_dict[tetra[i]].scalar_forbgm)
            coords_list.append(coords)
            scalars_list.append(scalars)
        for i in range(len(tetra_list)):
            c = coords_list[i]
            s = scalars_list[i]
            f.write(f"SS({c[0]},{c[1]},{c[2]},{c[3]},{c[4]},{c[5]},{c[6]},{c[7]},{c[8]},{c[9]},{c[10]},{c[11]})"
                    f"{{{s[0]:.2f},{s[1]:.2f},{s[2]:.2f},{s[3]:.2f}}};\n")
        f.write('};')

def read_vtk_outersurface(filepath_vtk):
    with open(filepath_vtk, 'r') as file:
        lines = file.readlines()
    points_section = False
    cells_section = False
    for line in lines:
        line = line.strip()
        if line.startswith("POINTS"):
            points_section = True
            node_id=0
            surfacenode_dict = {}
            surfacenodes = node.NodesAny() 
            continue
        if line.startswith("CELLS"):
            points_section = False
            cells_section = True
            triangle_id=0
            surfacetriangle_dict={}
            surfacetriangles = cell.Triangles()
            continue
        if points_section:
            if not line:
                points_section = False
                continue
            coords = list(map(float, line.split()))
            x=coords[0]
            y=coords[1]
            z=coords[2]
            surfacenode=node.NodeAny(node_id,x,y,z)
            surfacenode_dict[node_id]= surfacenode
            surfacenodes.append(surfacenode)
            node_id+=1
        if cells_section:
            if not line:
                cells_section = False
                continue
            cell_data = list(map(int, line.split()))
            if cell_data[0] == 3:
                node0 = surfacenode_dict[cell_data[1]]
                node1 = surfacenode_dict[cell_data[2]]
                node2 = surfacenode_dict[cell_data[3]]
                surfacetriangle = cell.Triangle(triangle_id, node0, node1, node2)
                surfacetriangle_dict[triangle_id] = surfacetriangle
                surfacetriangles.append(surfacetriangle)
                triangle_id += 1
    print("info_myio    : num of outersurface points is ",node_id)
    print("info_myio    : num of outersurface triangles is ",triangle_id)
    config.num_of_surfacenodes=node_id
    return surfacenodes,surfacetriangles

def write_stl_mostinnersurface(triangle_list):
    filepath=os.path.join("output","mostinnersurface.stl")
    with open(filepath, 'w') as f:
        f.write("solid model\n")
        for triangle in triangle_list:
            f.write(f"  facet normal {triangle.unitnormal_out[0]} {triangle.unitnormal_out[1]} {triangle.unitnormal_out[2]}\n")
            f.write("    outer loop\n")
            f.write(f"      vertex {triangle.node0.x} {triangle.node0.y} {triangle.node0.z}\n")
            f.write(f"      vertex {triangle.node1.x} {triangle.node1.y} {triangle.node1.z}\n")
            f.write(f"      vertex {triangle.node2.x} {triangle.node2.y} {triangle.node2.z}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        f.write("endsolid model\n")
    return filepath

def read_msh_innermesh(filepath):

    nodes_innermesh = []
    triangles_innerwall=[]
    triangles_inlet=[]
    triangles_outlet=[]
    node_innermesh_dict={}
    triangle_innerwall_dict={}  
    triangle_inlet_dict={}   ###### 不要かも
    triangle_outlet_dict={}  ######

    with open(filepath, "r") as file:
        lines = file.readlines()

    node_section = False
    skip_next_line = False  
    element_section = False

    for i, line in enumerate(lines):
        line = line.strip()

        if line.startswith("$Nodes"):
            node_section = True
            skip_next_line = True 
            continue

        if skip_next_line:
            skip_next_line = False  
            continue

        if line.startswith("$EndNodes"):
            node_section = False
            continue

        if node_section:
            parts = line.split()
            if len(parts) < 4:
                continue  
            
            node_id = int(parts[0])
            x, y, z = map(float, parts[1:4])
            node_innermesh = node.NodeAny(node_id, x, y, z)
            node_innermesh_dict[node_id]=node_innermesh
            nodes_innermesh.append(node_innermesh)

        if line.startswith("$Elements"):
            element_section = True
            skip_next_line = True  
            continue
        if skip_next_line:
            skip_next_line = False
            continue
        if line.startswith("$EndElements"):
            element_section = False
            continue

        if element_section:
            parts = line.split()
            if len(parts) < 5:
                continue 

            elem_id = int(parts[0])  # 要素ID
            elem_type = int(parts[1])  # 要素のタイプ
            physical_group = int(parts[3])  # 物理グループ（4列目）

            nodesid_composing_innerwalltriangle=set()
            nodesid_composing_inlettriangle=set()
            nodesid_composing_outlettriangle=set()

            if  elem_type == 2: 
                node0 = node_innermesh_dict[int(parts[-3])]
                node1 = node_innermesh_dict[int(parts[-2])]
                node2 = node_innermesh_dict[int(parts[-1])]

                if physical_group == 99 :
                    triangle_innerwall = cell.Triangle(elem_id, node0, node1, node2)
                    triangle_innerwall_dict[elem_id] = triangle_innerwall
                    triangles_innerwall.append(triangle_innerwall)
                    nodesid_composing_innerwalltriangle.update(map(int, parts[-3:]))

                elif physical_group == 20:
                    triangle_inlet = cell.Triangle(elem_id, node0, node1, node2)
                    triangle_inlet_dict[elem_id] = triangle_inlet
                    triangles_inlet.append(triangle_inlet)     ####################### 不要かも
                    nodesid_composing_inlettriangle.update(map(int, parts[-3:])) ##########

                elif physical_group == 30:
                    triangle_outlet = cell.Triangle(elem_id, node0, node1, node2)
                    triangle_outlet_dict[elem_id] = triangle_outlet
                    triangles_outlet.append(triangle_outlet)           ###############
                    nodesid_composing_outlettriangle.update(map(int, parts[-3:])) #########
        
    # 99(innerwall)と20or30(端面)を構成するNodeはboundaryNodeとして抽出する
    nodesid_on_inlet_boundaryedge = nodesid_composing_innerwalltriangle & nodesid_composing_inlettriangle
    nodesid_on_outlet_boundaryedge= nodesid_composing_innerwalltriangle & nodesid_composing_outlettriangle
    for nodeid in nodesid_on_inlet_boundaryedge:
        node_innermesh_dict[nodeid].on_boundaryedge = True
    for nodeid in nodesid_on_outlet_boundaryedge:
        node_innermesh_dict[nodeid].on_boundaryedge = True

    return nodes_innermesh, node_innermesh_dict, triangles_innerwall, triangle_innerwall_dict