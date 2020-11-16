#ifndef TOOLBOX_TIME_TRACKER_HPP
#define TOOLBOX_TIME_TRACKER_HPP

#include <string>
#include <vector>
#include <functional>

#include <toolbox_stl/timer.hpp>

// =============================================================================
namespace tbx {
// =============================================================================

class Time_tracker;
/// @note disabled by default g_timer.set_enable(true) to output results.
extern Time_tracker g_timer;

/** @brief Facilitate time measurement and display of task and sub tasks.

    @code
    Time_tracker _tracker;

    _tracker.push("Main task");
    // A 8ms computation
    _tracker.push("Sub task");
            _tracker.push("SubSub task 1");
                // A 2ms computation
            _tracker.pop(); // SubSub task 1

            _tracker.push("SubSub task 2");
                // A 50ms computation
            _tracker.pop(); // SubSub task 2
        _tracker.pop(); // Sub task
    _tracker.pop(); // Main task

    // Will display:
    // Main Task{
    //     Sub task{
    //         SubSub task 1{} 2ms
    //         SubSub task 2{} 50ms
    //     }52ms
    // }60ms
    @endcode

    By default we display to std::cout but you can set your own display function
    @code
        // For instance within maya console:
        _tracker.set_display_func(
            [](std::string msg){
                MGlobal::displayInfo(msg.c_str())
            } )
    @endcode

    Use the predefined macro to be sure time tracking code is not present in
    the final release:

    @code
        tbx_timer_push("my message");
        tbx_timer_pop();
    @encode
*/
class Time_tracker {
public:
    Time_tracker(bool enabled = true);


    // TODO: keep track of every Time_tracker instances created.
    // At desctruction if there are still messages to pop (user forgot to pop(),
    // exception occured, unexpected return of the function) then pop everything
    // up to the last instance created and signal the timer was prematurely poped()
    //~Time_tracker();

    /// By default timings are output with std::cout,
    /// but you can setup your own function 'print_func'. It could be
    /// std::cerr, a file etc.
    void set_display_func( std::function<void (std::string)> print_func ){
        _print_func = print_func;
    }

    void push(const std::string& msg);
    void pop();

    void set_enabled(bool enabled);

private:
    std::string space() const;

    bool _enabled;
    size_t _size_push;
    std::vector<tbx::Timer> _timers;
    //std::vector<std::string> _messages;
    std::string _msg;

    /// @brief Lambda function used to display a string
    ///
    /// by default ->
    /// @code
    /// void _display_func( std::string msge ) {
    ///     std::cout << msge << std::flush;
    /// }
    /// @endcode
    std::function<void (std::string)> _print_func;
};

// -----------------------------------------------------------------------------


}// END tbx Namespace ==========================================================

#if 1
static inline void tbx_timer_push(const std::string& msg){ tbx::g_timer.push(msg); }
static inline void tbx_timer_pop(){ tbx::g_timer.pop(); }
#else
#define tbx_timer_push(msge)
#define tbx_timer_pop()
#endif

#include "toolbox_stl/settings_end.hpp"

#endif // TOOLBOX_TIME_TRACKER_HPP
