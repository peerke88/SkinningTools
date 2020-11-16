#ifndef TOOLBOX_MAYA_PROGRESS_WINDOW_HPP
#define TOOLBOX_MAYA_PROGRESS_WINDOW_HPP

#include <string>
#include <time.h>

// =============================================================================
namespace tbx_maya {
// =============================================================================

/**
 * @brief Maya progress window wrapper.
 *
 * Display a progress window in Maya
 *
   Usage:
   @code
    int total = nb_iter;
    Progress_window window("Process in progress", total);

    // will only display progress if operation is running greater than
    // a certain delay
    window.set_delay(0.5); // (optional default = 1 sec)

    for(int iter = 0; iter < total; iter++)
    {
        if(window.is_canceled())
            break;

        //do stuff
        ...


        window.add(1);

    }
    window.stop(); // Optional (performed when window is destructed)
    @endcode
 *
 *
 */
class Progress_window {
private:

    /// How much we wait before displaying the window
    /// (time represented in clocks ticks) (see time.h clock())
    time_t _delay;

    /// starting time (in clock ticks) (see time.h clock())
    time_t _start;
    bool _is_init;
    bool _interruptable;
    std::string _win_title;

    int _progress;
    int _max_range;
    void start(const std::string& win_title, int max_range);
public:
    Progress_window();
    Progress_window(const std::string& win_title, int max_range, bool interuptable = true);
    ~Progress_window();

    void set_delay(float seconds) {
        _delay = time_t((float)CLOCKS_PER_SEC*seconds);
        _delay = _delay <= 0 ? 0 : _delay;
    }

    void add_progess(int increment = 1);
    void reset();
    void stop();

    /// @brief force window to show regardless of the delay
    /// set with "set_delay()"
    void show();

    /// @return if the canceled button was hit by the user.
    const bool is_canceled()const;
};

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_PROGRESS_WINDOW_HPP
