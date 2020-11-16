#pragma once
// =============================================================================
namespace skin_brush {
// =============================================================================


struct Brush {
    Brush(int v_idx, float val) : _v_idx(v_idx), _val(val) { }
    Brush() : _v_idx(-1), _val(-1.0f) { }
    int _v_idx; ///< vertex index
    float _val; ///< vertex value
};

}// END skin_brush Namespace ========================================
