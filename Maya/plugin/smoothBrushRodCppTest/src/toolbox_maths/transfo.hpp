#pragma once

#include "toolbox_maths/math_typedefs.hpp"
#include "toolbox_maths/vector3.hpp"
#include "toolbox_maths/vector4.hpp"
#include "toolbox_maths/matrix3x3.hpp"
#include "toolbox_maths/point3.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/**
  @name Transfo
  @brief Handling geometric transformations with a 4x4 matrix

  Read carrefully, this class is not just a 4x4 matrix but aims to efficiently
  handle affine transformations, there are special cases you must be aware of:

  Some methods will assume the 4x4 matrix represent an affine transformations,
  these methods will have undefined behavior if Transfo isn't an affine
  transformation (For instance a 4x4 matrix that represents a
  "perspective projection" is not an affine transformation)

  Memory layout
  =============

  The 4x4 matrix is stored linearly with an array of 16 floats.
  The matrix is layout with <b> rows first (i.e row major) </b>
  (note: OpenGl is column major)

  Vector multiplication
  =====================

  For convenience one can multiply Transfo against Point3 or Vec3 under certain
  conditions.

  A Point3 miss is forth homegenous component (1.0f). When multiplying, the
  translation part (last column) will be added (as points are expected to translate)
  however the last row is ignored:
  @code
  // Multiplies against the upper 3x3 matrix and add "Transfo(...).get_translation()"
  Point3 v = Transfo(...) * Point3(1.f); // Valid *only when* Transfo is affine
  @endcode

  A Vec3 miss is forth homegenous component (0.0f). When multiplying, the
  translation part (last column) will be *ignored* (as vectors
  are expected to not translate)
  however the last row is ignored:
  @code
  // All expressions below multiply against the sub Transfo(..).get_mat3()
  // and ignore the translation part of the transfo
  Vec3 v = Transfo(...) * Vec3(1.2f);
  Vec3 v = Transfo(..).mult_as_vec( Vec3(1.2f))
  @endcode

  You can reinterpret a Vec3 as a point to perform the translation:
  @code
  Vec3 v = Transfo(...) * Point(Vec3(1.2f));
  Vec3 v = Vec3(Transfo(...) * Point3(Vec3(1.2f)));
  Vec3 v = Vec3( Transfo(...) * Vec4(Vec3(1.2f), 1.0f) );
  Vec3 v = Transfo(...).mult_as_point(Vec3(1.2f));
  @endcode

  A Vec4 is not a special case and behaves as a full blown matrix multiplication.

  Projection
  ==========

  If one wants to project a point this can be done manually with a Vec4 with
  the last homegenous component set to one:
  @code
  Vec3 point;
  Vec4 h_point = Transfo(projection) * Vec4(point, 1.f);
  point = Vec3( h_point.x, h_point.y, h_point.z ) / h_point.z;
  @endcode

  Which is equivalent to use Transfo::project() with a Point3:
  @code
  Point3 result = Transfo(projection).project( Point3(a_point) );
  @endcode

  Inversion
  =========

  Two methods can be used for inverting the matrix:
  @li Transfo::fast_inverse() : assume the Transfo is affine and only inverts
  the 3x3 matrix and take the opposite of the translation component.
  @li Transfo::full_invert() : full 4x4 inversion.
  works with any matrix but slower

  @see Mat3 Vec3 Point3 Point Vec4
*/
template<class Real>
class AMatrix4x4 /* Affine matrix*/ {
    /// Linear matrix storage with <b> rows first (i.e row major) </b>
    /// Using this with OpenGL can be done by transposing first:
    /// @code
    ///     Transfo tr;
    ///     // OpenGL is column major !
    ///     glMultMatrixf( (GLfloat*)( tr.transpose() ) );
    /// @endcode
    Real m[16];
public:

    // -------------------------------------------------------------------------
    /// @name Constructors
    // -------------------------------------------------------------------------

    /// Default constructor set values to identity.
     inline
    AMatrix4x4() {
        m[ 0] = Real(1); m[ 1] = Real(0); m[ 2] = Real(0); m[ 3] = Real(0);
        m[ 4] = Real(0); m[ 5] = Real(1); m[ 6] = Real(0); m[ 7] = Real(0);
        m[ 8] = Real(0); m[ 9] = Real(0); m[10] = Real(1); m[11] = Real(0);
        m[12] = Real(0); m[13] = Real(0); m[14] = Real(0); m[15] = Real(1);
    }

    
    template<class In_real>
    inline explicit
    AMatrix4x4( const AMatrix4x4<In_real>& mat ) {
        m[ 0] = Real(mat[ 0]); m[ 1] = Real(mat[ 1]); m[ 2] = Real(mat[ 2]); m[ 3] = Real(mat[ 3]);
        m[ 4] = Real(mat[ 4]); m[ 5] = Real(mat[ 5]); m[ 6] = Real(mat[ 6]); m[ 7] = Real(mat[ 7]);
        m[ 8] = Real(mat[ 8]); m[ 9] = Real(mat[ 9]); m[10] = Real(mat[10]); m[11] = Real(mat[11]);
        m[12] = Real(mat[12]); m[13] = Real(mat[13]); m[14] = Real(mat[14]); m[15] = Real(mat[15]);
    }

    /// Fill the transform matrix with predefined values.
    
    inline AMatrix4x4(Real a00, Real a01, Real a02, Real a03,
                      Real a10, Real a11, Real a12, Real a13,
                      Real a20, Real a21, Real a22, Real a23,
                      Real a30, Real a31, Real a32, Real a33);

    static inline AMatrix4x4 from_array_ptr( const Real* row_major_ptr){
        AMatrix4x4 result;
        for(int i = 0; i < 16; ++i)
            result.m[i] = row_major_ptr[i];
        return result;
    }

    static AMatrix4x4 from_gl_ptr( const Real* column_major_ptr){
        return AMatrix4x4::from_array_ptr(column_major_ptr).transpose();
    }

    /// Builds a transform from the rotation given by matrix @param x.
    /// (translation set to zero)
    
    explicit inline
    AMatrix4x4(const Matrix3x3<Real>& x);

    /// Builds a transform from the rotation given by matrix @param x and the
    /// translation by vector @param v.
     inline
    AMatrix4x4(const Matrix3x3<Real>& x, const Vector3<Real>& v);

    /// Builds a transform from the transation given by vector @param v.
     explicit inline AMatrix4x4(const Vector3<Real>& v);

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

     inline Vector3<Real> x() const; ///< @return first matrix column
     inline Vector3<Real> y() const; ///< @return second matrix column
     inline Vector3<Real> z() const; ///< @return third matrix column

     inline Matrix3x3<Real> get_mat3() const;

    /// get translation part of the matrix (fourth column)
     inline Vector3<Real> get_translation() const { return Vector3<Real>(m[3], m[7], m[11]); }

     inline void set_x(const Vector3<Real>& x); ///< @return first matrix column
     inline void set_y(const Vector3<Real>& y);
     inline void set_z(const Vector3<Real>& z);

     inline void set_translation(const Vector3<Real>& tr);

     inline void set_translation(const Point3_base<Real>& tr){
        set_translation( Vector3<Real>(tr) );
    }

     inline void copy_translation(const AMatrix4x4& tr);

     inline void set_mat3(const Matrix3x3<Real>& x);

    // -------------------------------------------------------------------------
    /// @name Operators
    /// @note A special attention has to be made regarding the multiplication
    /// operators. The operator is overloaded differently wether you use
    /// Vec3 or Point3. This is because the homogenous part is not represented.
    /// Vec3 will ignore the translation part of the matrix (we assume w=0).
    /// Or must be converted to Vec4.
    /// Point3 are multiplied against the matrix translation part (we assume w=1).
    /// When projecting a point you will
    /// need to use the method 'project()' or Vec4
    // -------------------------------------------------------------------------

    /// Multiply against the sub Mat3x3.
    /// The translation part of the transformation is ignored (as expected
    /// for a vector 3)
    /// you may use Vec4 for a full multiplication or mult_as_point()
    /// @warning undefined behavior if 'this' is not an affine transformation
    
    inline Vector3<Real> mult_as_point(const Vector3<Real>& v) const;

    /// Multiply against the sub Mat3x3 and add the translation part of the
    /// matrix
    /// @warning undefined behavior if 'this' is not an affine transformation
    
    inline Point3_base<Real> mult_as_vec(const Point3_base<Real>& v) const;

    /// Multiply against the sub Mat3x3.
    /// The translation part of the transformation is ignored (as expected
    /// for a vector 3)
    /// you may use Vec4 for a full multiplication or mult_as_point()
     inline Vector3<Real> operator*(const Vector3<Real>&) const;


    /// Multiply against the sub Mat3x3 and add the translation part of the
    /// matrix. Transfo(..) * Point3(..) equivalent to Transfo(..) * Vec4(point3, 1.0)
    /// @warning undefined behavior if 'this' is not an affine transformation
     inline Point3_base<Real> operator*(const Point3_base<Real>& v) const;

    /// Multiply against the sub Mat3x3 and add the translation part of the
    /// matrix. Useful to temporarly consider a Vec3 as a Point without the need
    /// to convert back to Vec3.
    /// @warning undefined behavior if 'this' is not an affine transformation
    /// @code
    /// Vec3 v(.., .., ..);
    /// v = Transfo(..) * Point(v): // Transform v as a point.
    /// @endcode
     inline Vector3<Real> operator*(const Point_vec3<Real>& v) const;

    /// Full matrix multiplication against the Vec4
     inline Vector4<Real> operator*(const Vector4<Real>& v) const;

    /// Multiply 'v' by the matrix and do the perspective division
    
    inline Point3_base<Real> project(const Point3_base<Real>& v) const;

    
    inline AMatrix4x4<Real> operator*(const AMatrix4x4<Real>& t) const ;

    
    inline AMatrix4x4<Real>& operator*=(const AMatrix4x4<Real>& t);


    
    inline AMatrix4x4<Real> operator*(Real x) const;

    
    inline AMatrix4x4<Real> operator+(const AMatrix4x4<Real>& t) const;

    
    inline AMatrix4x4<Real>& operator+=(const AMatrix4x4<Real>& t);

    
    inline AMatrix4x4<Real> operator-(const AMatrix4x4<Real>& t) const;

    
    inline AMatrix4x4<Real>& operator-=(const AMatrix4x4<Real>& t);

    /// Two dimensionnal access
     inline
    Real& operator() (int i, int j) { return m[i*4+j]; }

     inline
    const Real& operator() (int i, int j) const { return m[i*4+j]; }

    /// One dimensionnal access (row major) i < 16
     inline       Real& operator[](int i)       { return m[i]; }
     inline const Real& operator[](int i) const { return m[i]; }

    // TODO: FIXME: the conversion to float* is too dangerous and should be forbiden
    // only data() should be allowed (same for Mat3())
    /// Conversion returns the memory address of the matrix.
    /// Very convenient to pass a Transfo pointer as a parameter to OpenGL:
    /// @code
    /// Transfo mat;
    /// glGetFloatv(GL_PROJECTION_MATRIX, mat);
    /// mat = mat.Transpose(); // Cuz OpenGl is column major and we are row major
    /// @endcode
     explicit operator const Real*() const = delete; // { return data(); }

    /// Conversion returns the memory address of the vector. (Non const version)
      explicit operator Real*() = delete; // { return data(); }

           Real* data()       { return m; }
     const Real* data() const { return m; }

    // -------------------------------------------------------------------------
    /// @name Getters
    // -------------------------------------------------------------------------


    
    inline AMatrix4x4<Real> transpose() const;

    /// Fast inversion of the Transformation matrix. To accelerate computation
    /// we consider that the matrix only represents affine Transformations
    /// such as rotation, scaling, translation, shear... Basically you can
    /// use this procedure only if the last row is equal to (0, 0, 0, 1)
    /// @warning undefined behavior if 'this' is not an affine transformation
    /// don't use this procedure to invert a projection matrix or
    /// anything that is not an affine transformation. Use #full_invert() instead.
    /// @see full_invert()
    
    inline AMatrix4x4<Real> fast_inverse() const;

    
    inline Real det() const;

    /// Full inversion of the Transformation matrix. No assumption is made about
    /// the 4x4 matrix to optimize inversion. if the Transformation is
    /// not affine you MUST use this procedure to invert the matrix. For
    /// instance perspective projection can't use the fast_inverse() procedure
    /// @see fast_inverse()
    
    inline AMatrix4x4<Real> full_inverse() const;

    /// @return the matrix with normalized x, y, z column vectors
    /// (basically eliminates scale factors of the matrix)
    
    inline AMatrix4x4<Real> normalized() const;

    /// Check if the vectors representing the frame are orthogonals.
    /// @warning Don't mix up this with orthogonal matrices.
    
    inline bool is_frame_ortho(Real eps = 0.0001) const;

    inline
    void print() const;

    /*
    inline friend
    std::ostream& operator<< ( std::ostream& ofs, const AMatrix4x4<Real>& tr );
    */

    // -------------------------------------------------------------------------
    /// @name Static transformation constructors (translation/rotation/scale)
    // -------------------------------------------------------------------------

    
    static inline AMatrix4x4<Real> translate(Real dx, Real dy, Real dz);

    
    static inline AMatrix4x4<Real> translate(const Vector3<Real>& v);

    
    static inline AMatrix4x4<Real> scale(Real sx, Real sy, Real sz);

    
    static inline AMatrix4x4<Real> scale(const Vector3<Real>& v);

    /// Build a uniform scaling matrix on x,y,z.
    
    static inline AMatrix4x4<Real> scale(Real s);

    /// @return the scale matrix given scale factors in 'v' and
    /// scale origin 'center'
    
    static inline AMatrix4x4<Real> scale(const Vector3<Real>& center, const Vector3<Real>& v);

    /// @return the uniform scale matrix given a scale factor 's' and
    /// scale origin 'center'
    
    static inline AMatrix4x4<Real> scale(const Vector3<Real>& center, Real s);

    
    static inline
    AMatrix4x4<Real> rotate(
            const Vector3<Real>& center,
            const Vector3<Real>& axis,
            Real radian_angle,
            const Matrix3x3<Real>& frame);

    /// @return the rotation matrix given an 'axis' rotation 'center' and
    /// 'angle' in radian
    
    static inline
    AMatrix4x4<Real> rotate(
            const Vector3<Real>& center,
            const Vector3<Real>& axis,
            Real radian_angle);


    /// build a rotation matrix around the origin.
    /// @param axis : the <b> normalized </b> axis of rotation
    /// @param radian_angle : rotation's angle in radian
    
    static inline AMatrix4x4<Real> rotate(const Vector3<Real>& axis, Real radian_angle);


    /// @return 4x4 identity matrix
    
    static inline AMatrix4x4<Real> identity();

    /// @return matrix full of zeros
    
    static inline AMatrix4x4<Real> null();

    /// Given a origin 'org' and a axis 'x_axis' generate the corresponding
    /// 3D frame. Meaning the columns for z and y axis will be
    /// computed to be orthogonal to 'x_axis'.
    
    static inline
    AMatrix4x4<Real> coordinate_system(const Vector3<Real>& org, const Vector3<Real>& x_axis);
};

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/transfo.inl"

#include "toolbox_maths/settings_end.hpp"
