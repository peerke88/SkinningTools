#pragma once

#include "toolbox_config/meta_headers/meta_math_cu.hpp"
#include "toolbox_config/tbx_assert.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

template <typename T> static inline T max(T a, T b){ return ((a > b) ? a : b); }
template <typename T> static inline T min(T a, T b){ return ((a < b) ? a : b); }

// -----------------------------------------------------------------------------

/// Compute numerically the inverse of f : R -> R within the range [xmin, xmax].
/// f must be monotonic. We use a dichotomy.
/// @param y : abscisa of f_inv
/// @param f : function to invert (f must be monotonic)
/// @param xmin, xmax : abscisa range used to perform the dychotomic search to
/// find y.
/// @param eps : threshold of precision to stop the dychotomic search
/// @return the value returned by f_inv( y ) (or the x corresponding to f(x) = y)
/// y must in [f(min), f(max)] otherwise result is undefined.
static inline
double f_inverse(double y, double (*f)(double x), double xmin, double xmax, double eps = 1e-5);

// -----------------------------------------------------------------------------

/// Another interface for inversing a 1D function
template<class Func, class Real> static inline
Real f_inverse_var(Real y,
                   const Func& func,
                   Real xmin,
                   Real xmax,
                   Real eps = (Real)1e-5)
{
    // Check we are within range [xmin, xmax]
#ifndef NDEBUG
    float a = func.f(xmin);
    float b = func.f(xmax);
    tbx_assert( min( max( a, b ), y ) == y );
#endif

    bool rising = func.f(xmax) > func.f(xmin);
    Real x0 = xmin;
    Real x1 = xmax;

    Real x_mid = x0;
    int acc = 0;
    while( std::abs(func.f(x_mid) - y) > eps )
    {
        if( acc++ > 1000) break; // avoid infinite loops

        x_mid = (x0+x1) * 0.5f;

        if ( !( (func.f(x_mid) > y) ^ (rising)) ) x1 = x_mid;
        else                                      x0 = x_mid;
    }

    return x_mid;
}


// -----------------------------------------------------------------------------

template<class Func, class Real>
static inline
Real eval_df(const Func& to_eval, Real x, Real eps = (Real)1e-5)
{
    return (to_eval.f(x+eps) + to_eval.f(x-eps)) / eps*2.;
}

// -----------------------------------------------------------------------------

/// @brief first order differentiation of a 1D func;
template<class Func, class Real>
struct Diff_f {

    Diff_f(const Func& f) : _func(f) { }

    Real f(Real x, const Real eps = (Real)1e5) const {
        return (_func.f(x + eps) - _func.f(x - eps)) / (Real(2.) * eps);
    }

    const Func& _func;
};

// -----------------------------------------------------------------------------

static inline
float clampf(float val, float min, float max)
{
    return fminf( max, fmaxf(val, min));
}

// -----------------------------------------------------------------------------

static inline
int clamp(int val, int min_v, int max_v)
{
    return min( max_v, max(val, min_v));
}

// -----------------------------------------------------------------------------

/// A simple integer power function
/// @return x^p
/// @note p must be positive
template<class T>
static inline
T ipow(T x, int p)
{
    tbx_assert(p >= 0);
    if (p == 0) return 1;
    if (p == 1) return x;
    return x * ipow(x, p-1);
}

// -----------------------------------------------------------------------------

/// A static version of the integral power
/// @return a^n
/// Usage: float result = ipow<n>( a );
template <int n> inline
float ipow(float a) {
    const float b = ipow<n/2>(a);
    return (n & 1) ? (a * b * b) : (b * b);
}

template <> inline float ipow<1>(float a){ return a;   }
template <> inline float ipow<0>(float  ){ return 1.f; }

// -----------------------------------------------------------------------------

/// A static version of the integral power
/// @return a^n
template <int n> inline
int ipow(int a) {
    const int b = ipow<n/2>(a);
    return (n & 1) ? (a * b * b) : (b * b);
}

template <> inline int ipow<1>(int a){ return a; }
template <> inline int ipow<0>(int  ){ return 1; }

// -----------------------------------------------------------------------------

/// @return factorial of 'x' i.e: factorial(x) == x * (x-1) * (x-2)* ... * 1
static inline int factorial(int x){
    int r = 1;
    for( int i = 1; i <= x; i++ )
        r = r * i;
    return r;
}

// -----------------------------------------------------------------------------

/// A function returning +1 if its argument is positive, -1 if negative and 0
/// if null, branchless.
template <typename T>
int sign(const T& val)
{
    return (T(0) < val) - (val < T(0));
}

// -----------------------------------------------------------------------------

inline float  to_radian(float  val){ return val *  float(M_PI/180.0); }
inline double to_radian(double val){ return val * double(M_PI/180.0); }

// -----------------------------------------------------------------------------

inline float  to_degree(float  val){ return val *  float(180.0/M_PI); }
inline double to_degree(double val){ return val * double(180.0/M_PI); }

}// END tbx ====================================================================

#include "toolbox_maths/settings_end.hpp"

#include "toolbox_maths/calculus.inl"

