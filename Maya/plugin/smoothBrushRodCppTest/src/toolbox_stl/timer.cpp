#include "toolbox_stl/timer.hpp"

#if 0
    #include <boost/timer.hpp>
#else

#include <ctime>
#include <limits>

// =============================================================================
namespace boost {
// =============================================================================

//  A timer object measures elapsed time.

//  It is recommended that implementations measure wall clock rather than CPU
//  time since the intended use is performance measurement on systems where
//  total elapsed time is more important than just process or CPU time.

//  Warnings: The maximum measurable elapsed time may well be only 596.5+ hours
//  due to implementation limitations.  The accuracy of timings depends on the
//  accuracy of timing information provided by the underlying platform, and
//  this varies a great deal from platform to platform.

class timer {
public:
    /// postcondition: elapsed()==0
    timer() { _start_time = std::clock(); }

    /// post: elapsed()==0
    void restart() { _start_time = std::clock(); }

    /// @return elapsed time in seconds
    double elapsed() const {
        return  double(std::clock() - _start_time) / CLOCKS_PER_SEC;
    }

    /// @return estimated maximum value for elapsed()
    double elapsed_max() const
    {
        // Portability warning: elapsed_max() may return too high a value
        // on systems where std::clock_t overflows or resets
        // at surprising values.
        return (double((std::numeric_limits<std::clock_t>::max)())
                - double(_start_time)) / double(CLOCKS_PER_SEC);
    }

    /// @return minimum value for elapsed()
    double elapsed_min() const {
        return double(1)/double(CLOCKS_PER_SEC);
    }

private:
    std::clock_t _start_time;
};

} // namespace boost ===========================================================
#endif

// =============================================================================
namespace tbx {
// =============================================================================

Timer::Timer() : _boost_timer( new boost::timer() )
{
}

// -----------------------------------------------------------------------------

Timer::~Timer()
{
    delete _boost_timer;
}

// -----------------------------------------------------------------------------

Timer::Timer(const Timer& t){
    _elapsed_time = t._elapsed_time;
    _boost_timer  = new boost::timer();
}

// -----------------------------------------------------------------------------

Timer& Timer::operator=(const Timer& t){
    _elapsed_time = t._elapsed_time;
    return *this;
}

// -----------------------------------------------------------------------------

void Timer::start() {
    _boost_timer->restart();
}

// -----------------------------------------------------------------------------

double Timer::elapsed() {
    _elapsed_time = _boost_timer->elapsed();
    return _elapsed_time;
}

// -----------------------------------------------------------------------------

void Timer::reset() {
    _elapsed_time = 0.;
    _boost_timer->restart();
}

// -----------------------------------------------------------------------------

double Timer::get_value(){
    return _elapsed_time;
}

}// END tbx NAMESPACE ==========================================================
