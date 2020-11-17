#include "toolbox_config/char_array.hpp"

#include <string>

// =============================================================================
namespace tbx {
// =============================================================================

static inline
Str to_char_array(const std::string& str) {
    return Str(str.c_str());
}

// -----------------------------------------------------------------------------

static inline
char* alloc_string(const char* str)
{
    std::string temp(str);
    char* ptr = new char[temp.size()+1];
    for(unsigned i = 0; i < temp.length(); ++i)
        ptr[i] = temp[i];

    ptr[temp.length()] = '\0';
    return ptr;
}

// -----------------------------------------------------------------------------

Str::Str(int                v) { _str = alloc_string( std::to_string(v).c_str()); }
Str::Str(unsigned           v) { _str = alloc_string( std::to_string(v).c_str()); }
Str::Str(float              v) { _str = alloc_string( std::to_string(v).c_str()); }
Str::Str(double             v) { _str = alloc_string( std::to_string(v).c_str()); }
Str::Str(long               v) { _str = alloc_string( std::to_string(v).c_str()); }
Str::Str(unsigned long      v) { _str = alloc_string( std::to_string(v).c_str()); }
Str::Str(unsigned long long v) { _str = alloc_string( std::to_string(v).c_str()); }

// -----------------------------------------------------------------------------

Str::Str(const char* str)
{
    _str = alloc_string(str);
}

// -----------------------------------------------------------------------------

Str::Str(const Str& copy)
{
   _str = alloc_string(copy._str);
}

// -----------------------------------------------------------------------------

Str::Str()
    : _str(nullptr)
{

}

// -----------------------------------------------------------------------------

Str::~Str()
{
    delete[] _str;
}

// -----------------------------------------------------------------------------

Str& Str::operator=(const Str& copy) {
    if( _str != nullptr)
        delete[] _str;
    _str = alloc_string( copy );
    return *this;
}

// -----------------------------------------------------------------------------

Str Str::operator + ( int value ) const{
    return this->operator+(Str(value));
}

// -----------------------------------------------------------------------------

Str Str::operator + (const Str& other ) const{
    return to_char_array(std::string(*this) + std::string(other));
}

Str Str::operator + (const char* other ) const{
    return to_char_array(std::string(*this) + std::string(other));
}

Str operator+(const char* lhs, const Str& rhs){
    return to_char_array(std::string(lhs) + std::string(rhs));
}

}// END Namespace ==============================================================

