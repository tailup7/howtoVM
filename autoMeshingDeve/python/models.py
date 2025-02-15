from dataclasses import dataclass,field
import config
import node
import cell
import utility

@dataclass
class Mesh:
    num_of_nodes:int = 0
    nodes:list = field(default_factory=list)
    num_of_elements:int = 0
    triangles_WALL:list = field(default_factory=list)
    triangles_INLET:list = field(default_factory=list)
    triangles_OUTLET:list = field(default_factory=list)
    quadrangles_INLET:list = field(default_factory=list)
    quadrangles_OUTLET:list = field(default_factory=list)
    tetras_INTERNAL:list = field(default_factory=list)
    prisms_INTERNAL:list = field(default_factory=list)

    triangles_INNERWALL:list = field(default_factory=list)
    nodes_innersurface:list = field(default_factory=list)


def make_nth_layer(surfacetriangles,surfacenode_dict, nodes_on_inletboundaryedge,nodes_on_outletboundaryedge,nth,thickratio,mesh):
    temp = set()
    nth_layer_surfacenode_dict={}
    first_id=float("inf")
    last_id=0
    for surfacetriangle in surfacetriangles.triangles:
        nodes = [surfacetriangle.node0, surfacetriangle.node1, surfacetriangle.node2]
        for onenode in nodes:
            if first_id > onenode.id:
                first_id = onenode.id
            if last_id < onenode.id:
                last_id = onenode.id

            if onenode.id in temp:
                nth_layer_surfacenode_dict[onenode.id].x += surfacetriangle.unitnormal_in[0]*thickratio*onenode.scalar_forlayer
                nth_layer_surfacenode_dict[onenode.id].y += surfacetriangle.unitnormal_in[1]*thickratio*onenode.scalar_forlayer
                nth_layer_surfacenode_dict[onenode.id].z += surfacetriangle.unitnormal_in[2]*thickratio*onenode.scalar_forlayer
                nth_layer_surfacenode_dict[onenode.id].sumcountor += 1
            else:
                x =  surfacetriangle.unitnormal_in[0]*thickratio*onenode.scalar_forlayer
                y =  surfacetriangle.unitnormal_in[1]*thickratio*onenode.scalar_forlayer
                z =  surfacetriangle.unitnormal_in[2]*thickratio*onenode.scalar_forlayer
                nth_layer_surfacenode = node.NodeAny(onenode.id + config.num_of_surfacenodes, x, y, z)
                nth_layer_surfacenode_dict[onenode.id] = nth_layer_surfacenode
                temp.add(onenode.id)

    nth_layer_surfacenodes=[]
    for i in range(first_id, last_id+1): ### ここ変えた
        nth_layer_surfacenode_dict[i].x = surfacenode_dict[i].x + nth_layer_surfacenode_dict[i].x/nth_layer_surfacenode_dict[i].sumcountor
        nth_layer_surfacenode_dict[i].y = surfacenode_dict[i].y + nth_layer_surfacenode_dict[i].y/nth_layer_surfacenode_dict[i].sumcountor
        nth_layer_surfacenode_dict[i].z = surfacenode_dict[i].z + nth_layer_surfacenode_dict[i].z/nth_layer_surfacenode_dict[i].sumcountor
        nth_layer_surfacenodes.append(nth_layer_surfacenode_dict[i])
        mesh.nodes.append(nth_layer_surfacenode_dict[i])
        mesh.num_of_nodes += 1
    nth_layer_surfacenode_sorted = sorted(nth_layer_surfacenodes, key=lambda obj: obj.id)   ## 今のところ使っていない

    #######
    sorted_points, right_neighbors = utility.find_right_neighbors_3d(nodes_on_inletboundaryedge, config.reference_point)
    for i in range(len(sorted_points)):
        quad_id0=sorted_points[i].id
        quad_id1=right_neighbors[i].id
        quad_id2=right_neighbors[i].id + config.num_of_surfacenodes
        quad_id3=sorted_points[i].id + config.num_of_surfacenodes
        quad = cell.Quad(quad_id0,quad_id1,quad_id2,quad_id3)
        mesh.quadrangles_INLET.append(quad)
        mesh.num_of_elements+=1

    sorted_points, right_neighbors = utility.find_right_neighbors_3d(nodes_on_outletboundaryedge, config.reference_point)
    for i in range(len(sorted_points)):
        quad_id0=sorted_points[i].id
        quad_id1=right_neighbors[i].id
        quad_id2=right_neighbors[i].id + config.num_of_surfacenodes
        quad_id3=sorted_points[i].id + config.num_of_surfacenodes
        quad = cell.Quad(quad_id0,quad_id1,quad_id2,quad_id3)
        mesh.quadrangles_OUTLET.append(quad)
        mesh.num_of_elements+=1

    nth_layer_prisms=[]
    mostinnersurfacetriangle_dict={}   ##不要...?
    for surfacetriangle in surfacetriangles.triangles:
        prism_id0=surfacetriangle.node0.id + config.num_of_surfacenodes
        prism_id1=surfacetriangle.node1.id + config.num_of_surfacenodes
        prism_id2=surfacetriangle.node2.id + config.num_of_surfacenodes
        prism_id3=surfacetriangle.node0.id
        prism_id4=surfacetriangle.node1.id
        prism_id5=surfacetriangle.node2.id
        nth_layer_prism = cell.Prism(prism_id0,prism_id1,prism_id2,prism_id3,prism_id4,prism_id5)
        mesh.prisms_INTERNAL.append(nth_layer_prism)
        mesh.num_of_elements+=1


