from maya import cmds
from maya import OpenMaya

def skin_constraint(mesh, transform, precision=2):
    '''
    skin_constraint('beltDetail_LOD1_geo', 'locator1')
    '''

    # clamp precision
    precision = max(precision, 1)

    # get barycentric coords
    point = cmds.xform(transform, q=True, t=True, ws=True)
    face_index, triangle_index, u, v = get_closest_polygon_on_mesh(point, mesh)

    # create weighted matrix node
    transforms, weights = get_triange_weights(mesh, face_index, triangle_index, u, v)
    matrix_node = create_weighted_matrix_node(transforms, weights, precision=precision)

    # multiply point-by-matrix
    vector_product_node1 = cmds.createNode('vectorProduct')
    cmds.setAttr('{}.operation'.format(vector_product_node1), 4)
    cmds.setAttr('{}.input1'.format(vector_product_node1), *point)
    cmds.connectAttr('{}.matrixSum'.format(matrix_node), '{}.matrix'.format(vector_product_node1))

    # make new-point relative (to its parent)
    vector_product_node2 = cmds.createNode('vectorProduct')
    cmds.setAttr('{}.operation'.format(vector_product_node2), 4)
    cmds.connectAttr('{}.output'.format(vector_product_node1), '{}.input1'.format(vector_product_node2))
    cmds.connectAttr('{}.parentInverseMatrix'.format(transform), '{}.matrix'.format(vector_product_node2))
    cmds.connectAttr('{}.output'.format(vector_product_node2), '{}.translate'.format(transform), force=True)

    # connect blended rotation
    decompose_matrix_node = cmds.createNode('decomposeMatrix')
    cmds.connectAttr('{}.matrixSum'.format(matrix_node), '{}.inputMatrix'.format(decompose_matrix_node))
    cmds.connectAttr('{}.outputRotate'.format(decompose_matrix_node), '{}.rotate'.format(transform), force=True)
    
def get_dagpath(node, extend_to_shape=False):
    '''
    '''

    selection_list = OpenMaya.MSelectionList()
    selection_list.add(node)

    dag_path = OpenMaya.MDagPath()
    selection_list.getDagPath(0, dag_path)

    if extend_to_shape:
        dag_path.extendToShape()

    return dag_path

def get_closest_polygon_on_mesh(point, mesh):
    '''
    '''

    # get mesh
    mesh_dag_path = get_dagpath(mesh, extend_to_shape=True)

    # create mesh octree
    mesh_intersector = OpenMaya.MMeshIntersector()
    mesh_intersector.create(mesh_dag_path.node(), mesh_dag_path.inclusiveMatrix())

    # get closest point
    point_ = OpenMaya.MPoint(*point)
    mesh_point = OpenMaya.MPointOnMesh()
    mesh_intersector.getClosestPoint(point_, mesh_point)

    # get closest face and triangle
    face_index = mesh_point.faceIndex()
    triangle_index = mesh_point.triangleIndex()

    # get barycentric coords
    script_util_u = OpenMaya.MScriptUtil()
    script_util_v = OpenMaya.MScriptUtil()
    script_util_u.createFromDouble(0)
    script_util_v.createFromDouble(0)
    ptr_u = script_util_u.asFloatPtr()
    ptr_v = script_util_v.asFloatPtr()
    mesh_point.getBarycentricCoords(ptr_u, ptr_v)
    u = OpenMaya.MScriptUtil.getFloat(ptr_u)
    v = OpenMaya.MScriptUtil.getFloat(ptr_v)

    return face_index, triangle_index, u, v

def get_triangle_vertex_indices(mesh, polygon_index, triangle_index):
    
    # get polygon iterator
    mesh_dag_path = get_dagpath(mesh, extend_to_shape=True)
    polygon_it = OpenMaya.MItMeshPolygon(mesh_dag_path)
    
    # set iterator index
    script_util = OpenMaya.MScriptUtil()
    script_util.createFromInt(0)
    prev_index_ptr = script_util.asIntPtr()    
    polygon_it.setIndex(polygon_index, prev_index_ptr)

    # get vertices
    points = OpenMaya.MPointArray()
    vertex_list = OpenMaya.MIntArray()
    polygon_it.getTriangle(triangle_index, points, vertex_list, OpenMaya.MSpace.kWorld)

    return (vertex_list[0], vertex_list[1], vertex_list[2])
    
def get_triange_weights(mesh, polygon_index, triangle_index, u, v):

    # get skin cluster
    skin_clusters = cmds.ls(cmds.findDeformers(mesh), type='skinCluster')
    if not skin_clusters:
        raise RuntimeError('Not skinCluster found')
    skin_cluster = skin_clusters[0]

    # get influences
    influences = cmds.skinCluster(skin_cluster, q=True, inf=True)

    # get triangle vertices
    vertex_indices = get_triangle_vertex_indices(mesh, polygon_index, triangle_index)
    barycentric_coordinates = [u, v, 1.0-u-v]

    # get weights 
    weights = [0.0 for _ in range(len(influences))]
    for i, vertex_index in enumerate(vertex_indices):

        # get vertex weights
        vertex_weights = cmds.skinPercent(skin_cluster, '{}.vtx[{}]'.format(mesh, vertex_index), query=True, value=True)

        # mult. weights by barycentric coordinates
        weights = [weights[j] + weight * barycentric_coordinates[i] for j,weight in enumerate(vertex_weights)]

    return influences, weights

def create_weighted_matrix_node(transforms, weights, precision, epsilon=1e-6):
    
    # prune and normalize weights
    pruned_transforms = list()
    pruned_weights = list()

    # prune weights
    total_weight = 0.0
    for transform_node, weight in zip(transforms, weights):

        # set precision.
        weight = float('%.{}f'.format(precision) % weight)
        
        if weight > epsilon:

            total_weight += weight
            pruned_transforms.append(transform_node)
            pruned_weights.append(weight)

    # normalize weights
    for i, weight in enumerate(pruned_weights):
        pruned_weights[i] *= 1.0 / max(total_weight, 1e-6)
    
    # ----------------------------------------------------------------------------------------------
    
    add_matrix_node = cmds.createNode('wtAddMatrix')

    for i, (transform_node, weight) in enumerate(zip(pruned_transforms, pruned_weights)):

        # make matrix relative
        mult_matrix_node = cmds.createNode('multMatrix')
        inv_matrix = cmds.getAttr('{}.worldInverseMatrix'.format(transform_node))
        cmds.setAttr('{}.matrixIn[0]'.format(mult_matrix_node), inv_matrix, type='matrix')
        cmds.connectAttr('{}.worldMatrix'.format(transform_node), '{}.matrixIn[1]'.format(mult_matrix_node))

        # connect to index
        cmds.connectAttr('{}.matrixSum'.format(mult_matrix_node), '{}.wtMatrix[{}].matrixIn'.format(add_matrix_node, i))
        cmds.setAttr('{}.wtMatrix[{}].weightIn'.format(add_matrix_node, i), weight)

        # add attribute in weighted node. (transform /  weight)
        cmds.addAttr(add_matrix_node, ln=transform_node, dv=weight, at='double', k=True)
        cmds.setAttr('{}.{}'.format(add_matrix_node, transform_node), lock=True)

    return add_matrix_node

# def get_barycentric_coords(point, mesh, face_index):

#     # get mesh
#     mesh_dag_path = get_dagpath(mesh, extend_to_shape=True)    
#     mesh_fn = OpenMaya.MFnMesh(mesh_dag_path)

#     # get triangles
#     # triangle_counts = OpenMaya.MIntArray()
#     # triangle_vertices = OpenMaya.MIntArray()
#     # mesh_fn.getTriangles(triangle_counts, triangle_vertices)

#     # 
#     polygon_it = OpenMaya.MItMeshPolygon(mesh_dag_path)
#     if face_index >= polygon_it.count():
#         raise RuntimeError('Invalid face index')

#     # set iterator index
#     script_util = OpenMaya.MScriptUtil()
#     script_util.createFromInt(0)
#     prev_index_ptr = script_util.asIntPtr()    
#     polygon_it.setIndex(face_index, prev_index_ptr)

#     num_triangles = polygon_it.numTriangles()
#     for triangle_index in range(num_triangles):

#         points = OpenMaya.MPointArray()
#         vertex_list = OpenMaya.MIntArray()
#         polygon_it.getTriangle(triangle_index, points, vertex_list, OpenMaya.MSpace.kWorld)

    # get points on triangle
    # script_util = OpenMaya.MScriptUtil()
    # script_util.createFromInt(0, 0, 0)
    # ptr = script_util.asIntPtr()
    # mesh_fn = OpenMaya.MFnMesh(mesh_dag_path)
    # mesh_fn.getPolygonTriangleVertices(face_index, triangle_index, ptr)

    # # get polygon vertices
    # vertex_list = OpenMaya.MIntArray()
    # mesh_fn.getPolygonVertices(face_index, vertex_list)

    # # get closest vertex
    # closest_vertex = -1
    # closest_distance = float('inf')

    # for i in range(vertex_list.length()):
    #     vertex_index = vertex_list[i]

    #     # get vertex position
    #     vertex_point = OpenMaya.MPoint()
    #     mesh_fn.getPoint(vertex_index, vertex_point, OpenMaya.MSpace.kWorld)

    #     distance = point_.distanceTo(vertex_point)
    #     if distance < closest_distance:
    #         closest_distance = distance
    #         closest_vertex = vertex_index
 
    # return closest_vertex
