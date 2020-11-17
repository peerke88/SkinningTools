/*

QUATERNIONS
===========
Q47.  What are quaternions?
Q48.  How do quaternions relate to 3D animation?
Q49.  How do I calculate the conjugate of a quaternion?
Q50.  How do I calculate the inverse of a quaternion?
Q51.  How do I calculate the magnitude of a quaternion?
Q52.  How do I normalize a quaternion?
Q53.  How do I multiply two quaternions together?
Q54.  How do I convert a quaternion to a rotation matrix?
Q55.  How do I convert a rotation matrix to a quaternion?
Q56.  How do I convert a rotation axis and angle to a quaternion?
Q57.  How do I convert a quaternion to a rotation axis and angle?
Q58.  How do I convert spherical rotation angles to a quaternion?
Q59.  How do I convert a quaternion to spherical rotation angles?
Q60.  How do I convert Euler rotation angles to a quaternion?
Q61.  How do I use quaternions to perform linear interpolation between matrices?
Q62.  How do I use quaternions to perform cubic interpolation between matrices?
Q63.  How do I use quaternions to rotate a vector?


Q47. What are quaternions?
--------------------------
  Quaternions extend the concept of rotation in three dimensions to
  rotation in four dimensions. This avoids the problem of "gimbal-lock"
  and allows for the implementation of smooth and continuous rotation.
  In effect, they may be considered to add a additional rotation angle
  to spherical coordinates ie. Longitude, Latitude and Rotation angles
  A Quaternion is defined using four floating point values |x y z w|.
  These are calculated from the combination of the three coordinates
  of the rotation axis and the rotation angle.

Q48. How do quaternions relate to 3D animation?
-----------------------------------------------
  As mentioned before, Euler angles have the disadvantage of being
  susceptible to "Gimbal lock" where attempts to rotate an
  object fail to appear as expected, due to the order in which the
  rotations are performed.

  Quaternions are a solution to this problem. Instead of rotating an
  object through a series of successive rotations, quaternions allow
  the programmer to rotate an object through an arbitary rotation axis
  and angle.

  The rotation is still performed using matrix mathematics. However,
  instead of multiplying matrices together, quaternions representing
  the axii of rotation are multiplied together. The final resulting
  quaternion is then converted to the desired rotation matrix.
  Because the rotation axis is specifed as a unit direction vector,
  it may also be calculated through vector mathematics or from
  spherical coordinates ie (longitude/latitude).
  Quaternions offer another advantage in that they be interpolated.
  This allows for smooth and predictable rotation effects.

Q49. How do I calculate the conjugate of a quaternion?
------------------------------------------------------
  This can be achieved by reversing the polarity (or negating) the
  vector part of the quaternion, ie:

    Qr =  ( Qr.scalar, -Qr.vector )
  ----------------------------------------------------------------
  quaternion_conjugate( QUAT *qr, QUAT *qa )
    {
    qr -> qw =  qa -> qw;
    qr -> qx = -qa -> qx;
    qr -> qy = -qa -> qy;
    qr -> qz = -qa -> qz;
    }

Q50. How do I calculate the inverse of a quaternion?
----------------------------------------------------
  This is equivalent to calculating the conjugate of the quaternion,
  if the quaternion is normalized (or a unit quaternion).
  In all other cases, the magnitude of the inverse is 1/|q|.
  See Q49: How do I calculate the conjugate of a quaternion?

Q51. How do I calculate the magnitude of a quaternion?
------------------------------------------------------
  The magnitude of a quaternion is calculated by multiplying the
  quaternion with its conjugate ie:
              ------------
             /      --
  |Qr| =  \/     Qr.Qr
  This can be implemented as the following code sequence:
  -------------------------------------------------------------------
  QFLOAT quaternion_magnitude( QUAT *qa )
    {
    return( sqrt(qa->qw*qa->qw+
                 qa->qx*qa->qx+ qa->qy*qa->qy+qa->qz*qa->qz) )
    }

Q52. How do I normalize a quaternion?
-------------------------------------
  A quaternion can be normalized in a way similar to vectors. The
  magnitude of the quaternion is calculated first. Then both the
  scalar and vector part of the quaternion are divided by this value.
  A unit quaternion will always have a magnitude of 1.0

Q53. How do I multiply two quaternions together?
------------------------------------------------
  Given two quaternions Q1 and Q2, the goal is to calculate the
  combined rotation Qr:

    Qr = Q1.Q2

  This is achieved through the expression:

    Qr = Q1.Q2 = ( w1.w2 - v1.v2, w1.v2 + w2.v1 + v1 x v2 )

  where v1 = (x,y,z) of Q1
        w1 = (w)     of Q1
        v2 = (x,y,z) of Q2
        w2 = (w)     of Q2

  and both . and x are the standard vector dot and cross products.
  This can be implemented using the following code segment:
  ---------------------------------------------------
  quaternion_multiply( QUAT *qr, QUAT *qa, QUAT *qb )
    {
    qr.scalar = qa->scalar * qb->scalar - v3_dot( &qa->vector, &qb->vector );
    v3_cross(  &va, &qa->vector, &qb->vector );
    v3_scalef( &vb, &qa->vector, &qb->scalar );
    v3_scalef( &vc, &qb->vector, &qa->scalar );
    v3_add(    &va,         &va, &vb );
    v3_add(    &qr->vector, &va, &vc );
    quaternion_normalize( qr );
    }

  ---------------------------------------------------
  An optimization can also be made by rearranging to
    w = w1w2 - x1x2 - y1y2 - z1z2
    x = w1x2 + x1w2 + y1z2 - z1y2
    y = w1y2 + y1w2 + z1x2 - x1z2
    z = w1z2 + z1w2 + x1y2 - y1x2

Q54. How do I convert a quaternion to a rotation matrix?
--------------------------------------------------------
  Assuming that a quaternion has been created in the form:

    Q = |X Y Z W|

  Then the quaternion can then be converted into a 4x4 rotation
  matrix using the following expression (Warning: you might have to
  transpose this matrix if you (do not) follow the OpenGL order!):

         ¦        2     2                                      ¦
         ¦ 1 - (2Y  + 2Z )   2XY + 2ZW         2XZ - 2YW       ¦
         ¦                                                     ¦
         ¦                          2     2                    ¦
     M = ¦ 2XY - 2ZW         1 - (2X  + 2Z )   2YZ + 2XW       ¦
         ¦                                                     ¦
         ¦                                            2     2  ¦
         ¦ 2XZ + 2YW         2YZ - 2XW         1 - (2X  + 2Y ) ¦
         ¦                                                     ¦

  If a 4x4 matrix is required, then the bottom row and right-most column
  may be added.
  The matrix may be generated using the following expression:

    xx      = X * X;
    xy      = X * Y;
    xz      = X * Z;
    xw      = X * W;
    yy      = Y * Y;
    yz      = Y * Z;
    yw      = Y * W;
    zz      = Z * Z;
    zw      = Z * W;
    mat[0]  = 1 - 2 * ( yy + zz );
    mat[1]  =     2 * ( xy - zw );
    mat[2]  =     2 * ( xz + yw );
    mat[4]  =     2 * ( xy + zw );
    mat[5]  = 1 - 2 * ( xx + zz );
    mat[6]  =     2 * ( yz - xw );
    mat[8]  =     2 * ( xz - yw );
    mat[9]  =     2 * ( yz + xw );
    mat[10] = 1 - 2 * ( xx + yy );
    mat[3]  = mat[7] = mat[11] = mat[12] = mat[13] = mat[14] = 0;
    mat[15] = 1;

  The resulting matrix uses the following positions:

      ¦ mat[0]  mat[4] mat[ 8] mat[12] ¦
  M = ¦ mat[1]  mat[5] mat[ 9] mat[13] ¦
      ¦ mat[2]  mat[6] mat[10] mat[14] ¦
      ¦ mat[3]  mat[7] mat[11] mat[15] ¦

Q55. How do I convert a rotation matrix to a quaternion?
--------------------------------------------------------
  A rotation may be converted back to a quaternion through the use of
  the following algorithm:
  The process is performed in the following stages, which are as follows:

    Calculate the trace of the matrix T from the equation:

                2     2     2
      T = 4 - 4x  - 4y  - 4z

                 2    2    2
        = 4( 1 -x  - y  - z )

        = 1 + mat[0] + mat[5] + mat[10]


    If the trace of the matrix is greater than zero, then
    perform an "instant" calculation.
    Important note wrt. rouning errors:

    Test if ( T > 0.00000001 ) to avoid large distortions!

      S = sqrt(T) * 2;
      X = ( mat[9] - mat[6] ) / S;
      Y = ( mat[2] - mat[8] ) / S;
      Z = ( mat[4] - mat[1] ) / S;
      W = 0.25 * S;

    If the trace of the matrix is equal to zero then identify
    which major diagonal element has the greatest value.
    Depending on this, calculate the following:

    if ( mat[0] > mat[5] && mat[0] > mat[10] )  {   // Column 0:
        S  = sqrt( 1.0 + mat[0] - mat[5] - mat[10] ) * 2;
        X = 0.25 * S;
        Y = (mat[4] + mat[1] ) / S;
        Z = (mat[2] + mat[8] ) / S;
        W = (mat[9] - mat[6] ) / S;
    } else if ( mat[5] > mat[10] ) {            // Column 1:
        S  = sqrt( 1.0 + mat[5] - mat[0] - mat[10] ) * 2;
        X = (mat[4] + mat[1] ) / S;
        Y = 0.25 * S;
        Z = (mat[9] + mat[6] ) / S;
        W = (mat[2] - mat[8] ) / S;
    } else {                        // Column 2:
        S  = sqrt( 1.0 + mat[10] - mat[0] - mat[5] ) * 2;
        X = (mat[2] + mat[8] ) / S;
        Y = (mat[9] + mat[6] ) / S;
        Z = 0.25 * S;
        W = (mat[4] - mat[1] ) / S;
    }

     The quaternion is then defined as:
       Q = | X Y Z W |

Q56. How do I convert a rotation axis and angle to a quaternion?
----------------------------------------------------------------
  Given a rotation axis and angle, the following
  algorithm may be used to generate a quaternion:

    vector_normalize(axis);
    sin_a = sin( angle / 2 );
    cos_a = cos( angle / 2 );
    X    = axis -> x * sin_a;
    Y    = axis -> y * sin_a;
    Z    = axis -> z * sin_a;
    W    = cos_a;

  It is necessary to normalize the quaternion in case any values are
  very close to zero.

Q57. How do I convert a quaternion to a rotation axis and angle?
----------------------------------------------------------------
  A quaternion can be converted back to a rotation axis and angle
  using the following algorithm:

    quaternion_normalize( |X,Y,Z,W| );
    cos_a = W;
    angle = acos( cos_a ) * 2;
    sin_a = sqrt( 1.0 - cos_a * cos_a );
    if ( fabs( sin_a ) < 0.0005 ) sin_a = 1;
    axis -> x = X / sin_a;
    axis -> y = Y / sin_a;
    axis -> z = Z / sin_a;

Q58. How do I convert spherical rotation angles to a quaternion?
----------------------------------------------------------------
  A rotation axis itself may be defined using spherical coordinates
  (latitude and longitude) and a rotation angle
  In this case, the quaternion can be calculated as follows:

    sin_a    = sin( angle / 2 )
    cos_a    = cos( angle / 2 )
    sin_lat  = sin( latitude )
    cos_lat  = cos( latitude )
    sin_long = sin( longitude )
    cos_long = cos( longitude )
    X       = sin_a * cos_lat * sin_long
    Y       = sin_a * sin_lat
    Z       = sin_a * sin_lat * cos_long
    W       = cos_a

  WARNING: There might be a problem in this code.
  An alternative is the code snipped given in [Q60: How
  do I convert Euler rotation angles to a quaternion?"].

Q59. How do I convert a quaternion to spherical rotation angles?
----------------------------------------------------------------
  A quaternion can be converted to spherical coordinates by extending
  the conversion process:

    cos_a  = W;
    sin_a  = sqrt( 1.0 - cos_a * cos_a );
    angle  = acos( cos_a ) * 2;
    if ( fabs( sin_angle ) < 0.0005 ) sin_a = 1;
    tx = X / sin_a;
    ty = Y / sin_a;
    tz = Z / sin_a;
    latitude = -asin( ty );
    if ( tx * tx + tz * tz < 0.0005 )
      longitude   = 0;
    else
       longitude  = atan2( tx, tz );
    if ( longitude < 0 )
      longitude += 360.0;

  WARNING: In this code might still be a problem.
  Please let me know what it is and how to fix this.

Q60. How do I convert Euler rotation angles to a quaternion?
-------------------------------------------------------------------
  Converting Euler rotation angles to quaterions can be achieved through
  the use of quaternion multiplication. Each rotation angle is converted
  to an axis-angle pair, with the axis corresponding to one of the
  Euclidean axii. The axis-angle pairs are converted to quaternions and
  multiplied together. The final quaternion is the desired result.


  The following code segment demonstrates this:

  quaternion_from_euler( QUATERNION *q, VFLOAT ax, VFLOAT ay, VFLOAT az )
  {
    VECTOR3 vx = { 1, 0, 0 }, vy = { 0, 1, 0 }, vz = { 0, 0, 1 };
    QUATERNION qx, qy, qz, qt;
    quaternion_from_axisangle( qx, &vx, rx );
    quaternion_from_axisangle( qy, &vy, ry );
    quaternion_from_axisangle( qz, &vz, rz );
    quaternion_multiply( &qt, &qx, &qy );
    quaternion_multiply( &q,  &qt, &qz );
  }

  The following more or less comes from:
  http://vered.rose.utoronto.ca/people/david_dir/GEMS/GEMS.html

   //Pitch->X axis, Yaw->Y axis, Roll->Z axis
    Quaternion::Quaternion(float fPitch, float fYaw, float fRoll)
    {
       const float fSinPitch(sin(fPitch*0.5F));
       const float fCosPitch(cos(fPitch*0.5F));
       const float fSinYaw(sin(fYaw*0.5F));
       const float fCosYaw(cos(fYaw*0.5F));
       const float fSinRoll(sin(fRoll*0.5F));
       const float fCosRoll(cos(fRoll*0.5F));
       const float fCosPitchCosYaw(fCosPitch*fCosYaw);
       const float fSinPitchSinYaw(fSinPitch*fSinYaw);
       X = fSinRoll * fCosPitchCosYaw     - fCosRoll * fSinPitchSinYaw;
       Y = fCosRoll * fSinPitch * fCosYaw + fSinRoll * fCosPitch * fSinYaw;
       Z = fCosRoll * fCosPitch * fSinYaw - fSinRoll * fSinPitch * fCosYaw;
       W = fCosRoll * fCosPitchCosYaw     + fSinRoll * fSinPitchSinYaw;
    }

  The following might also work:
  QUATERNION qx = { cos(pitch/2f), sin(pitch/2f), 0, 0 }
  QUATERNION qy = { cos(yaw/2f), 0, sin(yaw/2f), 0 }
  QUATERNION qz = { cos(roll/2f), 0, 0, sin(roll/2f) }
  quaternion_multiply( &qt, &qx, &qy );
  quaternion_multiply( &q,  &qt, &qz );

  In Java looks like this:

  public static void setQ( Quat4f q, float pitch, float yaw, float roll )
  {
      Quat4f qx = new Quat4f((float) Math.cos(pitch/2f),
                 (float) Math.sin(pitch/2f), 0, 0);
      Quat4f qy = new Quat4f((float) Math.cos(yaw/2f), 0,
                 (float) Math.sin(yaw/2f),0);
      Quat4f qz = new Quat4f((float) Math.cos(roll/2f), 0, 0,
                 (float) Math.sin(roll/2f) );
      Quat4f qt = new Quat4f();
      qt.set( qx );
      qt.mul( qy );
      qt.mul( qz );
      q.set( qt );
  }

Q61. How do I use quaternions to perform linear interpolation between matrices?
-------------------------------------------------------------------------------
  For many animation applications, it is necessary to interpolate
  between two rotation positions of a given object. These positions may
  have been specified using keyframe animation or inverse kinematics.
  Using either method, at least two rotation matrices must be known, and
  the desired goal is to interpolate between them. The two matrices are
  referred to as the starting and finish matrices( MS and MF).
  Using linear interpolation, the interpolated rotation matrix is
  generated using a blending equation with the parameter T, which
  ranges from 0.0 to 1.0.

  At T=0, the interpolated matrix is equal to the starting matrix.
  At T=1, the interpolated matrix is equal to the finishing matrix.
  Then the interpolated rotation matrix (MI) is specified as:

    MI = F( MS, MF, T )

  where F is a blending function.
  The first stage in interpolating between the two matrices is to
  determine the rotation matrix that will convert MS to MF.
  This is achieved using the following expression:

          -1
    T = Ms  . Mf

  where Ms is the start matrix,
        Mf is the finish matrix,
    and T is the intermediate matrix.

  The next stage is to convert this matrix into a rotation axis and
  angle. This is achieved by converting the matrix into a quaternion
  and finally into the required rotation axis and angle.
  In order to generate the interpolated rotation matrix, it is only
  necessary to scale the rotation angle and convert this angle and
  the rotation axis back into a rotation matrix.

  Using a 4x4 matrix library, this is as follows:

    m4_transpose(    mt, ms );                // Inverse
    m4_mult(         ms, mt, mb );            // Rotation matrix
    m4_to_axisangle( ms, axis, angle );       // Rotation axis/angle
    for ( t = 0; t < 1.0; t += 0.05 )
      {
      m4_from_axisangle( mi, axis, angle * t ); // Final interpolation
      ... whatever ...
      }

  where t is the interpolation factor ranging from 0.0 to 1.0

Q62. How do I use quaternions to perform cubic interpolation between matrices?
------------------------------------------------------------------------------
  For some applications, it may not be convenient or possible to use linear
  interpolation for animation purposes. In this case, cubic interpolation
  is another alternative.
  In order to use cubic interpolation, at least four rotation matrices must
  be known.

  Each of these is then converted into a set of spherical rotations
  via quaternions and spherical rotation angles (ie. longitude, latitude
  and rotation angle).

  These are then multiplied with the base matrix for a Cardinal spline
  curve. This interpolation matrix can then be used to determine the
  intermediate spherical rotation angles.
  Once the interpolated coordinates are known (latitude, longitude and
  rotation angle), the interpolated rotation matrix can then be generated
  through the conversion to quaternions.

  Using a 4x4 matrix library, the algorithm is as follows:

    for ( n = 0; n < 4; n++ )
      m4_to_spherical( mat[n], &v_sph[n] );   // Spherical coordinates
    m4_multspline( m_cardinal, v_sph, v_interp ); // Interpolation vector
    ...
    v3_cubic( v_pos, v_interp, t );           // Interpolation
    m4_from_spherical( m_rot, v_pos );        // Back to a matrix

Q63. How do I use quaternions to rotate a vector?
------------------------------------------------------------------------------
  A rather elegant way to rotate a vector using a quaternion directly
  is the following (qr being the rotation quaternion):

                       -1
       v' = qr * v * qr

  This can easily be realised and is most likely faster then the transformation
  using a rotation matrix.
*/

#pragma once

#include "toolbox_maths/transfo.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/** @brief Quaternions implementation to express rotation

  Quaternions are mathematics objects usefull to represent rotation about the
  origin. A quaternion is similar to complex number (a + ib) but in higher
  dimension : q = w + i*x + j*y + k*z where i^2 = j^2 = k^2 = ijk = -1.
  w is the scalar part and (x, y, z) the vector part. The intuition is that
  w represent the amount of rotation around a vector axis which can be
  extracted from the vector part (i,j,k).

  The advantages of dual quaternion over other rotation representations
  are the followings:
  @li it avoids "gimbal-lock" phenomena present with euler angles matrices.
  @li it is slightly faster than matrices.
  @li rounding error by combining successively several quaternions to do
  successive rotations are accumulated in the angle and not in the axis
  direction (unlike matrices).

  You can construct a dual quaternion from a transformation matrix of type
  Transfo and rotate a point or a vector with the method 'rotate()'
  it is also possible to compose several rotation by multiplying quaternions
  together with the overload operator (*)

  Quaternion are also used with dual quaternions to represent a rotation plus a
  translation

  @see Dual_quat
*/
class Quat {
    public:

    // -------------------------------------------------------------------------
    /// @name Constructors
    // -------------------------------------------------------------------------

    /// Default constructor : build a zero rotation.
     inline
    Quat()
    {
        _coeff[0] = 1.f;
        _coeff[1] = 0.f; _coeff[2] = 0.f; _coeff[3] = 0.f;
    }

    /// Copy constructor
     inline
    Quat(const Quat& q){
        _coeff[0] = q.w();
        _coeff[1] = q.i(); _coeff[2] = q.j(); _coeff[3] = q.k();
    }

    /// directly fill the quaternion
     inline
    Quat(float w, float i, float j, float k){
        _coeff[0] = w;
        _coeff[1] = i; _coeff[2] = j; _coeff[3] = k;
    }

    /// Construct the quaternion from the transformation matrix 't'
    /// Translation of 't' is ignored as quaternions can't represent it
     inline
    Quat(const Transfo& t)
    {

        float X, Y, Z, W;

        // Supposedly this version of the routine is slightly more robust.
        float r22 = t(2,2);
        if (r22 <= 0.0f)  // x^2 + y^2 >= z^2 + w^2
        {
            float dif10 = t(1,1) - t(0,0);
            float omr22 = 1.0f - r22;
            if (dif10 <= 0.0f)  // x^2 >= y^2
            {
                float four_x_sqr = omr22 - dif10;
                float inv4x = (0.5f) / sqrt(four_x_sqr);
                X = four_x_sqr*inv4x;
                Y = (t(0,1) + t(1,0)) * inv4x;
                Z = (t(0,2) + t(2,0)) * inv4x;
                W = (t(1,2) - t(2,1)) * inv4x;
            }
            else  // y^2 >= x^2
            {
                float four_y_sqr = omr22 + dif10;
                float inv4y = ((float)0.5) / sqrt(four_y_sqr);
                X = (t(0,1) + t(1,0)) * inv4y;
                Y = four_y_sqr * inv4y;
                Z = (t(1,2) + t(2,1)) * inv4y;
                W = (t(2,0) - t(0,2)) * inv4y;
            }
        }
        else  // z^2 + w^2 >= x^2 + y^2
        {
            float sum10 = t(1,1) + t(0,0);
            float opr22 = (float)1 + r22;
            if (sum10 <= (float)0)  // z^2 >= w^2
            {
                float four_z_sqr = opr22 - sum10;
                float inv4z = ((float)0.5) / sqrt(four_z_sqr);
                X = (t(0,2) + t(2,0)) * inv4z;
                Y = (t(1,2) + t(2,1)) * inv4z;
                Z = four_z_sqr * inv4z;
                W = (t(0,1) - t(1,0)) * inv4z;
            }
            else  // w^2 >= z^2
            {
                float four_w_sqr = opr22 + sum10;
                float inv4w = ((float)0.5) / sqrt(four_w_sqr);
                X = (t(1,2) - t(2,1)) * inv4w;
                Y = (t(2,0) - t(0,2)) * inv4w;
                Z = (t(0,1) - t(1,0)) * inv4w;
                W = four_w_sqr * inv4w;
            }
        }
        _coeff[0] = W; _coeff[1] = -X; _coeff[2] = -Y; _coeff[3] = -Z;
    }

    /// Construct the quaternion from the a rotation axis 'axis' and the angle
    /// 'angle' in radians
     inline
    static Quat from_axis_angle(const Vec3& axis, float angle)
    {
        Quat q;
        Vec3 vec_axis = axis.normalized();
        float sin_a = sin( angle * 0.5f );
        float cos_a = cos( angle * 0.5f );
        q._coeff[0]    = cos_a;
        q._coeff[1]    = vec_axis.x * sin_a;
        q._coeff[2]    = vec_axis.y * sin_a;
        q._coeff[3]    = vec_axis.z * sin_a;
        // It is necessary to normalize the quaternion in case any values are
        // very close to zero.
        q.normalize();
        return q;
    }

    // -------------------------------------------------------------------------
    /// @name Methods
    // -------------------------------------------------------------------------

    /// The conjugate of a quaternion is the inverse rotation
    /// (when the quaternion is normalized
     inline
    Quat conjugate() const
    {
        return Quat(  _coeff[0], -_coeff[1],
                     -_coeff[2], -_coeff[3]);
    }

    // TODO: Construct the quaternion from the rotation axis 'vec' and the
    // angle 'angle'
    // Quat(const Vec3& vec, float angle)

    /// Do the rotation of vector 'v' with the quaternion
     inline
    Vec3 rotate(const Vec3& v) const
    {

        // The conventionnal way to rotate a vector
        /*
        Quat tmp = *this;
        tmp.normalize();
        // Compute the quaternion inverse with
        Quat inv = tmp.conjugate();
        // Compute q * v * inv; in order to rotate the vector v
        // to do so v must be expressed as the quaternion q(0, v.x, v.y, v.z)
        return (Vec3)(*this * Quat(0, v) * inv);
        */

        // An optimized way to compute rotation
        Vec3 q_vec = get_vec_part();
        return v + (q_vec*2.f).cross( q_vec.cross(v) + v*_coeff[0] );
    }

    /// Do the rotation of point 'p' with the quaternion
     inline
    Point3 rotate(const Point3& p) const
    {
        Vec3 v = rotate((Vec3)p);
        return Point3(v.x, v.y, v.z);
    }

    /// Convert the quaternion to a rotation matrix
    /// @warning don't forget to normalize it before conversion
     inline
    Mat3 to_matrix3()
    {
        float W = _coeff[0], X = -_coeff[1], Y = -_coeff[2], Z = -_coeff[3];
        float xx = X * X, xy = X * Y, xz = X * Z, xw = X * W;
        float yy = Y * Y, yz = Y * Z, yw = Y * W, zz = Z * Z;
        float zw = Z * W;
        Mat3 mat = Mat3(
                    1.f - 2.f * (yy + zz),      2.f * (xy + zw),       2.f * (xz - yw),
                          2.f * (xy - zw),1.f - 2.f * (xx + zz),       2.f * (yz + xw),
                          2.f * (xz + yw),      2.f * (yz - xw), 1.f - 2.f * (xx + yy)
                    );

        return mat;
    }



    /// Convert quaternion to the equivalent (axis, angle) rotation
    // TODO: code untested....
     inline
    float to_axis_angle(Vec3& axis)
    {
        Quat q = *this;
        /// coeff[w:0], coeff[i:X:1], coeff[j:Y:2], coeff[k:Z:3]
        //quaternion_normalize( |X,Y,Z,W| );
        //cos_a = W;
        //angle = acos( cos_a ) * 2;
        //sin_a = sqrt( 1.0 - cos_a * cos_a );
        //if ( fabs( sin_a ) < 0.0005 ) sin_a = 1;
        //axis -> x = X / sin_a;
        //axis -> y = Y / sin_a;
        //axis -> z = Z / sin_a;
        q.normalize();
        float cos_a = _coeff[0];
        float angle = acos( cos_a ) * 2.0f;
        float sin_a = sqrtf( 1.0f - cos_a * cos_a );
        if( fabs( sin_a ) < 0.0005f )
            sin_a = 1.0f;
        axis.x = _coeff[1] / sin_a;
        axis.y = _coeff[2] / sin_a;
        axis.z = _coeff[3] / sin_a;
        return angle;
    }

     inline
    Vec3 get_vec_part() const
    {
        return Vec3(_coeff[1], _coeff[2], _coeff[3]);
    }

     inline
    float norm() const
    {
        return sqrt(_coeff[0]*_coeff[0] +
                    _coeff[1]*_coeff[1] +
                    _coeff[2]*_coeff[2] +
                    _coeff[3]*_coeff[3]);
    }

     inline
    float normalize()
    {
        float n = norm();
        _coeff[0] /= n;
        _coeff[1] /= n;
        _coeff[2] /= n;
        _coeff[3] /= n;
        return n;
    }

     inline
    float dot(const Quat& q){
        return w() * q.w() + i() * q.i() + j() * q.j() + k() * q.k();
    }

     inline float w() const { return _coeff[0]; }
     inline float i() const { return _coeff[1]; }
     inline float j() const { return _coeff[2]; }
     inline float k() const { return _coeff[3]; }

    // -------------------------------------------------------------------------
    /// @name Operators
    // -------------------------------------------------------------------------

     inline
    Quat operator/ (float scalar) const
    {
        Quat q = *this;
        q._coeff[0] /= scalar;
        q._coeff[1] /= scalar;
        q._coeff[2] /= scalar;
        q._coeff[3] /= scalar;
        return q;
    }

     inline
    Quat operator/= (float scalar){
        _coeff[0] /= scalar;
        _coeff[1] /= scalar;
        _coeff[2] /= scalar;
        _coeff[3] /= scalar;
        return *this;
    }

     inline
    Quat operator* (const Quat& q) const
    {
         return Quat(
         _coeff[0]*q._coeff[0] - _coeff[1]*q._coeff[1] - _coeff[2]*q._coeff[2] - _coeff[3]*q._coeff[3],
         _coeff[0]*q._coeff[1] + _coeff[1]*q._coeff[0] + _coeff[2]*q._coeff[3] - _coeff[3]*q._coeff[2],
         _coeff[0]*q._coeff[2] + _coeff[2]*q._coeff[0] + _coeff[3]*q._coeff[1] - _coeff[1]*q._coeff[3],
         _coeff[0]*q._coeff[3] + _coeff[3]*q._coeff[0] + _coeff[1]*q._coeff[2] - _coeff[2]*q._coeff[1]);
    }

     inline
    Quat operator* (float scalar) const
    {
        return Quat(_coeff[0] * scalar,
                    _coeff[1] * scalar,
                    _coeff[2] * scalar,
                    _coeff[3] * scalar);
    }

     inline
    Quat operator+ (const Quat& q) const
    {
         return Quat(_coeff[0] + q._coeff[0],
                     _coeff[1] + q._coeff[1],
                     _coeff[2] + q._coeff[2],
                     _coeff[3] + q._coeff[3]);
    }

    /// Get vector part
     inline
    operator Vec3 () const{
        return Vec3(_coeff[1], _coeff[2], _coeff[3]);
    }

    /// Get scalar part
     inline
    operator float () const{
        return _coeff[0];
    }

    // -------------------------------------------------------------------------
    /// @name Attributes
    // -------------------------------------------------------------------------

    /// coeff[0], coeff[1], coeff[2], coeff[3] respectively
    /// w, i, j, k coefficients or W, X, Y, Z as noted in the F.A.Q
    float _coeff[4];

};

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"


