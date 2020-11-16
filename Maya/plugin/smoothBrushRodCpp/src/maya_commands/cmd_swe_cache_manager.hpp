#ifndef CMD_SWE_CACHE_MANAGER_HPP
#define CMD_SWE_CACHE_MANAGER_HPP

#include <maya/MPxCommand.h>


// =============================================================================
namespace skin_brush {
// =============================================================================

/**
 * @brief Maya command "SWE_cache_manager".
 *  Please refer to the following page for documentation:
    @ref cmd_skinning_weights (doc/manual/source_docs/commands/skinning_weights.dox)
    @see Node_swe_cache
*/
class Cmd_swe_cache_manager : public MPxCommand {
public:

    Cmd_swe_cache_manager() { }
    static char _s_name[];
    static void* creator() { return new Cmd_swe_cache_manager(); }
    virtual ~Cmd_swe_cache_manager() { }

    // -------------------------------------------------------------------------
    /// @name MPxCommand overrides
    // -------------------------------------------------------------------------
    ///@{
    MStatus doIt( const MArgList& ) final;
    bool isUndoable() const final { return false; /* TODO: undo redo for the active joint... */ }
    ///@}

};

}// END Namespace ==============================================================


#endif // CMD_SWE_CACHE_MANAGER_HPP
