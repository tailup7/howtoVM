# https://gmsh.info/doc/texinfo/gmsh.html

#        @staticmethod
#        def extrudeBoundaryLayer(dimTags, numElements=[1], heights=[], recombine=False, second=False, viewIndex=-1):
#            """
#            gmsh.model.geo.extrudeBoundaryLayer(dimTags, numElements=[1], heights=[], recombine=False, second=False, viewIndex=-1)
#
#            Extrude the entities `dimTags' (given as a vector of (dim, tag) pairs) in
#            the built-in CAD representation along the normals of the mesh, creating
#            discrete boundary layer entities. Return extruded entities in `outDimTags'.
#            The entries in `numElements' give the number of elements in each layer. If
#            the `height' vector is not empty, it provides the (cumulative) height of
#            the different layers. If `recombine' is set, recombine the mesh in the
#            layers. A second boundary layer can be created from the same entities if
#            `second' is set. If `viewIndex' is >= 0, use the corresponding view to
#            either specify the normals (if the view contains a vector field) or scale
#            the normals (if the view is scalar).
#
#            Return `outDimTags'.
#
#            Types:
#            - `dimTags': vector of pairs of integers
#            - `outDimTags': vector of pairs of integers
#            - `numElements': vector of integers
#            - `heights': vector of doubles
#            - `recombine': boolean
#            - `second': boolean
#            - `viewIndex': integer
#            """
#            api_dimTags_, api_dimTags_n_ = _ivectorpair(dimTags)
#            api_outDimTags_, api_outDimTags_n_ = POINTER(c_int)(), c_size_t()
#            api_numElements_, api_numElements_n_ = _ivectorint(numElements)
#            api_heights_, api_heights_n_ = _ivectordouble(heights)
#            ierr = c_int()
#            lib.gmshModelGeoExtrudeBoundaryLayer(
#                api_dimTags_, api_dimTags_n_,
#                byref(api_outDimTags_), byref(api_outDimTags_n_),
#                api_numElements_, api_numElements_n_,
#                api_heights_, api_heights_n_,
#                c_int(bool(recombine)),
#                c_int(bool(second)),
#                c_int(viewIndex),
#                byref(ierr))
#            if ierr.value != 0:
#                raise Exception(logger.getLastError())
#            return _ovectorpair(api_outDimTags_, api_outDimTags_n_.value)
#        extrude_boundary_layer = extrudeBoundaryLayer

import gmsh
import sys
import math
import numpy as np

gmsh.initialize(sys.argv)
gmsh.model.add("Tube boundary layer")

# meshing constraints
gmsh.option.setNumber("Mesh.MeshSizeMax", 0.1)
order2 = False

# fuse 2 cylinders and only keep outside shell
c1 = gmsh.model.occ.addCylinder(0,0,0, 5,0,0, 0.5)
c2 = gmsh.model.occ.addCylinder(2,0,-2, 0,0,2, 0.3)
s = gmsh.model.occ.fuse([(3, c1)], [(3, c2)])
gmsh.model.occ.remove(gmsh.model.occ.getEntities(3))
gmsh.model.occ.remove([(2,2), (2,3), (2,5)]) # fixme: automate this
gmsh.model.occ.synchronize()

# create boundary layer extrusion, and make extrusion only return "top" surfaces
# and volumes, not lateral surfaces
gmsh.option.setNumber('Geometry.ExtrudeReturnLateralEntities', 0)
n = np.linspace(1, 1, 5)
d = np.logspace(-3, -1, 5)
e = gmsh.model.geo.extrudeBoundaryLayer(gmsh.model.getEntities(2), n, -d, True)

# get "top" surfaces created by extrusion
top_ent = [s for s in e if s[0] == 2]
top_surf = [s[1] for s in top_ent]

# get boundary of top surfaces, i.e. boundaries of holes
gmsh.model.geo.synchronize()
bnd_ent = gmsh.model.getBoundary(top_ent)
bnd_curv = [c[1] for c in bnd_ent]

# create plane surfaces filling the holes
loops = gmsh.model.geo.addCurveLoops(bnd_curv)
for l in loops:
    top_surf.append(gmsh.model.geo.addPlaneSurface([l]))

# create the inner volume
gmsh.model.geo.addVolume([gmsh.model.geo.addSurfaceLoop(top_surf)])
gmsh.model.geo.synchronize()

# generate the mesh
gmsh.model.mesh.generate(3)

# 2nd order + fast curving of the boundary layer
if order2:
    gmsh.model.mesh.setOrder(2)
    gmsh.model.mesh.optimize('HighOrderFastCurving')

gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write("test.msh")
gmsh.write("test.vtk")

if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
