import math



class ball():
    """3d spherical ball object, with mass, position vector, velocity vector and radius"""

    def __init__(self, mass, radius, x =0, y =0, xsp = 0, ysp = 0):
        self.mass = mass
        self.pos = vector3(x,y)
        self.vel = vector3(xsp,ysp)
        self.radius = radius

    def move(self,dt):
        self.pos = self.pos + self.vel*dt

    def zmf_vel(self, other):
        #zero momentum frame velocity vector
        summass = self.mass + other.mass
        return (self.vel*self.mass + other.vel*other.mass)/summass

    def momentum(self):
        return self.vel*self.mass

    def collide(self, other, is_elastic):
        #elastically or inelastically collides balls 1 and 2
        posdif = self.pos - other.pos
        veldif = self.vel - other.vel
        summass = self.mass + other.mass

        if is_elastic:
            v1= self.vel - posdif*(2*other.mass/(summass))*(veldif.dot(posdif)/posdif.mag()**2)
            v2= other.vel - posdif*(-2*self.mass/(summass))*(veldif.dot(posdif)/posdif.mag()**2)
        else:
            v1 = self.zmf_vel(other)
            v2 = self.zmf_vel(other)

        self.vel = v1
        other.vel = v2

    def collision_check(self, other):
        return ((self.pos - other.pos).mag() <= self.radius + other.radius)

class vector3():
    """3D vector object"""

    def __init__(self,x, y, z= 0):
        self.x = x
        self.y = y
        self.z = z

    def mag(self):
        #magnitude
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def phi(self):
        #polar angle in radians, between 0 and pi
        return math.acos((self- vector3(0,0, self.z)).norm().dot(vector3(1, 0, 0)))
    def theta(self):
        #3d azimuthal angle
        if self.mag() == 0:
            return 0
        else:
            return math.acos(self.z/self.mag())
    def multi(self, a):
        #scalar multiple
        return vector3(a*self.x, a*self.y, a*self.z)
    def norm(self):
        #normalised vector
        mag = self.mag()
        if mag == 0:
            return self
        else:
            return vector3(self.x/mag, self.y/mag, self.z/mag)

    def phi_rotate(self, angle, origin):
        #returns vector with phi changed by angle in anti clockwise direction
        diff= self - origin
        sin = math.sin(angle)
        cos = math.cos(angle)
        new = vector3(cos*diff.x - sin*diff.y, +sin*diff.x + cos*diff.y, diff.z)
        return new + origin

    def __add__(self, other):
        return vector3(self.x+other.x, self.y+other.y, self.z+other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        return vector3(self.x-other.x, self.y-other.y, self.z-other.z)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, other):
        return vector3(other*self.x, other*self.y, other*self.z)

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        self.z *= other
        return self

    def __rmul__(self, other):
        return vector3(other*self.x, other*self.y, other*self.z)

    def __div__(self, other):
        return vector3(self.x/other, self.y/other, self.z/other)

    def __idiv__(self, other):
        self.x /= other
        self.y /= other
        self.z /= other
        return self

    def dot(self, other):
        #dots vector self and other
        return (self.x*other.x+self.y*other.y + self.z*other.z)

    def cross(self,other):
        #crosses vectors self and other
        return vector3(self.y*other.z- other.y*self.z, other.x*self.z-self.x*other.z, self.x*other.y -self.y*other.x)

    def __str__(self):
        return "({0.x}, {0.y}, {0.z})".format(self)

def runge_kutta4(y, f, t, dt):
    """Return next iteration of function y with derivative f with timestep dt using Runge-Kutta 4th order"""
    k1 = f(t, y)
    k2 = f(t + dt/2, y + k1*dt/2)
    k3 = f(t + dt/2, y + k2*dt/2)
    k4 = f(t + dt, y + dt*k3)
    y = y + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)
    return y

def num_bisection(function, a, b, iterations):
    iterations  = int(math.sqrt(iterations**2))
    if a>b:
        a, b = b, a
    c = (a+b)/2.0
    for letter in (a, b, c):
        if function(letter) == 0:
            return letter

    for i in range(iterations-1):
        if function(c)*function(a)>0:
            a = c
        else:
            b = c
        c = (a+b)/2.0
    return c

def num_linear(function, a, b, iterations):
    iterations  = int(math.sqrt(iterations**2))
    if a>b:
        a, b = b, a

    for i in range(iterations):
        fa = function(a)
        fb = function(b)
        c =  a - (b-a)/(fb/fa -1)
        new = function(c)

        if new == 0:
            return c
        elif new*function(a)>0:
            a = c
        else:
            b = c
    return c

def num_newton(function, derivative, guess, iterations):
    """Newton-Raphson numerical method.

    Return root of function using it's first derivative with initial guess, over given iterations."""

    c = guess
    for i in range(iterations):
        fc = function(c)
        if fc ==0:
            return c
        c -= fc/derivative(c)
    return c

def num_secant(function, guess1, guess2, iterations, tol = 0.000001):
    """Secant numerical method.

    Return root of function with initial guess1 and guess2, over given iterations."""

    for i in range(iterations):
        print guess1
        f1 = function(guess1)
        f2 = function(guess2)

        if f1 ==0 or -tol <= guess1 - guess2 <= tol:
            return guess1
        elif f2 ==0:
            return guess2
        # elif f1 == f2:
        #     return None

        c = guess1 - f1*(guess1-guess2)/(f1-f2)
        guess2 = guess1
        guess1 = c
    return guess1
