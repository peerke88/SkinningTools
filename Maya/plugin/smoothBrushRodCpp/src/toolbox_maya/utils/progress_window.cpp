#include "toolbox_maya/utils/progress_window.hpp"

#include <toolbox_maya/utils/maya_error.hpp>
#include <maya/MProgressWindow.h>
#include <maya/MString.h>

// =============================================================================
namespace tbx_maya {
// =============================================================================

Progress_window::Progress_window()
    : _delay(CLOCKS_PER_SEC*1)
{
}

// -----------------------------------------------------------------------------

Progress_window::Progress_window(const std::string& win_title,
                                 int max_range,
                                 bool interuptable)
    : _delay(CLOCKS_PER_SEC*1)
    , _interruptable( interuptable )
{
    start(win_title,max_range);
}

// -----------------------------------------------------------------------------

Progress_window::~Progress_window(void)
{
    stop();
}

// -----------------------------------------------------------------------------

void Progress_window::start(const std::string& win_title, int max_range)
{
    _max_range = max_range;
    _win_title = win_title;

    _start = clock();
    _progress = 0;
    _is_init = false;

}

// -----------------------------------------------------------------------------

void Progress_window::stop()
{
    if (_is_init) {
        mayaCheck( MProgressWindow::endProgress() );
        _is_init = false;
    }
}

// -----------------------------------------------------------------------------

void Progress_window::add_progess(int increment)
{
    if( clock() > _start + Progress_window::_delay ) {
        show();
    }

    if (_is_init)
        mayaCheck( MProgressWindow::advanceProgress(increment) );
    else
        _progress += increment;

}

// -----------------------------------------------------------------------------

void Progress_window::show()
{
    if(!_is_init )
    {
        if (MProgressWindow::reserve())
        {
            _is_init = true;
            mayaCheck( MProgressWindow::setProgressRange(0, _max_range) );
            mayaCheck( MProgressWindow::setTitle( _win_title.c_str() ) );
            mayaCheck( MProgressWindow::setProgressStatus(_win_title.c_str()) );
            mayaCheck( MProgressWindow::setInterruptable(_interruptable) );
            mayaCheck( MProgressWindow::setProgress(_progress) );
            mayaCheck( MProgressWindow::startProgress() );
        }
    }
}

// -----------------------------------------------------------------------------

void Progress_window::reset() {
    if (_is_init)
        mayaCheck( MProgressWindow::setProgress(0) );
}

// -----------------------------------------------------------------------------

const bool Progress_window::is_canceled() const
{
    return _is_init && MProgressWindow::isCancelled();
}

}// END tbx_maya Namespace =====================================================
