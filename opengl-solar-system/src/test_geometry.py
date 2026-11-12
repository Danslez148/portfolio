import os
import sys

# GLX only exists on Linux; on Windows and macOS let PyOpenGL pick its default platform.
if sys.platform.startswith('linux'):
    os.environ.setdefault('PYOPENGL_PLATFORM', 'glx')

import pygame as pg
from OpenGL.GL import *
from Geometry import Geometry

pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_COMPATIBILITY)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 2)
pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)

print("OpenGL version:", glGetString(GL_VERSION))

g = Geometry('../resources/sphere.obj')
print('Vertex count:', g.vertexCount)
print('First few vertices:', g.vertices[:9])

pg.quit()