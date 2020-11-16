#pragma once
#include <vector>
#include <toolbox_stl/memory.hpp>
#include <toolbox_maths/transfo.hpp>
#include "data/skin_deformer.hpp"

// Forward declaration ---------------------------------------------------------
namespace skin_brush {
}
// Forward declaration end -----------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

/**
  @brief Build a list of skeleton poses from a skeleton.

  @code
  Build_examples ex;
  ex.build_example_poses(skel, mesh);

  for(const Deformer& dfm : ex){

  }
  @endcode

*/
class Build_examples {
    bool _is_deformer_init;
    /// Precompute skin deformer per example
    std::vector< Uptr<Skin_deformer> > _list_deformers_per_example;
    /// _list_examples[pose_i][bone_i];
    std::vector< std::vector<Transfo> > _list_examples; // List of local user poses (like twist bend -30 +30 etc.)

    const Maya_skeleton* _skel;
    const Maya_mesh* _mesh;
public:

    Build_examples(const Maya_skeleton* skel,
                   const Maya_mesh* mesh = nullptr)
        : _is_deformer_init(false)
        ,_skel(skel)
        ,_mesh(mesh)
    {

    }

    /// @brief Preset for arap relaxation
    static void build_ex_for_arap_optimization(Build_examples& ex);

    ///@brief Move each joint in isolation and create a single a example each time.
    ///@param ignore_list : list of bone ids that should be excluded from
    /// the pose generation
    void add_isolated_joints_motions(
            float degree_angle,
            const std::vector<tbx::bone::Id>& ignore_list = {});

    ///@brief add the rest pose (bind pose) as a single example.
    void add_rest_pose();

    ///@move each
    void add_random_pose_all_joints( int nb_max_samples,
                                     float degree_angle,
                                     const std::vector<tbx::bone::Id>& ignore_list = {});

    ///@brief Tearing apart (quartering XD) the skeleton by slightly translating
    /// every joint in the direction of their parent.
    void add_quartering_pose();

    void clear(){
        _list_deformers_per_example.clear();
        _list_examples.clear();
        _is_deformer_init = false;
    }


    void build_deformers(const Maya_mesh* mesh = nullptr);

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

    inline unsigned nb_examples() const {
        return unsigned(_list_examples.size());
    }

    const std::vector<std::vector<Transfo> >& get_list_examples() const;

    ///@warning: launch build_deformers() first
    inline const Skin_deformer& get_deformer(int pose_i) const {
        mayaAssert(_is_deformer_init);
        return *(_list_deformers_per_example[pose_i]);
    }

    /** @brief Iterates over the set of examples _list_examples */
    class Example_it {
        friend class Build_examples;
    protected:
        unsigned _i;
        const Build_examples& _examples;
        inline Example_it(const Build_examples& examples, unsigned idx) :
            _i(idx),
            _examples( examples )
        { }
    public:
        inline bool operator!= (const Example_it& oth) const { return _i != oth._i; }
        inline const Example_it& operator++(   ) { ++_i; return (*this); }

        const Skin_deformer& operator*() const { return _examples.get_deformer(_i); }
    };

    inline Example_it begin() const { return Example_it(*this, 0);              }
    inline Example_it end()   const { return Example_it(*this, nb_examples());  }

};

}// END skin_brush Namespace ========================================
