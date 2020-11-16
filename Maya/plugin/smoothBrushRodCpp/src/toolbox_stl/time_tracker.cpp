#include "toolbox_stl/time_tracker.hpp"

#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_config/tbx_printf.hpp"


// =============================================================================
namespace tbx {
// =============================================================================

Time_tracker g_timer(false);

// -----------------------------------------------------------------------------

namespace local {
    // If true display timings any time we pop().
    // If false display timings only for the last pop()
    static bool s_real_time_trace_on = false;
}

// -----------------------------------------------------------------------------

Time_tracker::Time_tracker(bool enabled): _size_push(0), _msg("")
{
    _enabled = enabled;
    _print_func = [](std::string str) { tbx_print( str.c_str() ); };
}

// -----------------------------------------------------------------------------

std::string Time_tracker::space() const {
    std::string space = "";
    for(unsigned i = 0; i < (_timers.size()-1); ++i){
        space += "      ";
    }
    return space;
}

void Time_tracker::set_enabled(bool enabled)
{
    _enabled = enabled;
}

// -----------------------------------------------------------------------------

void Time_tracker::push(const std::string& msg){
    if(_enabled)
    {
        _timers.push_back(tbx::Timer());
        std::string str = ("\n") + space() + msg + ("{");
        _msg += str;

        if(local::s_real_time_trace_on)
            _print_func( std::string(("push: ")) + space() + msg + ("{")  );

        _timers.back().start();

        _size_push = _timers.size();
    }
}

// -----------------------------------------------------------------------------

void Time_tracker::pop(){
    if(_enabled)
    {
        tbx_assert(_timers.size() != 0);
        double t = _timers.back().elapsed() * 1000.0;
        bool leaf = _size_push == _timers.size();

        std::string str;
        if(!leaf) str += "\n";
        if(!leaf) str += space();
        str += ("}") + std::to_string(t) + (" ms");

        if(local::s_real_time_trace_on)
            _print_func( std::string(("pop:  ")) + space() + "" + std::to_string(t) + (" ms") );

        _msg += str;

        _timers.pop_back();

        if(_timers.size() == 0)
        {
            std::string str = ("\n"
                                 "------------\n"
                                 "Time digest:\n"
                                 "------------");
            //MGlobal::displayInfo( (str + _msg).c_str() );
            _print_func(str + _msg + "\n");
            _msg = "";
        }
    }
}


}// END tbxNamespace ===========================================================

