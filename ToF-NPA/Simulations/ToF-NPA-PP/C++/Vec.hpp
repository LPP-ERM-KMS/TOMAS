#ifndef VEC_HPP
#define VEC_HPP

using namespace std;
#include <vector>

class Vec {
    // The components of this three dimensional vector
    double _x;
    double _y;
    double _z;

public:
    Vec() {_x =0; _y=0; _z=0;} // Initiates as a vector of length zero
    Vec(double x, double y, double z)
        { _x = x; _y = y; _z = z;}

    double x() const { return _x; }
    double y() const { return _y; }
    double z() const { return _z; }

    Vec& operator+=(Vec v) {
        _x += v._x;
        _y += v._y;
        _z += v._z;
        return *this;
    }
    Vec& operator-=(Vec v) {
        _x -= v._x;
        _y -= v._y;
        _z -= v._z;
        return *this;
    }
    Vec& operator*=(double s) {
        _x *= s;
        _y *= s;
        _z *= s;
        return *this;
    }
    Vec& operator/=(double s) {
        _x /= s;
        _y /= s;
        _z /= s;
        return *this;
    }

    double norm() const { return sqrt(_x*_x + _y*_y + _z*_z); }
    double norm2() const { return _x*_x + _y*_y + _z*_z; }
    double norm3() const { double r = sqrt(_x*_x + _y*_y + _z*_z); return r*r*r; }
};

void print(Vec a)
{ cout << a.x() << ' ' << a.y() << ' ' << a.z() << endl; }

// operations between two vectors
Vec operator+(Vec a, Vec b) { return a += b; }
Vec operator-(Vec a, Vec b) { return a -= b; }

// operations between a vector and a scalar
Vec operator*(Vec a, double s) { return a *= s; }
Vec operator*(double s, Vec b) { return b *= s; }
Vec operator/(Vec a, double s) { return a /= s; }


vector<Vec> operator+(vector<Vec> a, vector<Vec> b) {
    if (a.size() != b.size()) {cout << "error: the two vectors should have an equal size";}
    for (int i=0; i<a.size(); ++i) {a[i] += b[i];}
    return a;
}

vector<Vec> operator-(vector<Vec> a, vector<Vec> b) {
    if (a.size() != b.size()) {cout << "error: the two vectors should have an equal size";}
    for (int i=0; i<a.size(); ++i) {a[i] -= b[i];}
    return a;
}

vector<Vec> operator*(vector<Vec> a, const double& b) {
    for (int i=0; i<a.size(); ++i) {a[i] *= b;}
    return a;
}

vector<Vec> operator*( const double& b, vector<Vec> a) {
    for (int i=0; i<a.size(); ++i) {a[i] *= b;}
    return a;
}

vector<Vec> operator/(vector<Vec> a, const double& b) {
    for (int i=0; i<a.size(); ++i) {a[i] /= b;}
    return a;
}

vector<Vec> print(vector<Vec> a) {
    for (int i=0; i<a.size(); ++i) {print(a[i]);}
    return vector<Vec>();
}

#endif //VEC_HPP
