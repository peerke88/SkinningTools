#include "operations/arap_svd.hpp"

#include <toolbox_maths/eigen_lib_interop.hpp>

// =============================================================================
namespace skin_brush {
// =============================================================================

// From Mathias Muller optimized svd:
// https://animation.rwth-aachen.de/media/papers/2016-MIG-StableRotation.pdf
void extract_rotation(const Mat3& A, Quat& q,const unsigned int max_iter = 30)
{
    for (unsigned int iter = 0; iter < max_iter; iter++){
        Mat3 R = q.to_matrix3();

        Vec3 omega = (
                (R.x().cross( (A.x()) ) +
                 R.y().cross( (A.y()) ) +
                 R.z().cross( (A.z()) ) )
                * (1.0 / fabs(R.x().dot( (A.x()) ) +
                              R.y().dot( (A.y()) ) +
                              R.z().dot( (A.z()) )) + 1.0e-9)
                    );

        float w = omega.norm();
        if (w < 1.0e-9)
            break;

        q = Quat::from_axis_angle((1.0f / w)*omega, w ) * q;
        q.normalize();
    }
}

// -----------------------------------------------------------------------------

void compute_SVD_rotations_with_quats(
        std::vector<tbx::Mat3>& svd_rotations,
        std::vector<tbx::Quat>& quat_rotations,
        const std::vector<std::map<int, float> >& weights,
        const First_ring_it& topo,
        const std::vector<Vec3>& vertices,
        const Sub_mesh& sub_mesh,
        const std::vector< std::vector<float> >& per_edge_weights,
        const Skin_deformer& dfm)
{
    Eigen::Matrix3f eye = Eigen::Matrix3f::Identity();

    for(unsigned i : sub_mesh)
    {
        unsigned valence = topo.nb_neighbors(i);

        Eigen::MatrixXf P(3, valence);
        Eigen::MatrixXf Q(3, valence);
        for(unsigned n = 0; n < valence; n++)
        {
            int vert_j = topo.neighbor_to(i, n);

            // eij = pi - pj
            // compute: P_i * D_i in the paper
            float w_cotan = per_edge_weights[i][n];
            Vec3 v = (vertices[i] - vertices[vert_j]) * w_cotan;
            //P.col(degree) = Eigen::Vector3f(v.x, v.y, v.z);
            P(0, n) = v.x;
            P(1, n) = v.y;
            P(2, n) = v.z;

            // eij' = pi' - pj'
            //compute: P_i'
            v = dfm.vert_anim_pos(weights, i) - dfm.vert_anim_pos(weights, vert_j);
            //Q.col() = Eigen::Vector3f(v.x, v.y, v.z);
            Q(0, n) = v.x;
            Q(1, n) = v.y;
            Q(2, n) = v.z;
        }
        // Compute the 3 by 3 covariance matrix:
        // actually S = (P * W * Q.t()); W is already considerred in the previous step (P=P*W)
        Eigen::Matrix3f S = (P * Q.transpose());

#if 1
        // Compute the singular value decomposition S = UDV.t
        Eigen::JacobiSVD<Eigen::MatrixXf> svd(S, Eigen::ComputeThinU | Eigen::ComputeThinV); // X = U * D * V.t()

        Eigen::MatrixXf V = svd.matrixV();
        Eigen::MatrixXf Ut = svd.matrixU().transpose();

        eye(2,2) = (V * Ut).determinant();	// remember: Eigen starts from zero index

        // V*U.t may be reflection (determinant = -1). in this case, we need to change the sign of
        // column of U corresponding to the smallest singular value (3rd column)
        Eigen::Matrix3f rot = (V * eye * Ut);


        svd_rotations[i] = Mat3((float)rot(0,0), (float)rot(0,1), (float)rot(0,2),
                                (float)rot(1,0), (float)rot(1,1), (float)rot(1,2),
                                (float)rot(2,0), (float)rot(2,1), (float)rot(2,2) ); //Ri = (V * eye * U.t());
#else
        extract_rotation( tbx::to_mat3(S), quat_rotations[i]);
        svd_rotations[i] = quat_rotations[i].to_matrix3();
#endif

    }
}

// -----------------------------------------------------------------------------

void compute_SVD_rotations(std::vector<tbx::Mat3>& svd_rotations,
                           const std::vector<std::map<int, float> >& weights,
                           const First_ring_it& topo,
                           const std::vector<Vec3>& vertices,
                           const Sub_mesh& sub_mesh,
                           const std::vector< std::vector<float> >& per_edge_weights,
                           const Skin_deformer& dfm)
{
    Eigen::Matrix3f eye = Eigen::Matrix3f::Identity();

    for(unsigned i : sub_mesh)
    {
        unsigned valence = topo.nb_neighbors(i);

        Eigen::MatrixXf P(3, valence);
        Eigen::MatrixXf Q(3, valence);
        for(unsigned n = 0; n < valence; n++)
        {
            int vert_j = topo.neighbor_to(i, n);

            // eij = pi - pj
            // compute: P_i * D_i in the paper
            float w_cotan = per_edge_weights[i][n];
            Vec3 v = (vertices[i] - vertices[vert_j]) * w_cotan;
            //P.col(degree) = Eigen::Vector3f(v.x, v.y, v.z);
            P(0, n) = v.x;
            P(1, n) = v.y;
            P(2, n) = v.z;

            // eij' = pi' - pj'
            //compute: P_i'
            v = dfm.vert_anim_pos(weights, i) - dfm.vert_anim_pos(weights, vert_j);
            //Q.col() = Eigen::Vector3f(v.x, v.y, v.z);
            Q(0, n) = v.x;
            Q(1, n) = v.y;
            Q(2, n) = v.z;
        }
        // Compute the 3 by 3 covariance matrix:
        // actually S = (P * W * Q.t()); W is already considerred in the previous step (P=P*W)
        Eigen::MatrixXf S = (P * Q.transpose());

        // Compute the singular value decomposition S = UDV.t
        Eigen::JacobiSVD<Eigen::MatrixXf> svd(S, Eigen::ComputeThinU | Eigen::ComputeThinV); // X = U * D * V.t()

        Eigen::MatrixXf V = svd.matrixV();
        Eigen::MatrixXf Ut = svd.matrixU().transpose();

        eye(2,2) = (V * Ut).determinant();	// remember: Eigen starts from zero index

        // V*U.t may be reflection (determinant = -1). in this case, we need to change the sign of
        // column of U corresponding to the smallest singular value (3rd column)
        Eigen::Matrix3f rot = (V * eye * Ut);


        svd_rotations[i] = Mat3((float)rot(0,0), (float)rot(0,1), (float)rot(0,2),
                                (float)rot(1,0), (float)rot(1,1), (float)rot(1,2),
                                (float)rot(2,0), (float)rot(2,1), (float)rot(2,2) ); //Ri = (V * eye * U.t());
    }
}

}// END skin_brush Namespace ========================================
