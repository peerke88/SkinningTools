#ifndef TOOL_BOX_TIMER_HPP
#define TOOL_BOX_TIMER_HPP

///@cond ext_forward_def
namespace boost{ class timer; }
///@endcond

// =============================================================================
namespace tbx {
// =============================================================================

/** @class Timer
    @brief boost timer wrapper class
*/
struct Timer{
    Timer();
    Timer(const Timer& t);
    Timer& operator=(const Timer& t);

    ~Timer();

    /// Restart the timer without erasing previous measured time
    /// (accessible with get_value())
    void start();
    /// return elapsed time in seconds
    double elapsed();
    /// Get last measured in seconds since the last elapsed() call
    double get_value();
    /// restart the timer and erase the previous results
    void reset();

private:
    //TODO: delete this dependency to boost.
    boost::timer* _boost_timer;
    double _elapsed_time;
};

}// END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_TIMER_HPP
