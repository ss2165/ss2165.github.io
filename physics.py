# Copyright 2015 Seyon Sivarajah
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Anvil service module for physics objects and methods.

Classes:
vector3 -- 3D vector type with each component as an attribute.
complex2 -- complex number type.
ball -- 3D ball with vector attributes and associated methods.
point_source -- subclass of ball which radiates spherical waves.

Functions:
exp2 -- complex exponential function.
disc_convolve -- discrete convolution of two functions.
dfft -- discrete fast fourier transform (inverse not working).
disc_fourier -- calculate normal discrete fourier transform.
disc_inv_fourier -- calculate normal inverse discrete fourier transform.
runge_kutta4 -- numerical integration using 4th order Runge-Kutta method.
num_bisection -- find root of function using numerical bisection method.
num_linear -- find root of function using linear interpolation.
num_newton -- find root of function using Newton-Raphson method.
num_secant -- find root of function using secant method.
diff -- numerical differentiation.
diff_5 -- 5th order numerical differentiation.
"""
import math


class ball():
    """3d spherical ball object, with mass, position vector, velocity vector and radius"""

    def __init__(self, mass, radius, x =0, y =0, xsp = 0, ysp = 0):
        self.mass = mass
        self.pos = vector3(x,y)
        self.vel = vector3(xsp,ysp)
        self.radius = radius

    def move(self,dt):
        #move at current constant velocity
        self.pos = self.pos + self.vel*dt

    def zmf_vel(self, other):
        #zero momentum frame velocity vector
        summass = self.mass + other.mass
        return (self.vel*self.mass + other.vel*other.mass)/summass

    def momentum(self):
        #return momentum vector
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
        #check if two balls are touching or overlap
        return ((self.pos - other.pos).mag() <= self.radius + other.radius)

class point_source(ball):
    """Subclass of ball which radiates spherical wavefronts."""
    #speed of light, default speed.
    c= 3e8

    def __init__(self, speed = c, frequency = None, wavelength = None,radius = 0.1, x =0, y =0, xsp = 0, ysp = 0):
        """Initialize
        Attributes:
        speed (float) -- wavespeed.
        frequency (float) -- wave frequency.
        wavelength (float) -- wavelength.
        radius (float) -- source radius.
        x (float) -- position x component.
        y (float) -- position y component.
        xsp (float) -- velocity x component.
        ysp (float) -- velocity y component.
        """
        ball.__init__(self, mass=0.1,radius =radius, x =x, y =y, xsp =xsp, ysp =ysp)

        #if only two of speed, wavelength or frequency are provided, calculate the third
        if frequency !=None:
            if wavelength !=None:
                self.speed = frequency * wavelength
                self.frequency = frequency
                self.wavelength = wavelength
            self.speed = speed
            self.frequency = frequency
            self.wavelength = speed/frequency
        elif wavelength !=None:
            self.speed = speed
            self.wavelength = wavelength
            self.frequency = speed/wavelength
        else:
            raise "Provide two out of three of speed, wavelength or frequency"

        self.wavefront = 0
        self.mousedown = False
    def __mul__(self, other):
        return self

    def radiate(self, dt):
        #move wavefront
        self.wavefront += self.speed*dt


class vector3():
    """3D vector object with each component as an attribute and associated methods.

    Attributes:
    x (float) -- x component.
    y (float) -- y component.
    z (float) -- z component.

    Methods:
    mag -- magnitude of vector.
    phi -- angle in xy plane (angle in cylindrical polar coordinates).
    theta -- angle from z axis (azimuthal angle).
    multi -- (deprecated) multiply vector by scalar.
    norm -- normalised vector.
    phi_rotate -- rotate vector by angle.
    dot -- dot product.
    cross -- cross product.
    str -- formatted string of vector.
    """

    def __init__(self,x, y, z= 0):
        self.x = x
        self.y = y
        self.z = z

    def mag(self):
        """Return magnitude."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def phi(self):
        """Return polar angle in radians, between -pi and pi."""
        return math.atan2(self.y, self.x)
    def theta(self):
        """Return azimuthal angle."""
        if self.mag() == 0:
            return 0
        else:
            xymag = vector3(self.x, self.y).mag()
            return math.atan2(xymag, self.z)
    def multi(self, a):
        """deprecated scalar multiple."""
        return vector3(a*self.x, a*self.y, a*self.z)
    def norm(self):
        """Return normalised vector."""
        mag = self.mag()
        if mag == 0:
            return self
        else:
            return vector3(self.x/mag, self.y/mag, self.z/mag)

    def phi_rotate(self, angle, origin):
        """Return vector rotated in xy plane by angle in anti clockwise direction"""
        diff= self - origin
        sin = math.sin(angle)
        cos = math.cos(angle)
        new = vector3(cos*diff.x - sin*diff.y, +sin*diff.x + cos*diff.y, diff.z)
        return new + origin

    def __add__(self, other):
        """Add two vectors."""
        return vector3(self.x+other.x, self.y+other.y, self.z+other.z)

    def __iadd__(self, other):
        """Add to vector."""
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        """Subtract two vectors."""
        return vector3(self.x-other.x, self.y-other.y, self.z-other.z)

    def __isub__(self, other):
        """Subtract from vector."""
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, other):
        """Multiply by scalar."""
        return vector3(other*self.x, other*self.y, other*self.z)

    def __imul__(self, other):
        """Multiply by scalar in place."""
        self.x *= other
        self.y *= other
        self.z *= other
        return self

    def __rmul__(self, other):
        """Multiply by scalar."""
        return vector3(other*self.x, other*self.y, other*self.z)

    def __div__(self, other):
        """Divide by scalar."""
        return vector3(self.x/other, self.y/other, self.z/other)

    def __idiv__(self, other):
        """Divide by scalar."""
        self.x /= other
        self.y /= other
        self.z /= other
        return self

    def dot(self, other):
        """Return dot product of two vectors."""
        return (self.x*other.x+self.y*other.y + self.z*other.z)

    def cross(self,other):
        """Return cross product of two vectors."""
        return vector3(self.y*other.z- other.y*self.z, other.x*self.z-self.x*other.z, self.x*other.y -self.y*other.x)

    def __str__(self):
        """Return formatted string of vector."""
        return "({0.x}, {0.y}, {0.z})".format(self)

class complex2():
    """Complex number with real and imaginary attributes. VERY EARLY STAGES, UNTESTED."""

    def __init__(self,re, im):
        if not isinstance(re, (int, long, float)) or not isinstance(im, (int, long, float)):
            raise "Arguments are not numbers"
        self.re = re
        self.im = im

    def mag(self):
        """Return Magnitude."""
        return math.sqrt(self.re**2 + self.im**2)

    def phase(self):
        """Return polar angle in radians, between -pi and pi."""
        return math.atan2(self.im, self.re)

    def polar(self):
        return (self.mag(), self.phase())
    def phi_rotate(self, angle, origin):
        #returns vector with phi changed by angle in anti clockwise direction
        diff= self - origin
        sin = math.sin(angle)
        cos = math.cos(angle)
        new = complex2(cos*diff.x - sin*diff.y, +sin*diff.x + cos*diff.y)
        return new + origin

    def __abs__(self):
        return math.sqrt(self.re**2 + self.im**2)
    def __add__(self, other):
        if isinstance(other, complex2):
            return complex2(self.re+other.re, self.im+other.im)
        else:
            return complex2(self.re+other, self.im)
    def __iadd__(self, other):
        if isinstance(other, complex2):
            self.re += other.re
            self.im += other.im
        else:
            self.re += other
        return self

    def __sub__(self, other):
        if isinstance(other, complex2):
            return complex2(self.re-other.re, self.im-other.im)
        else:
            return complex2(self.re-other, self.im)

    def __isub__(self, other):
        if isinstance(other, complex2):
            self.re -= other.re
            self.im -= other.im
        else:
            self.re -= other
        return self

    def __mul__(self, other):
        if isinstance(other, complex2):
            return complex2(other.re*self.re - other.im*self.im, other.re*self.im + other.im*self.re)
        else:
            return complex2(other*self.re, other*self.im)

    def __imul__(self, other):
        if isinstance(other, complex2):
            self =  complex2(other.re*self.re - other.im*self.im, other.re*self.im + other.im*self.re)
        else:
            self.re *= other
            self.im *= other
        return self

    def __rmul__(self, other):
        return complex2(other*self.re, other*self.im)

    def __div__(self, other):
        if not isinstance(other, complex2):
            return complex2(self.re/other, self.im/other)
        else:
            return self

    def __idiv__(self, other):
        if not isinstance(other, complex2):
            self.re /= other
            self.im /= other
            return self
        else:
            return self

    def __str__(self):
        return "{0.re} + {0.im}i".format(self)

def exp2(x):
    #return complex exponential, if not complex use normal exponential function.
    if isinstance(x, complex2):
        return math.exp(x.re)*complex2(math.cos(x.im), math.sin(x.im))
    else:
        return complex2(math.exp(x), 0)

def disc_convolve(f, g):
    """Return discrete convolution list of two discrete function iterables f and g"""

    result = []
    for i in range(len(f)):
        sums = 0
        for j in range(len(g)):
            if i>=j:
                sums += f[i-j]*g[j]
        result.append(sums)
    return result

def dfft(x, N, s=1, inverse = False):
    """Discrete fast fourier transform. Uses complex2 type."""

    inv = -1 if inverse else 1

    if N == 1:
        if isinstance(x[0], complex2):
            return x
        else:
            return [complex2(x[0],0)]
    else:
        X = dfft(x, N/2,  s=2*s, inverse = inverse) + dfft(x[s:], N/2, s =2*s, inverse = inverse)
        i = complex2(0, 1)
        for k in range(N/2):
            t = X[k]
            r = inv*exp2(-2*inv*math.pi*i*k/N)*X[k+N/2]
            X[k] = (t + r)
            X[k+N/2] = (t - r)
        if inverse and s == 1:
            X = [x/N for x in X]
        return X

def disc_fourier(x):
    """Discrete fourier transform of x."""
    X  = []
    i = complex2(0, 1)
    N = len(x)
    for k in range(N):
        result = complex2(0,0)
        for n in range(N):
            result += x[n]*exp2(-2*math.pi*i*n*k/N)
        X.append(result)

    return X

def disc_inv_fourier(X):
    """Inverse discrete fourier transform."""
    x  = []
    i = complex2(0, 1)
    N = len(X)
    for n in range(N):
        result = complex2(0,0)
        for k in range(N):
            result += X[k]*exp2(2*math.pi*i*n*k/N)
        x.append(result.re/N)

    return x

def runge_kutta4(y, f, t, dt):
    """Return next iteration of function y with derivative f with timestep dt using Runge-Kutta 4th order."""
    k1 = f(t, y)
    k2 = f(t + dt/2, y + k1*dt/2)
    k3 = f(t + dt/2, y + k2*dt/2)
    k4 = f(t + dt, y + dt*k3)
    y = y + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)
    return y

def num_bisection(function, a, b, iterations):
    """Find root of function with guesses a,b over iterations using bisection."""
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
    """Find root of function with guesses a,b over iterations using linear interpolation."""
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

def diff(values):
    """Differentiate values numerically."""
    res = []
    for i in range(len(values)-1):
        x1,y1  = values[i]
        x2, y2 = values[i+1]
        if x2 != x1:
            res.append((x1, (y2-y1)/(x2-x1)))

    return res

def diff_5(values):
    """Differentiate values numerically using 5th order method."""
    res = []
    for i in range(2,len(values)-2):
        h = values[i+1][0] - values[i][0]
        y1= values[i+1][1]
        y2= values[i+2][1]
        y_1= values[i-1][1]
        y_2= values[i-2][1]
        if h != 0:
            res.append((values[i][0], (-y2 + 8*y1 - 8*y_1 + y_2)/(12*h)))

    return res
