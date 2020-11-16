#ifndef NODE_SBR_CACHE_HPP
#define NODE_SBR_CACHE_HPP

#include <map>
#include "toolbox_maths/skel/bone_type.hpp"
#include <maya/MPxNode.h>
#include <maya/MNodeMessage.h>
// ---
#include <toolbox_stl/memory.hpp>
// ---

#include "toolbox_maya/utils/sub_mesh.hpp"

// FORWARD DEFS ----------------------------------------------------------------
namespace tbx_maya {
struct Maya_skeleton;
struct Maya_mesh;
}
namespace skin_brush {
class Rig;
struct User_data;
}
// END FORWARD DEFS ------------------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

/**
 * @brief Maya node to cache information
 *
 * Cache some data in a maya node, there is one cache per skinCluster.
 *
 * @see Cmd_swe_cache_manager
 */
class Node_swe_cache : public MPxNode {
public:
    Node_swe_cache();
    virtual void postConstructor() final;
    virtual ~Node_swe_cache();

    // ------
    static void* creator();
    /// Init the static attributes of our node
    static MStatus initialize();
    // ------

    ///@brief build the cache and destroys any previous instance
    ///@return a pointer to the cache node (Maya API owns that pointer)
    static Node_swe_cache* build_cache(MObject skin_cluster);

    /// destroys cache linked to the skin cluster (or does nothing if no cache)
    static void destroy_from_skin_cluster(MObject skin_cluster);

    static void destroy_cache(MObject cache_obj);

    /// Make sure the cache is up to date. updates the corresponding dirty flags,
    /// otherwise does nothing.
    void update();

    /// @brief find the "swe_cache" linked to "skin_cluster"
    /// @return true if a cache could be found.
    /// @warning unitialized cache (this->is_init() == false) will return false
    /// this mostly can happen when reloading a scene file sometimes the
    /// node get saved but internal attributes (_maya_skeleton, _maya_mesh, etc.)
    /// won't. In this case the cache needs to be re-built from scratch and we
    /// consider this node non-existent
    /// @see Node_swe_cache::build_cache()
    static bool find_valid_cache(MObject skin_cluster, Node_swe_cache*& swe_cache);

    /// @return true if there is a properly initialized cache.
    static bool has_cache(MObject skin_cluster)
    {
        Node_swe_cache* swe_cache = nullptr;
        return find_valid_cache(skin_cluster, swe_cache);
    }

    // -------------------------------------------------------------------------
    /// Secondary functions linked to the cache.
    // -------------------------------------------------------------------------


    /// This flag is true when the cache needs to be updated
    bool _cache_skin_weights_dirty;

    // -------------------------------------------------------------------------

    /// @brief find the skin cluster linked to this cache.
    /// @return the found skin cluster or MObject::kNullObj
    MObject find_skin_cluster() const;

    /// @return Mesh shape linked to this cache or null
    MObject find_output_mesh() const;

    /// @return wether initialize_deformer() was called or not;
    bool is_init() const
    {
        return _is_init;
    }

    // -------------------------------------------------------------------------

    ///@return a "Sub_mesh" representing the entire mesh.
    ///(i.e. list of indices listing any single vertex of the mesh)
    const Sub_mesh& whole_mesh() const;
    tbx_maya::Maya_skeleton* get_skeleton() const;
    tbx_maya::Maya_mesh* get_mesh() const;
    Rig* get_rig() const;
    User_data* get_user_data() const;

    // TODO: make private:
    //MString _active_joint;

private:
    ///@return null pointer if not cache could be found
    /// @note You should check wether the returned cache is properly initialized
    /// or not with "is_init()"
    static MObject find_cache_object(MObject skin_cluster);

    ///@return null pointer if no cache could be found
    /// @note You should check wether the returned cache is properly initialized
    /// or not with "is_init()"
    static Node_swe_cache* find_cache_ptr(MObject skin_cluster);

    /// Initialize cache the information using the skin_cluster.
    /// - cache mesh information
    /// - cache skeleton information (bones, weights)
    /// - connect skin_cluster.message to Node_swe_cache::_s_dummy
    /// - set is_init() to true
    /// @warning must be called before using any other methods
    /// @warning Bind pose must be set prior to this call.
    void initialize_node(MObject skin_cluster);    

    void init_callback(MObject skin_cluster);
    void remove_callback();    

    // -------------------------------------------------------------------------
    /// @name MPxNode Interface
    // -------------------------------------------------------------------------

    static void skin_cluster_attribute_changed_callback(
        MNodeMessage::AttributeMessage msg,
        MPlug& plug,
        MPlug& /*otherPlug*/,
        void* clientData);

    // -------------------------------------------------------------------------
    /// @name Attributes: deformation
    // -------------------------------------------------------------------------

    // connection to related node (skin cluster etc).
    static MObject _s_link;

public:
    // -------------------------------------------------------------------------
    /// @name Node infos
    // -------------------------------------------------------------------------
    static MTypeId _s_id;
    static MString _s_name;
    static MPxNode::Type _s_type;

    // -------------------------------------------------------------------------

private:
    // -------------------------------------------------------------------------
    /// @name Cached data
    // -------------------------------------------------------------------------
    // Data (!!not necessarily in rest pose!!)
    Uptr<tbx_maya::Maya_skeleton> _maya_skeleton;
    Uptr<tbx_maya::Maya_mesh> _maya_mesh;
    Uptr<Rig> _rig;
    Uptr<User_data> _user_data;    

    /// List of every indices for the whole mesh
    Sub_mesh _mesh_it;

    /// True when initialize_node() was called
    bool _is_init;

    /// Callback in charge to flag attribute changes related to a skin cluster.
    MCallbackId _callback_skin_cluster_attr_changed_id;

    bool _callback_enabled;
};

} // END skin_brush Namespace ===============================================

#endif // NODE_SBR_CACHE_HPP
