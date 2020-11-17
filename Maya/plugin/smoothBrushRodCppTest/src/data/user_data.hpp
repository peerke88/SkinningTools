#ifndef USER_DATA_HPP
#define USER_DATA_HPP

#include <toolbox_stl/memory.hpp>
#include <toolbox_stl/map.hpp>
#include <toolbox_maya/utils/maya_error.hpp>

// =============================================================================
namespace skin_brush {
// =============================================================================

struct User_data {
    typedef int Data_id;

    class Data {
    public:
        virtual ~Data(){ }
    };

    template <class T>
    const T* get_data(Data_id id) const
    {
        auto it = _user_data.find(id);
        if( it != _user_data.end() )
        {
            const tbx::Uptr<Data>& data = it->second;
            if( data )
                return dynamic_cast<const T*>( data.get() );
        }

        return nullptr;
    }

    template <class T>
    T* get_data(Data_id id)
    {
        auto it = _user_data.find(id);
        if( it != _user_data.end() )
        {
            tbx::Uptr<Data>& data = it->second;
            if( data )
                return dynamic_cast<T*>( data.get() );
        }

        return nullptr;
    }

    void push_data(Uptr<Data> ptr, Data_id id)
    {
        // You should not push twice the same data id;
        mayaAssert( !tbx::exists(_user_data, id) );
        _user_data[id] = std::move(ptr);
    }

private:
    std::map<Data_id, tbx::Uptr<Data> > _user_data;
};


}// END skin_brush Namespace ========================================


#endif // USER_DATA_HPP
