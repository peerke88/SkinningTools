#include <toolbox_mesh/mesh_utils.hpp>

#include <limits>
#include <algorithm>
#include <toolbox_maths/calculus.hpp>
#include <toolbox_maths/matrix3x3.hpp>
#include <toolbox_config/tbx_printf.hpp>

// =============================================================================
namespace tbx_mesh {
// =============================================================================

// =============================================================================
namespace mesh_utils {
// =============================================================================

void normals(const Mesh_geometry& mesh, std::vector<tbx::Vec3>& normals_out)
{
    const int num_vertices  = (int)mesh._vertices.size();
    const int num_triangles = (int)mesh._triangles.size();
    const int num_quads     = (int)mesh._quads.size();

    normals_out.clear();
    normals_out.resize(num_vertices, tbx::Vec3(0.0f));

    for(int t = 0; t < num_triangles; t++)
    {
        const Tri_face& tri = mesh._triangles[t];
        tbx::Vec3 n = tri_normal(mesh, t);
        float norm = -n.norm();
        n /= norm;

        for ( int i = 0 ; i < 3 ; ++i )
        {
            normals_out[ tri[i] ] += n;
        }

    }

    for( int q = 0; q < num_quads; q++ )
    {
        std::vector<tbx::Vec3> v;
        get_quad_vertices(mesh, q, v);

        tbx::Vec3 e0 = v[1] - v[0] + v[2] - v[3];
        tbx::Vec3 e1 = v[3] - v[0] + v[2] - v[1];

        tbx::Vec3 n = e0.cross( e1 );
        float norm = -n.norm();
        n /= norm;

        for ( int i = 0 ; i < 4 ; ++i )
        {
            normals_out[ mesh._quads[q].vert(i) ] += n;
        }
    }
    for(int i = 0; i < num_vertices; i++)
    {
        tbx::Vec3& n = normals_out[i];
        float norm = n.norm();
        if(norm > 0.f)
            n /= -norm;
    }
}

// -----------------------------------------------------------------------------

void scale(Mesh_geometry& mesh, const tbx::Vec3& scale)
{
    for( unsigned i = 0; i < mesh._vertices.size(); ++i )
    {
        mesh._vertices[i].mult(scale);
    }
}

// -----------------------------------------------------------------------------

void translate(Mesh_geometry& mesh, const tbx::Vec3& tr)
{
    for( unsigned i = 0; i < mesh._vertices.size(); ++i)
    {
        mesh._vertices[i] += tr;
    }
}

// -----------------------------------------------------------------------------

float laplacian_cotan_weight(const Mesh_geometry& geom,
                             const Mesh_topology_lvl_1& topo,
                             tbx_mesh::Vert_idx vertex_i,
                             int edge_j )
{
    const int nb_neighs = (int)topo.nb_neighbors(vertex_i);

    const tbx_mesh::Vert_idx vertex_j      = topo.neighbor_to(vertex_i,  edge_j                                    );
    const tbx_mesh::Vert_idx vertex_j_next = topo.neighbor_to(vertex_i, (edge_j+1) % nb_neighs                     );
    const tbx_mesh::Vert_idx vertex_j_prev = topo.neighbor_to(vertex_i, (edge_j-1) >= 0 ? (edge_j-1) : nb_neighs-1 );

    const tbx::Vec3 v1 = geom.vertex(vertex_i) - geom.vertex(vertex_j_prev);
    const tbx::Vec3 v2 = geom.vertex(vertex_j) - geom.vertex(vertex_j_prev);
    const tbx::Vec3 v3 = geom.vertex(vertex_i) - geom.vertex(vertex_j_next);
    const tbx::Vec3 v4 = geom.vertex(vertex_j) - geom.vertex(vertex_j_next);

    float cotan_alpha = v1.cotan(v2); //v1.dot(v2)) / (v1.cross(v2)).norm();
    float cotan_beta  = v3.cotan(v4); //v3.dot(v4)) / (v3.cross(v4)).norm();

    // If the mesh is not a water-tight closed volume
    // we must check for edges lying on the sides of wholes
    if(topo.is_vert_on_side(vertex_i) && topo.is_vert_on_side(vertex_j))
    {
        // boundary edge, only have one such angle
        if( vertex_j_next == vertex_j_prev )
        {
            // two angles are the same, e.g. corner of a square
            cotan_beta = 0.0f;
            // Note this case should be avoided by flipping the edge of the
            // triangle...
        }
        else
        {
            // find the angle not on the boundary
            if( topo.is_vert_on_side(vertex_i) && topo.is_vert_on_side(vertex_j_next) )
                cotan_beta = 0.0;
            else
                cotan_alpha = 0.0f;
        }
    }

    float wij = (cotan_alpha + cotan_beta)/* * 0.5f*/; ///////////////////////////////////////////////// TODO: check if smoothing still operatres correctly when we properly multiply by 0.5

    if( std::isnan(wij) ){
        wij = 0.0f;
    }
    // compute the cotangent value close to 0.0f.
    // as cotan approaches infinity close to zero we clamp
    // higher values
    const float eps = 1e-6f;
    const float cotan_max = cos( eps ) / sin( eps );
    wij = tbx::clampf(wij, -cotan_max, cotan_max);


    return wij;
}

// -----------------------------------------------------------------------------

void laplacian_cotan_weights(const Mesh_geometry& geom,
                             const Mesh_topology_lvl_1& topo,
                             std::vector< std::vector<float> >& per_edge_cotan_weights)
{
    int nb_verts = geom.nb_vertices();
    per_edge_cotan_weights.resize( nb_verts );
    for(int i = 0; i < nb_verts; ++i)
    {
        const int nb_neighs = (int)topo.nb_neighbors(i);
        per_edge_cotan_weights[i].resize( nb_neighs );
        for(int edge_j = 0; edge_j < nb_neighs; ++edge_j)
        {
            float wij = laplacian_cotan_weight(geom, topo, i, edge_j);
            per_edge_cotan_weights[i][edge_j] = wij;
        }
    }
}

// -----------------------------------------------------------------------------

void uniform_weights(const Mesh_geometry& geom,
        const First_ring_it& topo,
        std::vector< std::vector<float> >& per_edge_uniform_weights, float val)
{
    int nb_verts = geom.nb_vertices();
    per_edge_uniform_weights.resize( nb_verts );
    for(int i = 0; i < nb_verts; ++i)
    {
        const int nb_neighs = (int)topo.nb_neighbors(i);
        per_edge_uniform_weights[i].resize( nb_neighs );
        for(int edge_j = 0; edge_j < nb_neighs; ++edge_j)
        {
            per_edge_uniform_weights[i][edge_j] = val;
        }
    }
}

// -----------------------------------------------------------------------------

float laplacian_positive_cotan_weight(const Mesh_geometry& geom,
                                      const Mesh_topology_lvl_1& m,
                                      tbx_mesh::Vert_idx vertex_i,
                                      int edge_j )
{
    const int nb_neighs = (int)m.nb_neighbors(vertex_i);

    const tbx_mesh::Vert_idx vertex_j      = m.neighbor_to(vertex_i,  edge_j                                    );
    const tbx_mesh::Vert_idx vertex_j_next = m.neighbor_to(vertex_i, (edge_j+1) % nb_neighs                     );
    const tbx_mesh::Vert_idx vertex_j_prev = m.neighbor_to(vertex_i, (edge_j-1) >= 0 ? (edge_j-1) : nb_neighs-1 );

    const tbx::Vec3 pi      = geom.vertex(vertex_i);
    const tbx::Vec3 pj      = geom.vertex(vertex_j);
    const tbx::Vec3 pj_prev = geom.vertex(vertex_j_prev);
    const tbx::Vec3 pj_next = geom.vertex(vertex_j_next);

    float e1 = (pi      - pj     ).norm();
    float e2 = (pi      - pj_prev).norm();
    float e3 = (pj_prev - pj     ).norm();
    // NOTE: cos(alpha) = (a^2.b^2  - c^2) / (2.a.b)
    // with a, b, c the lengths of of the sides of the triangle and (a, b)
    // forming the angle alpha.
    float cos_alpha = fabs((e3*e3 + e2*e2 - e1*e1) / (2.0f*e3*e2));

    float e4 = (pi      - pj_next).norm();
    float e5 = (pj_next - pj     ).norm();
    float cos_beta = fabs((e4*e4 + e5*e5 - e1*e1) / (2.0f*e4*e5));

    // NOTE: cot(x) = cos(x)/sin(x)
    // and recall cos(x)^2 + sin(x)^2 = 1
    // then sin(x) = sqrt(1-cos(x))
    float cotan1 = cos_alpha / sqrt(1.0f - cos_alpha * cos_alpha);
    float cotan2 = cos_beta  / sqrt(1.0f - cos_beta  * cos_beta );

    // If the mesh is not a water-tight closed volume
    // we must check for edges lying on the sides of wholes
    if(m.is_vert_on_side(vertex_i) && m.is_vert_on_side(vertex_j))
    {
        // for boundary edge, there is only one such edge
        // boundary edge, only have one such angle
        if( vertex_j_next == vertex_j_prev )
        {
            // two angles are the same, e.g. corner of a square
            cotan2 = 0.0f;
            // Note this case could be avoided by flipping the edge of the
            // triangle...
        } else {
            // find the angle not on the boundary
            if( m.is_vert_on_side(vertex_i) && m.is_vert_on_side(vertex_j_next) )
                cotan2 = 0.0;
            else
                cotan1 = 0.0f;
        }
    }

    // wij = (cot(alpha) + cot(beta))
    float wij = (cotan1 + cotan2) / 2.0f;

    if( std::isnan(wij) ){
        wij = 0.0f;
    }
    // compute the cotangent value close to 0.0f.
    // as cotan approaches infinity close to zero we clamp
    // higher values
    const float eps = 1e-6f;
    const float cotan_max = cos( eps ) / sin( eps );
    if(wij >= cotan_max ){
        wij = cotan_max;
    }

    return wij;
}

// -----------------------------------------------------------------------------

void laplacian_positive_cotan_weights(
        const Mesh_topology_lvl_1& m,
        std::vector< std::vector<float> >& per_edge_cotan_weights)
{
    int nb_verts = m.geom().nb_vertices();
    per_edge_cotan_weights.resize( nb_verts );
    for(int vertex_i = 0; vertex_i < nb_verts; ++vertex_i)
    {
        const int nb_neighs = (int)m.nb_neighbors(vertex_i);
        per_edge_cotan_weights[vertex_i].resize( nb_neighs );
        for(int edge_j = 0; edge_j < nb_neighs; ++edge_j)
        {
            float wij = laplacian_positive_cotan_weight(m.geom(), m, vertex_i, edge_j);

            per_edge_cotan_weights[vertex_i][edge_j] = wij;
        }
    }
}

// -----------------------------------------------------------------------------

std::vector<float> laplacian_edge_length_weights(
        const Mesh_geometry& geom,
        const First_ring_it& topo,
        tbx_mesh::Vert_idx vertex_i)
{
    const unsigned nb_neighs = (unsigned)topo.nb_neighbors(vertex_i);
    std::vector<float> weights(nb_neighs, 1.0f);

    tbx::Vec3 pos_i = geom.vertex(vertex_i);
    float total_length = 0.0f;
    for(unsigned edge_j = 0; edge_j < nb_neighs; edge_j++)
    {
        int vertex_j = topo.neighbor_to(vertex_i, edge_j);
        tbx::Vec3 pos_j = geom.vertex(vertex_j);

        float len = (pos_i - pos_j).norm();

        if(len < 1e-6f){
            len = 1e-6f;
            //tbx_warning("Warning: very short edge length at vertex: "+std::to_string(vertex_i)+" weld that vertex for better results");
        }

        total_length += len;
        weights[edge_j] = len;
    }

    for(unsigned edge_j = 0; edge_j < nb_neighs; edge_j++)
    {
        weights[edge_j] = total_length/weights[edge_j];
    }
    return weights;
}

// -----------------------------------------------------------------------------

void laplacian_edge_length_weights(const Mesh_geometry& geom,
        const First_ring_it &topo,
        std::vector< std::vector<float> >& per_edge_weights)
{
    int nb_verts = geom.nb_vertices();
    per_edge_weights.resize( nb_verts );
    for(int vertex_i = 0; vertex_i < nb_verts; ++vertex_i) {
        per_edge_weights[vertex_i] = laplacian_edge_length_weights(geom, topo, vertex_i);
    }
}

// -----------------------------------------------------------------------------

void flip_edge_corners(Mesh_geometry& geom)
{

    using namespace tbx_mesh;
    Vertex_to_face vertex_to;
    vertex_to.compute( geom );

    // Detect vertices lying on a degenerate boundary (corner case just one triangle)
    /*
            (v0) -> corner_vertex (this vertex is only linked to one triangle)
              +
             / \
            /f1 \
      (v1) +-----+ (v2) -> shared_edge
          / \f2 / \
         /   \ /   \
        +-----+-----+
             (v3)

             f1 = corner face
             f2 = opposite face

       We want to flip the edge as below because this triangulation is
       more stable to compute things such as the laplacian:

            (v0)
              +
             /|\
            / | \
      (v1) +  |  + (v2)
          / \ | / \
         /   \|/   \
        +-----+-----+
             (v3)

   */
    std::vector<tbx_mesh::Vert_idx> corner_vertices;
    for(unsigned vert_id = 0; vert_id < vertex_to._1st_ring_tris.size(); ++vert_id)
    {
        if( vertex_to._1st_ring_tris[vert_id].size() == 1 )
            corner_vertices.push_back( vert_id );
    }

    for(unsigned i = 0; i < corner_vertices.size(); ++i)
    {
        tbx_mesh::Vert_idx corner_vert = corner_vertices[i];
        Face_idx corner_face_id = vertex_to._1st_ring_tris[corner_vert][0];
        Tri_face corner_face = geom.triangle( corner_face_id );
        Edge shared_edge = corner_face.opposite_edge( corner_vert );

        // Seek the opposite face
        Face_idx opposite_face_id = -1;
        Tri_face opposite_face;
        for(unsigned j = 0; j < vertex_to._1st_ring_tris[shared_edge.a].size(); ++j)
        {
            Face_idx fid = vertex_to._1st_ring_tris[shared_edge.a][j];
            Tri_face face = geom.triangle( fid );
            if( face.has_edge(shared_edge) && !face.has_vertex(corner_vert) ){
                opposite_face = face;
                opposite_face_id = fid;
            }
        }

        // Do the edge flip:
        if(opposite_face_id != -1)
        {
            tbx_mesh::Vert_idx v0 = corner_vert;
            tbx_mesh::Vert_idx v1 = shared_edge.a;
            tbx_mesh::Vert_idx v2 = shared_edge.b;
            tbx_mesh::Vert_idx v3 = opposite_face.opposite_vertex( shared_edge );

            geom._triangles[corner_face_id  ] = Tri_face(v0, v1, v3);
            geom._triangles[opposite_face_id] = Tri_face(v0, v3, v2);
        }
    }
}

// -----------------------------------------------------------------------------

std::vector<std::vector< Triplet<float> > >
get_laplacian(const Mesh_geometry& geom,
              const Mesh_topology_lvl_1& topo)
{
    unsigned nv = unsigned(geom.nb_vertices());
    std::vector<std::vector< tbx::Triplet<float> >> mat_elemts(nv);
    for(unsigned i = 0; i < nv; ++i)
        mat_elemts[i].reserve(10);

    int nb_verts = geom.nb_vertices();
    for(int i = 0; i < nb_verts; ++i)
    {
        double sum = 0.;
        const int nb_neighs = (int)topo.nb_neighbors(i);
        for(int edge_j = 0; edge_j < nb_neighs; ++edge_j)
        {
            float wij = laplacian_cotan_weight(geom, topo, i, edge_j);
            sum += wij;
            mat_elemts[i].push_back( tbx::Triplet<float>(i, topo.neighbor_to(i, edge_j), wij) );
        }
        mat_elemts[i].push_back( tbx::Triplet<float>(i, i, -sum) );
    }
    return mat_elemts;
}

}// END mesh_utils NAMESPACE ===================================================
}// END tbx_mesh NAMESPACE =====================================================
