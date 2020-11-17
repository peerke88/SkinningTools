#ifndef TOOLBOX_MAYA_MAYA_SKELETON_HPP
#define TOOLBOX_MAYA_MAYA_SKELETON_HPP

#include <vector>
#include <map>

#include <maya/MDagPath.h>
#include <maya/MTransformationMatrix.h>

#include <toolbox_maths/transfo.hpp>
#include <toolbox_maths/skel/bone.hpp>
#include <toolbox_maya/utils/maya_error.hpp>

// =============================================================================
namespace tbx_maya {
// =============================================================================

/**
 * @brief Compact representation of skeleton in Maya
 *
 * Given a skin cluster we extract a minimal set of information:
 *
 * Since the skin cluster only list joints that actually influence the mesh,
 * we extract this list of joints and turn in into bones. (Rest transformation
 * length/origin of the bone are extracted)
 *
 * @warning: Joints without influence are not stored in this class!
 * @warning: a skin cluster is connected to a soup of joints, there is no
 * garantee they all belong to the same skeleton hierarchy!
 *
 * FIXME: Maya_skeleton should be renamed Maya_influences to better reflect
 * what is stored
 *
 * To iterate over bones please use the skeleton iterator:
   @code
   Maya_skeleton skel;
   // Iterates over every joints *with* an influence (ignores other joints)
   for(const tbx::Bone& bone : skel){
        skel.func( bone.id() );
   }
   @endcode
 *
*/
struct Maya_skeleton {

    /// Skinning weights associated to each vertex
    /// _weights[ith_vertex] == map:(bone id, bone influence value)
    std::vector< std::map<tbx::bone::Id, float> > _weights;

private:
    /// *Sparse* list of bones!
    /// Our representation of a bone (direction and length)
    /// _bones[bone_index] = bone_info
    /// i.e. bone_info.id() == bone_index == influence_object_index
    ///
    /// bones are stored by logical index (same as skinCluster.indexForInfluenceObject())
    /// Therefore some bones may have have negative index (in the list of influence objects
    /// some logical indices might be empty)
    // Note to dev: refrain from adding an accessor to this array,
    // use the iterator "Bone_it".
    std::vector<tbx::Bone> _bones;

    /// List of parent bone for each bone. _parents[bone_id] = (parent_id);
    /// if parent_id == -1 then this parent bone does not influence the mesh
    std::vector<tbx::bone::Id> _parents;

    /// List of children bone for each bone. _sons[bone_id] = list of son_id;
    std::vector< std::vector<tbx::bone::Id> > _sons;

    /// Dag path associated to the ith bone (sparse array)
    /// _dag_paths[tbx::bone::Id]
    std::vector<MDagPath> _dag_paths;

    /// Global transformation associated to the ith bone (sparse array)
    /// at the time the skeleton was loaded (usually in bind pose)
    /// _bind_transfos[tbx::bone::Id] == joint global transfo / inclusiveMatrix
    std::vector<tbx::Transfo> _bind_global;

    /// Initial pose at the time the skeleton was loaded (usually in bind pose)
    std::vector<MTransformationMatrix> _initial_pose;

    /// Skin cluster from which we generated this skeleton
    MObject _src_skin_cluster;
public:

    Maya_skeleton() { }

    ~Maya_skeleton() { clear(); }


    Maya_skeleton(MObject skin_cluster_node) { load(skin_cluster_node); }

    /// @warning extract the current skeleton "as is".
    /// You need to make sure is in bind pose with:
    /// @code
    ///     Save_dag_pose save_pose;
    ///     save_pose.every_kjoints_to_bind_pose();
    /// @endcode
    /// Or to ask the user to set manually the bind pose.
    ///
    /// Otherwise you will extract the current pose.
    ///
    void load(MObject skin_cluster_node);

    // -------------------------------------------------------------------------
    ///@name Accessors
    // -------------------------------------------------------------------------

    /// @return the maximal possible tbx::bone::Id index for a bone +1.
    /// This way, you can allocate an array like:
    /// - std::vector<Something> my_array(get_max_size_bones())
    /// and access every its elements according to bone ids efficiently:
    /// - my_array[bone_index]
    /// @warning do not use this to iterate over bones like so:
    /// @code
    ///     for(int i = 0; i < skel.get_max_size_bones(); ++i)
    ///         // bone ids are sparse therefore 'i' is most likely to
    ///         // hit a non existing bone.
    ///         // skel.bone(i) will fail
    /// @endcode
    /// Instead use Maya_skeleton::Bone_it
    /// @code
    /// for(const tbx::Bone& bone : skel){
    ///     skel.func( bone.id() );
    /// }
    /// @endcode
    unsigned get_max_size_bones() const { return (unsigned)_bones.size(); }

    const tbx::Bone& bone(tbx::bone::Id bone_id) const;

    /// Initial pose at the time the skeleton was loaded (usually in bind pose)
    MTransformationMatrix get_initial_pose(tbx::bone::Id bone_id) const;

    /// @return W_j joint current animated position (world position)
    tbx::Transfo get_joint_transfo(tbx::bone::Id bone_id) const;

    /// @return the global transformation matrix T_j to compute
    /// linear blending skinning:
    /// deformedVertex_i = sum_j T_j . w_ij . v_i
    /// (The matrix represents the current animated pose)
    /// T_j = W_j . (B_j)^-1
    tbx::Transfo get_skinning_transfo(tbx::bone::Id bone_id) const;

    /// Global transformation of the ith joint when loading Maya_skeleton
    /// This is the global bind pose "B_j" if the skeleton was loaded
    /// (as it should) in bind pose.
    /// B_j = (T_j)^(-1) . W_j
    tbx::Transfo get_bind_global(tbx::bone::Id bone_id) const;

    /// Local transformation L_j according to the parent of the ith joint
    /// in bind pose:
    /// B_j = L_root ... L_p(j) . L_j
    /// L_j = (B_p(j))^-1 . B_j
    tbx::Transfo get_bind_local(tbx::bone::Id id) const;

    MDagPath get_dag_path(tbx::bone::Id bone_id) const;

    /// Dag path associated to the ith bone (sparse array)
    /// _dag_paths[tbx::bone::Id]
    const std::vector<MDagPath>& get_dag_paths() const;

    /// @return -1 if path not found
    tbx::bone::Id to_bone_id(MDagPath path) const;

    MObject skin_cluster() const { return _src_skin_cluster; }

    // -------------------------------------------------------------------------
    ///@name Hierachy
    // -------------------------------------------------------------------------

    /// @return list of children of bone_id.
    /// @warning joint that do not have any influence are ignored!
    /// Use Maya API to get the full hierachy
    std::vector<tbx::bone::Id> children( tbx::bone::Id bone_id ) const{
        return _sons[bone_id];
    }

    /// @return parent of bone_id, or -1 if not present.
    /// @warning joint that do not have any influence are ignored!
    /// Use Maya API to get the full hierachy
    tbx::bone::Id parent( tbx::bone::Id bone_id ) const {
        return _parents[bone_id];
    }

    /// The skin cluster is connected to a soup of joints, therefore the influencing
    /// joints might be part of several skeleton hierarchies, which means
    /// we may have several root joints!
    /// @warning joint that do not have any influence are ignored!
    /// Use Maya API to get the full hierachy
    std::vector<tbx::bone::Id> compute_root_joints() const;

    // -------------------------------------------------------------------------
    ///@name Bone iterator
    // -------------------------------------------------------------------------

private:
    /// @return list of children of bone_id.
    /// @warning joint that do not have any influence are ignored!
    std::vector<tbx::bone::Id> compute_children( tbx::bone::Id bone_id ) const;

    /// @return parent of bone_id, or -1 if not present.
    /// @warning joint that do not have any influence are ignored!
    tbx::bone::Id compute_parent( tbx::bone::Id bone_id ) const;

    unsigned next_valid_index(unsigned i) const {
        mayaAssert(i >= 0);
        while(i < _bones.size())
        {
            if( _bones[i].id() > -1 )
                break;
            else
                ++i;
        }
        return i;
    }

    ///@brief iterates over every bones and skipping empty/undefined bones in the
    /// sparse array of bones.
    class Bone_it {
        friend struct Maya_skeleton;
    protected:
        unsigned _i;
        const Maya_skeleton& _meta;
        inline Bone_it(const Maya_skeleton& meta, unsigned idx) :
            _i(idx),
            _meta( meta )
        { }
    public:
        inline bool operator!= (const Bone_it& oth) const { return _i != oth._i; }

        inline const Bone_it& operator++(   ) {
            _i = _meta.next_valid_index(_i + 1);
            return (*this);
        }

        const tbx::Bone& operator*() const { return _meta.bone(_i); }
    };
public:

    inline Bone_it begin() const {
        return Bone_it( *this, next_valid_index(0) );
    }

    inline Bone_it end() const {
        return Bone_it(*this, (unsigned)_bones.size());
    }

    // -------------------------------------------------------------------------
    ///@name Internals
    // -------------------------------------------------------------------------

private:

    /// @return joint current animated transformation.
    tbx::Transfo get_joint_transfo(const MDagPath& path) const;

    /// @return root joint when going downstream the bone "id"
    /// every looked up bone including "id" is marked as visited.
    tbx::bone::Id rec_find_root(tbx::bone::Id id, std::vector<bool>& visited) const;

    /// @param[in] joint_path : Maya joint dag path
    /// @param[in] bone_id : the id we associate to our bone tbx::Bone
    /// @param[in] bind_global : sparse list of bind matrices (world space) for
    /// each bone. bind_global[bone_id] = bind_matrix
    /// @param[in] dag_paths : sparse list of bone's dag paths
    /// dag_paths[bone_id] = dag_path
    /// @param[in]
    /// @return the output bone geometry according to the joint bind
    /// position (bind_global), the bone id is set to 'bone_id'
    tbx::Bone make_bone(const MDagPath& joint_path,
                        tbx::bone::Id bone_id) const;

    void init(int size);

    void clear();
};

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_SKELETON_HPP
