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
    return surfacenodes,surfacetriangles