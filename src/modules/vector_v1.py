from math import sqrt, atan2, sin, cos, pi

class Vector:
    def __init__(self, x, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self._norm = None
        self._direction = None

    @property
    def norm(self):
        if self._norm is None:
            self._norm = sqrt(self.x**2 + self.y**2 + self.z**2)
        return self._norm

    @property
    def direction(self):
        if self._direction is None:
            self._direction = atan2(self.y, self.x)
        return self._direction

    def __repr__(self):
        return f'Vector({self.x}, {self.y}, {self.z})'

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        return NotImplemented

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
        return NotImplemented

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x / scalar, self.y / scalar, self.z / scalar)
        return NotImplemented

    def dot(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        return NotImplemented

    def cross(self, other):
        if isinstance(other, Vector):
            return Vector(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
            )
        return NotImplemented

    def normalize(self):
        if self.norm != 0:
            return self / self.norm
        return Vector(0, 0, 0)

    def rotate(self, angle):
        """Rotate the vector by angle (in radians) in the xy-plane."""
        cos_a, sin_a = cos(angle), sin(angle)
        return Vector(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
            self.z
        )

    @staticmethod
    def from_polar(r, theta, z=0):
        """Create a vector from polar coordinates."""
        return Vector(r * cos(theta), r * sin(theta), z)

    def to_polar(self):
        """Convert the vector to polar coordinates."""
        return self.norm, self.direction, self.z

def distance(v1, v2):
    return (v2 - v1).norm

def angle_between(v1, v2):
    return atan2(v1.cross(v2).norm, v1.dot(v2))

if __name__ == '__main__':
    v1 = Vector(3, 4)
    v2 = Vector(1, 2, 3)
    
    print('v1:', v1)
    print('v2:', v2)
    print('Norme de v1:', v1.norm)
    print(f'Direction de v1:{v1.direction:.4f}')
    print('v1 + v2:', v1 + v2)
    print('v1 - v2:', v1 - v2)
    print('2 * v1:', 2 * v1)
    print('v1 / 2:', v1 / 2)
    print('Produit scalaire v1 . v2:', v1.dot(v2))
    print('Produit vectoriel v1 x v2:', v1.cross(v2))
    print('v1 normalisé:', v1.normalize())
    print('v1 tourné de 90 degrés:', v1.rotate(pi/2))
    print('Distance entre v1 et v2:', distance(v1, v2))
    print('Angle entre v1 et v2:', angle_between(v1, v2))
    
    v3 = Vector.from_polar(5, pi/4)
    print('Vecteur depuis coordonnées polaires:', v3)
    print('Coordonnées polaires de v3:', v3.to_polar())