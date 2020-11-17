#include <toolbox_maths/calculus.hpp>

// =============================================================================
namespace tbx {
// =============================================================================

double f_inverse(double y,
                 double (*f)(double x),
                 double xmin,
                 double xmax,
                 double eps)
{
    // Check we are within range [xmin, xmax]
    tbx_assert( min( max( f(xmin), f(xmax) ), y ) == y );

    bool rising = f(xmax) > f(xmin);
    double x0 = xmin;
    double x1 = xmax;

    double x_mid = x0;
    int acc = 0;
    while( std::abs(f(x_mid) - y) > eps )
    {
        if( acc++ > 1000) break; // avoid infinite loops

        x_mid = (x0+x1) * 0.5f;

        if ( !( (f(x_mid) > y) ^ (rising)) ) x1 = x_mid;
        else                                 x0 = x_mid;
    }

    return x_mid;
}

}// END IBL ====================================================================
