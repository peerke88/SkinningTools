#ifndef CHAR_ARRAY_HPP
#define CHAR_ARRAY_HPP

// =============================================================================
namespace tbx {
// =============================================================================

///@brief light weight representation of a string without std::string header
struct Str {


    Str(const char* str);
    Str(const Str& copy);
    Str();

    Str(int v);
    Str(unsigned);
    Str(float v);
    Str(double v);
    Str(long v);
    Str(unsigned long v);
    Str(unsigned long long v);

    ~Str();

    const char* c_str() const { return  _str; }

    // auto cast to const char*
    operator const char*() const { return _str; }
    // Copy
    Str& operator=(const Str& copy);


    /*
    Str&	operator += ( const Str& other );
    Str&	operator += ( const char* other );

    Str&	operator += ( double other );
    Str&	operator += ( int other );
    Str&	operator += ( unsigned int other );
    Str&	operator += ( float other );

    Str&	operator =  ( const char* other );
    Str&	operator =  ( double value );
    bool		operator == ( const Str& other ) const;
    bool		operator == ( const char* other ) const;
    bool		operator != ( const Str& other ) const;
    bool		operator != ( const char* other ) const;
    Str operator + ( double value ) const;
    Str operator + ( float value ) const;
    */
    Str operator + ( int value ) const;


    // Concat
    Str operator + (const Str& other ) const;
    Str operator + (const char* other ) const;
    friend Str operator+(const char*, const Str& );

public:
    char* _str;
};


}// END Namespace ==============================================================

#endif // CHAR_ARRAY_HPP
