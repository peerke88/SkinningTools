#pragma once

#include <maya/MPxCommand.h>
#include <toolbox_maths/vector2.hpp>
#include "maya_nodes/node_swe_cache.hpp"

// =============================================================================
namespace skin_brush {
// =============================================================================

/**
 * @brief Maya command "SBR_brush".
*/
class Cmd_swe_brush : public MPxCommand {
public:

    static char _s_name[];
    static void* creator() { return new Cmd_swe_brush(); }

    Cmd_swe_brush() :
        _action(eUndef),        
        _cache(nullptr),        
        _flood(false),
        _extra_links(false),
        _radius_extra_links(0.0f),
        _max_influences(0)
    { }

    virtual ~Cmd_swe_brush() { }

    // -------------------------------------------------------------------------
    /// @name MPxCommand overrides
    // -------------------------------------------------------------------------
    ///@{
    MStatus doIt( const MArgList& ) final;
    MStatus redoIt();
    MStatus undoIt();
    bool isUndoable() const final {
        // Can't undo build cache
        return _action != eBuildCache;
    }
    ///@}

    // -------------------------------------------------------------------------
    /// @name
    // -------------------------------------------------------------------------
private:

    enum Action_e {
        eSmooth,
        eRelax,
        eBuildCache,
        eUndef
    };

    Action_e _action;
    MString _skin_cluster_name;
    MObject _skin_cluster;

    Sub_mesh _sub_mesh;
    // Original weights for undo
    std::vector< std::map<tbx::bone::Id, float> > _original_weights;    

    std::vector<int> _vertex_selection;

    MString _brush_context;

    // Smoothing    
    std::vector<tbx::Vec2> _constraints;

    Node_swe_cache* _cache;

    /// when true apply to every vertices
    bool _flood;

    bool _extra_links;

    float _radius_extra_links;

    /// Try to maintain the maximum number of influences below (0 = we don't care)
    int _max_influences;

    std::vector<bool> _locked_joints;
};

}// END skin_brush Namespace ========================================


