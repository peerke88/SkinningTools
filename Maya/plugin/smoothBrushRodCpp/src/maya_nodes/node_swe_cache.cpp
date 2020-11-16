#include "maya_nodes/node_swe_cache.hpp"

#include <maya/MItDependencyGraph.h>
#include <maya/MFnMessageAttribute.h>
// ----------
#include <toolbox_maya/utils/maya_attributes.hpp>
#include <toolbox_maya/utils/maya_error.hpp>
#include <toolbox_maya/utils/maya_utils.hpp>
#include <toolbox_maya/utils/maya_dependency_nodes.hpp>
#include <toolbox_maya/utils/maya_dag_nodes.hpp>
#include <toolbox_maya/utils/find_node.hpp>
#include <toolbox_maya/data/maya_skeleton.hpp>
#include <toolbox_maya/data/maya_skin_weights.hpp>
#include <toolbox_mesh/mesh_utils.hpp>
#include <toolbox_stl/time_tracker.hpp>
#include <toolbox_stl/vector.hpp>

// ------------
#include "data/rig.hpp"
#include "data/user_data.hpp"
#include "sbr_utils.hpp"


// =============================================================================
namespace skin_brush {
// =============================================================================

// -----------------------------------------------------------------------------
// static attributes
// -----------------------------------------------------------------------------

MString Node_swe_cache::_s_name("SBR_cacheNode");
MTypeId Node_swe_cache::_s_id(0x00131770);
MPxNode::Type Node_swe_cache::_s_type(MPxNode::kDependNode);

// ----
MObject Node_swe_cache::_s_link;

// -----------------------------------------------------------------------------

Node_swe_cache::Node_swe_cache()
    : MPxNode()
    , _cache_skin_weights_dirty(false)
    , _is_init(false)
    , _callback_enabled(false)    
{
}

// -----------------------------------------------------------------------------

void Node_swe_cache::postConstructor()
{
    mayaCheck(setExistWithoutInConnections(false));
}

// -----------------------------------------------------------------------------

Node_swe_cache::~Node_swe_cache()
{
}

// -----------------------------------------------------------------------------

void* Node_swe_cache::creator()
{
    return new Node_swe_cache();
}

// -----------------------------------------------------------------------------

/// Init the static attributes of our node
MStatus Node_swe_cache::initialize()
{
    try {
        MStatus status;
        MFnMessageAttribute msg_attr;
        _s_link = msg_attr.create("link", "lnk", &status);
        mayaCheck(status);
        mayaCheck(msg_attr.setArray(true));
        mayaCheck(msg_attr.setIndexMatters(false));
        mayaCheck(addAttribute(_s_link));
    }
    catch (std::exception& e) {
        maya_print_error(e);
        return MS::kFailure;
    }
    return MStatus::kSuccess;
}

// -----------------------------------------------------------------------------

Node_swe_cache* Node_swe_cache::build_cache(MObject skin_cluster)
{
    Node_swe_cache* cache = nullptr;
    Node_swe_cache::destroy_from_skin_cluster(skin_cluster);
    cache = create_node<Node_swe_cache>();
    cache->initialize_node(skin_cluster);
    return cache;
}

// -----------------------------------------------------------------------------

void Node_swe_cache::destroy_from_skin_cluster(MObject skin_cluster)
{
    MObject cache;
    if (!(cache = Node_swe_cache::find_cache_object(skin_cluster)).isNull()) {
        Node_swe_cache::destroy_cache(cache);
    }

}

// -----------------------------------------------------------------------------

void Node_swe_cache::destroy_cache(MObject cache_obj)
{
    Node_swe_cache* cache = get_interface_node<Node_swe_cache>(cache_obj);
    cache->remove_callback();

    MObject skin_cluster = cache->find_skin_cluster();
    mayaAssert(!skin_cluster.isNull());

    disconnect(skin_cluster, "message", cache_obj, Node_swe_cache::_s_link);
    delete_node(cache_obj);
}

// -----------------------------------------------------------------------------

void Node_swe_cache::initialize_node(MObject skin_cluster)
{
    connect(skin_cluster, "message", thisMObject(), Node_swe_cache::_s_link);

    MObject out_mesh_shape;
    if (!find_dfm_output_deformed_mesh(skin_cluster, out_mesh_shape)) {
        mayaWarning("Can't find output mesh");
        return;
    }

    _maya_skeleton.reset(new Maya_skeleton(skin_cluster));
    
    _maya_mesh.reset(new Maya_mesh(out_mesh_shape, tbx_maya::world_mmatrix(out_mesh_shape)));
    
    _rig.reset(new Rig(*_maya_mesh, *_maya_skeleton));
    _user_data.reset(new User_data());
    _mesh_it.set(_maya_mesh->nb_vertices());

    // Add callback to update '_skin_weights_dirty' flag.
    // (every time skin cluster weights change we set it to 'true')
    init_callback(skin_cluster);
    _is_init = true;

}

// -----------------------------------------------------------------------------

// NOTE: currently you update skin weight dirty flag through a callback
// but you could use an attribute and the MPxNode::compute & data_block.isClean
// to detect changes in the skin weights...
// -> problem isClean seems to not be triggered when painting with the normal
// maya skin paint mode.
void Node_swe_cache::skin_cluster_attribute_changed_callback(
    MNodeMessage::AttributeMessage msg,
    MPlug& plug,
    MPlug& /*otherPlug*/,
    void* swe_cache_ptr)
{
    try {
        MStatus status;

        if (!((Node_swe_cache*)(swe_cache_ptr))->_callback_enabled)
            return;

        if (!(msg & MNodeMessage::kAttributeSet))
            return;

        // To be tested:
        if (((Node_swe_cache*)(swe_cache_ptr))->_cache_skin_weights_dirty)
            return;

        MObject node = plug.node(&status);
        mayaCheck(status);

        if (node.apiType() == MFn::Type::kSkinClusterFilter) {
            MString na = plug.name(&status);
            mayaCheck(status);
            std::string name(na.asChar());
            std::string sub = name.substr(name.find_first_of('.') + 1, 10);
            if (sub == "weightList") {
                ((Node_swe_cache*)(swe_cache_ptr))->_cache_skin_weights_dirty = true;
            }
        }
    }
    catch (std::exception& e) {
        maya_print_error(e);
    }
}

// -----------------------------------------------------------------------------

const Sub_mesh& Node_swe_cache::whole_mesh() const
{
    mayaAssert(_is_init);
    return _mesh_it;
}

Maya_skeleton* Node_swe_cache::get_skeleton() const
{
    mayaAssert(_is_init);
    return _maya_skeleton.get();
}

Rig* Node_swe_cache::get_rig() const
{
    mayaAssert(_is_init);
    return _rig.get();
}

Maya_mesh* Node_swe_cache::get_mesh() const
{
    mayaAssert(_is_init);
    return _maya_mesh.get();
}

User_data* Node_swe_cache::get_user_data() const
{
    mayaAssert(_is_init);
    return _user_data.get();
}

// -----------------------------------------------------------------------------

MObject Node_swe_cache::find_cache_object(MObject skin_cluster)
{
    
    MStatus status;
    MPlug message_plug = get_plug(skin_cluster, "message");
    MObject result = MObject::kNullObj;
    if (!is_connected(message_plug))
        return MObject::kNullObj;


    // walk the tree of stuff upstream from this plug
    MItDependencyGraph dg_it(message_plug,
                             MFn::kInvalid,
                             MItDependencyGraph::kDownstream,
                             MItDependencyGraph::kDepthFirst,
                             MItDependencyGraph::kPlugLevel,
                             &status);

    mayaCheck(status);
    dg_it.disablePruningOnFilter();
    for (; !dg_it.isDone(); dg_it.next()) {
        MObject curr_node = dg_it.currentItem();
        // go until we find the cache node
        if (get_type_id(curr_node) == Node_swe_cache::_s_id) {
            result = curr_node;
            break;
        }
    }

    
    return result;
}

// -----------------------------------------------------------------------------

Node_swe_cache* Node_swe_cache::find_cache_ptr(MObject skin_cluster)
{
    MObject cache = find_cache_object(skin_cluster);
    if (!cache.isNull())
        return get_interface_node<Node_swe_cache>(cache);
    else
        return nullptr;
}

// -----------------------------------------------------------------------------

void Node_swe_cache::update()
{    
    mayaAssertMsg(_is_init, "The cache is corrupted re-build it.");

    //get_mesh()->topo()._topo_lvl_1.update(get_mesh()->geom());
    get_mesh()->topo()._islands.compute( get_mesh()->topo().first_ring() );
    get_mesh()->topo()._edges.compute( get_mesh()->topo().first_ring() );

#if 1
    if (!_cache_skin_weights_dirty)
        return;
#endif


    MObject skin_cluster = find_skin_cluster();
    if (skin_cluster.isNull()) {
        mayaWarning("Can't find skin cluster");
        return;
    }

    if (g_debug_mode) {
        MGlobal::displayInfo("update SWE cache (skin weights)");
    }
    //try to implement a method to update only a subset through this node.

    
    //skin_weights::get_all_through_mfnskincluster(skin_cluster, _maya_skeleton->_weights);

    skin_weights::get_all_through_mplug(skin_cluster, _maya_skeleton->_weights);
    

    _cache_skin_weights_dirty = false;
}

// -----------------------------------------------------------------------------

bool Node_swe_cache::find_valid_cache(MObject skin_cluster,
                                      Node_swe_cache*& swe_cache)
{
    
    swe_cache = nullptr;
    MObject cache_obj = find_cache_object(skin_cluster);
    if (!cache_obj.isNull()) {
        auto* tmp = get_interface_node<Node_swe_cache>(cache_obj);
        if (tmp->is_init()) {
            swe_cache = tmp;
        }
    }
    
    return swe_cache != nullptr;
}

// -----------------------------------------------------------------------------

MObject Node_swe_cache::find_output_mesh() const
{
    MObject output_mesh_shape = MObject::kNullObj;
    MObject skin_cluster = find_skin_cluster();
    if (skin_cluster.isNull())
        return MObject::kNullObj;

    if (find_dfm_output_deformed_mesh(skin_cluster, output_mesh_shape))
        return output_mesh_shape;

    return MObject::kNullObj;
}

// -----------------------------------------------------------------------------

MObject Node_swe_cache::find_skin_cluster() const
{
    MObject skin_cluster = MObject::kNullObj;
    MStatus status;
    MPlug message_plug = get_plug(thisMObject(), Node_swe_cache::_s_link);
    if (!is_connected(message_plug))
        return MObject::kNullObj;

    // walk the tree of stuff upstream from this plug
    MItDependencyGraph dg_it(message_plug,
                             MFn::kInvalid,
                             MItDependencyGraph::kUpstream,
                             MItDependencyGraph::kDepthFirst,
                             MItDependencyGraph::kPlugLevel,
                             &status);

    mayaCheck(status);
    dg_it.disablePruningOnFilter();
    for (; !dg_it.isDone(); dg_it.next()) {
        MObject curr_node = dg_it.currentItem();
        // go until we find a skinCluster
        if (curr_node.apiType() == MFn::kSkinClusterFilter) {
            skin_cluster = curr_node;
            return skin_cluster;
        }
    }

    return skin_cluster;
}

// -----------------------------------------------------------------------------

void Node_swe_cache::init_callback(MObject skin_cluster)
{
    if (!_callback_enabled) {
        
        MStatus status;
        _callback_skin_cluster_attr_changed_id = MNodeMessage::addAttributeChangedCallback(skin_cluster, skin_cluster_attribute_changed_callback, this, &status);
        mayaCheck(status);

        _callback_enabled = true;
        
    }
}

// -----------------------------------------------------------------------------

void Node_swe_cache::remove_callback()
{
    if (_callback_enabled) {
        
        _callback_enabled = false;
        MMessage::removeCallback(_callback_skin_cluster_attr_changed_id);
        
    }
}

} // END skin_brush Namespace ==================================================
