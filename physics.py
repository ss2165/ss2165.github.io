import math

class ball():
	#3d spherical ball object, with mass, position vector, velocity vector and radius
	def __init__(self, mass, radius, x =0, y =0, xsp = 0, ysp = 0):
		self.mass = mass
		self.pos = vector3(x,y)
		self.vel = vector3(xsp,ysp)
		self.radius = radius
	def momentum(self):
	 	return self.vel*self.mass
	def move(self,dt):
		self.pos = self.pos + self.vel*dt

class vector3():
	#3D vector object
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
	def __sub__(self, other):
		return vector3(self.x-other.x, self.y-other.y, self.z-other.z)
	def __mul__(self, other):
		return vector3(other*self.x, other*self.y, other*self.z)
	def __rmul__(self, other):
	 	return vector3(other*self.x, other*self.y, other*self.z)
	def __div__(self, other):
		return vector3(self.x/other, self.y/other, self.z/other)
	def dot(self, other):
		#dots vector self and other
		return (self.x*other.x+self.y*other.y + self.z*other.z)
	def cross(self,other):
		#crosses vectors self and other
		return vector3(self.y*other.z- other.y*self.z, other.x*self.z-self.x*other.z, self.x*other.y -self.y*other.x)

	def __str__(self):
		return "({0.x}, {0.y}, {0.z})".format(self)

# def vector_add(a, b):
# 	#adds vectors a and b
# 	c = vector3(a.x+b.x, a.y+b.y, a.z+b.z)
# 	return c
# def vector_sub(a,b):
# 	#subtracts vector b from a
# 	c = vector3(a.x-b.x, a.y-b.y, a.z-b.z)
# 	return c
#
# def vector_dot(a,b):
# 	#dots vector a and b
# 	return (a.x*b.x+a.y*b.y + a.z*b.z)
# def vector_cross(a,b):
# 	#crosses vectors a and b
# 	return (a.y*b.z- b.y*a.z, b.x*a.z-a.x*b.z, a.x*b.y -a.y*b.x)

def collide(ball_1,ball_2, is_elastic):
	#elastically or inelastically collides balls 1 and 2
	posdif = ball_1.pos - ball_2.pos
	veldif = ball_1.vel - ball_2.vel
	summass = ball_1.mass + ball_2.mass

	if is_elastic:
		v1= ball_1.vel - posdif*(2*ball_2.mass/(summass))*(veldif.dot(posdif)/posdif.mag()**2)
		v2= ball_2.vel - posdif*(-2*ball_1.mass/(summass))*(veldif.dot(posdif)/posdif.mag()**2)
	else:
		v1 = zmf_vel(ball_1, ball_2)
		v2 = zmf_vel(ball_1, ball_2)

	ball_1.vel = v1
	ball_2.vel = v2

def zmf_speed(ball_1, ball_2):
	#centre of mass speed for two objects
	return (ball_1.mass*ball_1.vel.x + ball_2.mass*ball_2.vel.x)/(ball_1.mass+ball_2.mass)
def zmf_vel(ball_1, ball_2):
	#zero momentum frame velocity vector
	summass = ball_1.mass + ball_2.mass
	return (ball_1.vel*ball_1.mass + ball_2.vel*ball_2.mass)/summass

def dist(obj1, obj2):
	#distance between two vectors
	return math.sqrt((obj1.x-obj2.x)**2+(obj1.y-obj2.y)**2)

def collision_check(ball_1, ball_2):
	#checks if two balls have collided
	if dist(ball_1.pos, ball_2.pos) <= ball_1.radius + ball_2.radius:
		return True
	else:
		return False
