#include "toolbox_maya/data/maya_skeleton.hpp"

#include <toolbox_stl/timer.hpp>
// -----
#include <toolbox_stl/vector.hpp>
#include <toolbox_maths/skel/bone_type.hpp>
#include <toolbox_stl/map.hpp>
// -----
#include "toolbox_maya/utils/maya_dag_nodes.hpp"
#include "toolbox_maya/utils/maya_utils.hpp"
#include "toolbox_maya/utils/maya_transform.hpp"
#include "toolbox_maya/utils/maya_error.hpp"
#include "toolbox_maya/utils/find_node.hpp"
#include <toolbox_maya/utils/maya_attributes.hpp>
#include "toolbox_maya/data/maya_skin_weights.hpp"
// -----
#include <maya/MFnSkinCluster.h>
#include <maya/MDagPathArray.h>

using namespace tbx;

// =============================================================================
namespace tbx_maya {
// =============================================================================

std::vector<tbx::bone::Id> Maya_skeleton::compute_children( tbx::bone::Id bone_id ) const
{
    mayaAssert(bone_id > -1 && bone_id < tbx::bone::Id(_bones.size()));
    mayaAssert(_bones[bone_id].id() > -1);

    MStatus status;
    MDagPath vert_joint_path = _dag_paths[ bone_id ];

    int nb_children = vert_joint_path.childCount(&status);
    mayaCheck(status);
    std::vector<tbx::bone::Id> children;
    children.reserve(nb_children);
    for(int i = 0; i < nb_children; ++i)
    {
        MObject child = vert_joint_path.child(i, &status);
        mayaCheck(status);
        if( child.hasFn(MFn::kJoint) )
        {
            MDagPath child_path = get_MDagPath( child );
            int child_id = tbx::find(_dag_paths, child_path);
            if( child_id > -1 )
                children.push_back( child_id );
        }
    }

    return children;
}

// -----------------------------------------------------------------------------

tbx::bone::Id Maya_skeleton::compute_parent( tbx::bone::Id bone_id ) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    mayaAssert(_bones[bone_id].id() > -1);

    MStatus status;
    MDagPath vert_joint_path = _dag_paths[ bone_id ];

    MFnDagNode dag_node( vert_joint_path );
    unsigned nb_parents = dag_node.parentCount( &status );
    mayaCheck(status);
    if( nb_parents > 0)
    {
        MObject parent = dag_node.parent(0, &status);
        mayaCheck(status);
        if( parent.hasFn(MFn::kJoint) )
        {
            MDagPath parent_path = get_MDagPath( parent );
            int parent_id = tbx::find(_dag_paths, parent_path);
            return parent_id;
        }
    }
    return -1;
}

// -----------------------------------------------------------------------------

bone::Id Maya_skeleton::rec_find_root(bone::Id id, std::vector<bool>& visited) const
{
    visited[id] = true;
    bone::Id parent = compute_parent(id);
    if( parent > -1){
        return rec_find_root(parent, visited);
    } else {
        return id;
    }
}

// -----------------------------------------------------------------------------

std::vector<bone::Id> Maya_skeleton::compute_root_joints() const
{
    std::vector<bone::Id> root_joints;
    std::vector<bool> visited(get_max_size_bones(), false);

    for(const tbx::Bone& bone : *this){
        if( !visited[bone.id()] ){
            tbx::push_unique( root_joints, rec_find_root(bone.id(), visited));
        }
    }

    return root_joints;
}

// -----------------------------------------------------------------------------

tbx::Transfo Maya_skeleton::get_skinning_transfo(tbx::bone::Id bone_id) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    mayaAssert(_bones[bone_id].id() > -1);

    Transfo bind = this->get_bind_global( bone_id );
    MDagPath path = this->get_dag_path( bone_id );
    return world_transfo(path) * bind.fast_inverse();
}

// -----------------------------------------------------------------------------

const std::vector<MDagPath>& Maya_skeleton::get_dag_paths() const
{
    return _dag_paths;
}

// -----------------------------------------------------------------------------

const tbx::Bone& Maya_skeleton::bone(tbx::bone::Id bone_id) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    mayaAssert(_bones[bone_id].id() > -1);
    return _bones[bone_id];
}

// -----------------------------------------------------------------------------

Transfo Maya_skeleton::get_bind_global(tbx::bone::Id bone_id) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    return _bind_global[bone_id];
}

// -----------------------------------------------------------------------------

Transfo Maya_skeleton::get_bind_local(bone::Id bone_id) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    Transfo bind_lcl;
    bone::Id parent_id = compute_parent(bone_id);

    if(parent_id == -1)
        //FIXME: parent_id == -1 only means there is no influencing object, it does not mean there is no parent.
        bind_lcl = get_bind_global(bone_id); // Root is local to itself.
    else
        bind_lcl = get_bind_global(parent_id).fast_inverse() * get_bind_global(bone_id);

    return bind_lcl;
}

// -----------------------------------------------------------------------------

tbx::Transfo Maya_skeleton::get_joint_transfo(tbx::bone::Id bone_id) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    MDagPath path = this->get_dag_path( bone_id );
    return world_transfo(path);
}

// -----------------------------------------------------------------------------

MDagPath Maya_skeleton::get_dag_path(tbx::bone::Id bone_id) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    mayaAssert(_bones[bone_id].id() > -1);
    return _dag_paths[bone_id];
}

// -----------------------------------------------------------------------------

tbx::bone::Id Maya_skeleton::to_bone_id(MDagPath path) const
{
    return tbx::find( _dag_paths, path );
    /*
         * Alternatively:
        MStatus status;
        unsigned lidx = skin_cluster.indexForInfluenceObject(path, &status);
        mayaCheck(status);
        Not sure which one is faster.
        */
}

// -----------------------------------------------------------------------------

Transfo Maya_skeleton::get_joint_transfo(const MDagPath& path) const
{
    return world_transfo(path);
}

// -----------------------------------------------------------------------------

tbx::Bone Maya_skeleton::make_bone(const MDagPath& joint_path,
                                   tbx::bone::Id bone_id) const
{
    /*
     * Note: we compute the length and direction of bones using parent and
     * children joints. (regardless if they have an influence or not)
    */

    MStatus status = MStatus::kSuccess;
    Transfo tr_start = get_joint_transfo(joint_path);

    Point3 start = Point3( tr_start.get_translation() );
    Point3 end   = start + tr_start.x().normalized();

    unsigned nb_children = joint_path.childCount(&status);
    mayaCheck(status);

    // By default we assume the joint is not a leaf or a root joint
    tbx::bone::Role role = tbx::bone::Role::eINTERNAL;

    // If there is a child joint we can enhance the end point of the bone.
    if( nb_children > 0 )
    {
        Point3 avg(0.0f);
        for(unsigned i = 0; i < nb_children; ++i)
        {
            MObject child = joint_path.child(i, &status);
            mayaCheck(status);
            if( child.hasFn(MFn::kJoint) )
            {
                MDagPath child_path = get_MDagPath( child );
                avg += Point3( get_joint_transfo(child_path).get_translation() );
            }
        }
        end = avg / (float)nb_children;

    } else { // no children well its a leaf
        role = tbx::bone::Role::eLEAF;
    }

    MFnDagNode dag_node( joint_path );

    unsigned nb_parents = dag_node.parentCount( &status );
    mayaCheck(status);
    if( nb_parents > 0) {
        MObject parent = dag_node.parent(0, &status);
        mayaCheck(status);
        if( !parent.hasFn(MFn::kJoint) ) { // no parent of type kJoint -> root
            role = tbx::bone::Role::eROOT;
        }
    } else { // no parent at all -> root
        role = tbx::bone::Role::eROOT;
    }

    return tbx::Bone(start, end, bone_id, role);
}

// -----------------------------------------------------------------------------

void Maya_skeleton::init(int size)
{
    clear();
    _parents.resize( size, -1 );
    _sons.resize( size );
    _bones.resize(size);
    _dag_paths.resize(size);
    _bind_global.resize(size);
    _initial_pose.resize(size);
}

// -----------------------------------------------------------------------------

void Maya_skeleton::clear()
{
    _parents.clear();
    _sons.clear();
    _bones.clear();
    _dag_paths.clear();
    _bind_global.clear();
    _initial_pose.clear();
}

// -----------------------------------------------------------------------------

static int max_influence_obj_index(const MDagPathArray& influence_objs,
                                   const MFnSkinCluster& skin_cluster)
{
    MStatus status;
    int max_idx = 0;
    for(int i = 0; i < (int)influence_objs.length(); ++i)
    {
        const MDagPath& path = influence_objs[i];
        mayaCheck(status);
        unsigned idx = skin_cluster.indexForInfluenceObject( path, &status);
        mayaCheck(status);
        if((int)idx > max_idx)
            max_idx = idx;
    }
    return max_idx;
}

// -----------------------------------------------------------------------------

MTransformationMatrix Maya_skeleton::get_initial_pose(tbx::bone::Id bone_id) const
{
    mayaAssert(bone_id > -1 && bone_id < _bones.size());
    mayaAssert(_bones[bone_id].id() > -1);
    return _initial_pose[bone_id];
}

// -----------------------------------------------------------------------------

void Maya_skeleton::load(MObject skin_cluster_node)
{
    clear();
    _src_skin_cluster = skin_cluster_node;

    MStatus status = MStatus::kSuccess;
    MFnSkinCluster skin_cluster(skin_cluster_node, &status);
    mayaCheck(status);

    MDagPathArray influence_objs;
    skin_cluster.influenceObjects(influence_objs, &status);
    mayaCheck(status);

    // Search maximum logical index in influence_objs:
    int max_idx = max_influence_obj_index(influence_objs, skin_cluster);

    int nb_bones = max_idx+1;
    init( nb_bones );

    for(int i = 0; i < (int)influence_objs.length(); ++i)
    {
        const MDagPath& path = influence_objs[i];
        mayaCheck(status);
        unsigned idx = skin_cluster.indexForInfluenceObject( path, &status);
        mayaCheck(status);
        // ------
        _dag_paths[idx] = path;
        _bones[idx] = make_bone( path, idx);
        _bind_global[idx] = get_joint_transfo(path);
        _initial_pose[idx] = get_MTransformationMatrix( get_MObject(path) );
        // ------
    }

    // Build bone geometry:
    for(int i = 0; i < (int)influence_objs.length(); ++i)
    {
        const MDagPath& path = influence_objs[i];
        mayaCheck(status);
        unsigned idx = skin_cluster.indexForInfluenceObject( path, &status);
        mayaCheck(status);

    }

    _parents.clear();
    _parents.resize( nb_bones, -1);
    for(const tbx::Bone& bone : *this)
    {
        tbx::bone::Id id = bone.id();
        _parents[id] = compute_parent  (id);
        _sons[id]    = compute_children(id);
    }

    //skin_weights::get_all_through_mfnskincluster(_src_skin_cluster, _weights);
    skin_weights::get_all_through_mplug(_src_skin_cluster, _weights);
}

}// END tbx_maya Namespace =====================================================
