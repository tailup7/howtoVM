import node
import sys

class PostProcessGmsh:
    @staticmethod
    def coords_to_nodes(coords, nodes_any):
        if len(coords)%3!=0:
            print("mylib_info   : error. 座標成分の総数が3の倍数になりません")
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


    
