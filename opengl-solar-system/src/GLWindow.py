import os
import sys

# GLX only exists on Linux; on Windows and macOS let PyOpenGL pick its default platform.
if sys.platform.startswith('linux'):
    os.environ.setdefault('PYOPENGL_PLATFORM', 'glx')

import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

from Geometry import Geometry


class Triangle:

    def __init__(self, shader):
        self.vertexLoc = glGetAttribLocation(shader, "position")
        self.vertices = np.array([0.0, 0.5, 0.0,
                                  -0.5, -0.5, 0.0,
                                  0.5, -0.5, 0.0], dtype=np.float32)

        self.vertexCount = 3
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(self.vertexLoc)
        glVertexAttribPointer(self.vertexLoc, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

    def cleanup(self):
        glDeleteBuffers(1, (self.vbo,))


class OpenGLWindow:

    def __init__(self):
        self.triangle = None
        self.clock = pg.time.Clock()

        # Animation (angles + speeds)
        self.animating = True
        self.earth_angle = 0.0
        self.moon_angle = 0.0
        self.earth_speed = 0.5
        self.moon_speed = 1.5
        
        self.mercury_angle = 0.0
        self.mars_angle    = 0.0
        self.jupiter_angle = 0.0
        self.uranus_angle  = 0.0
        self.mercury_speed = 2.0
        self.mars_speed    = 0.3
        self.jupiter_speed = 0.15
        self.uranus_speed  = 0.08

        # Camera angles (2.1)
        self.cam_yaw = 0.0 # rotate around y axis
        self.cam_pitch = 0.0 # rotate around x axis
        self.cam_distance = 50.0

        # Second orbiting light
        self.light2_angle = 0.0
        self.light2_speed = 0.8
        self.light2_radius = 15.0

        self.sun_light_on = True
        self.light2_on = True

        self.cloud_offset = 0.0
        self.cloud_speed = 0.005

    def loadShaderProgram(self, vertex, fragment):
        with open(vertex, 'r') as f:
            vertex_src = f.readlines()

        with open(fragment, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def initGL(self, screen_width=640, screen_height=480):
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 2)

        pg.display.set_mode((screen_width, screen_height), pg.OPENGL | pg.DOUBLEBUF)

        glEnable(GL_DEPTH_TEST)
        # Uncomment these two lines when perspective camera has been implemented
        #glEnable(GL_CULL_FACE)
        #glCullFace(GL_BACK)
        glClearColor(0, 0, 0, 1)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Note that this path is relative to your working directory when running the program
        # You will need change the filepath if you are running the script from inside ./src/

        self.shader = self.loadShaderProgram("./shaders/simple.vert", "./shaders/simple.frag")
        glUseProgram(self.shader)

        colorLoc = glGetUniformLocation(self.shader, "objectColor")
        glUniform3f(colorLoc, 1.0, 1.0, 1.0)

        # Uncomment this for triangle rendering
        # self.triangle = Triangle(self.shader)

        # Uncomment this for model rendering
        self.sphere = Geometry('./resources/sphere.obj')

        self.sunTex = self.loadTexture('./sun.png')
        self.earthTex = self.loadTexture('./earth.png')
        self.moonTex = self.loadTexture('./moon.png')
        self.mercuryTex = self.loadTexture('./resources/2k_mercury.jpg')
        self.marsTex    = self.loadTexture('./resources/2k_mars.jpg')
        self.jupiterTex = self.loadTexture('./resources/2k_jupiter.jpg')
        self.uranusTex  = self.loadTexture('./resources/2k_uranus.jpg')
        self.cloudTex = self.loadTexture('./resources/2k_earth_clouds.jpg')
        
        self.cloudOffsetLoc = glGetUniformLocation(self.shader, "cloudOffset")
        self.isEarthLoc = glGetUniformLocation(self.shader, "isEarth")
        self.cloudTexLoc = glGetUniformLocation(self.shader, "cloudSampler")

        # Set up of projection (aissignment 1)
        aspect = 640 / 480
        projection = pyrr.matrix44.create_orthogonal_projection_matrix(
            left=-25.0 * aspect,
            right=25.0 * aspect,
            bottom=-25.0,
            top=25.0,
            near=0.1,
            far=200.0,
            dtype=np.float32
        )
        projLoc = glGetUniformLocation(self.shader, "projection")
        glUniformMatrix4fv(projLoc, 1, GL_FALSE, projection)

        # View matrix defines the camera position and orientation (assignment 1)
        # view = pyrr.matrix44.create_identity(dtype=np.float32)
        # viewLoc = glGetUniformLocation(self.shader, "view")
        # glUniformMatrix4fv(viewLoc, 1, GL_FALSE, view)

        # View will be computed each frame in render() (assignment 2 version of code)
        self.viewLoc = glGetUniformLocation(self.shader, "view")

        # Cache location, use in render()
        self.modelLoc = glGetUniformLocation(self.shader, "model")

        self.colorLoc = glGetUniformLocation(self.shader, "objectColor")

        # Shader stuff
        self.lightPosLoc = glGetUniformLocation(self.shader, "lightPos")
        self.viewPosLoc = glGetUniformLocation(self.shader, "viewPos")
        self.lightColorLoc = glGetUniformLocation(self.shader, "lightColor")
        self.texLoc = glGetUniformLocation(self.shader, "textureSampler")
        self.isLightSourceLoc = glGetUniformLocation(self.shader, "isLightSource")

        glUniform3f(self.lightColorLoc, 1.0, 1.0, 0.8)
        glUniform3f(self.lightPosLoc, 0.0, 0.0, 0.0)

        self.light2PosLoc = glGetUniformLocation(self.shader, "light2Pos")
        self.light2ColorLoc = glGetUniformLocation(self.shader, "light2Color")
        glUniform3f(self.light2ColorLoc, 0.0, 0.8, 1.0)
        print("Setup complete!")

    # moves based on speed
    def update(self):
        if self.animating:
            self.earth_angle = (self.earth_angle + self.earth_speed) % 360.0
            self.moon_angle = (self.moon_angle + self.moon_speed) % 360.0
            self.mercury_angle = (self.mercury_angle + self.mercury_speed) % 360.0
            self.mars_angle = (self.mars_angle + self.mars_speed) % 360.0
            self.jupiter_angle = (self.jupiter_angle + self.jupiter_speed) % 360.0
            self.uranus_angle = (self.uranus_angle + self.uranus_speed) % 360.0
            self.light2_angle = (self.light2_angle + self.light2_speed) % 360.0
            self.cloud_offset = (self.cloud_offset + self.cloud_speed) % 1.0

    # handles input, and does things based on key pressed
    def handleInput(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            elif event.type == pg.KEYDOWN:
            # Quit
                if event.key == pg.K_q:
                    return False
            # Start or stop animation
                elif event.key == pg.K_SPACE:
                    self.animating = not self.animating
            # Earth speed up and down
                elif event.key == pg.K_e:
                    self.earth_speed = min(self.earth_speed + 0.1, 10.0)
                elif event.key == pg.K_d:
                    self.earth_speed = max(self.earth_speed - 0.1, 0.0)
            # Moon speed up and down
                elif event.key == pg.K_r:
                    self.moon_speed = min(self.moon_speed + 0.1, 10.0)
                elif event.key == pg.K_f:
                    self.moon_speed = max(self.moon_speed - 0.1, 0.0)
            # Lights toggle
                elif event.key == pg.K_1:
                    self.sun_light_on = not self.sun_light_on
                elif event.key == pg.K_2:
                    self.light2_on = not self.light2_on
            # Camera movement
                elif event.key == pg.K_LEFT:
                    self.cam_yaw -= 5.0
                elif event.key == pg.K_RIGHT:
                    self.cam_yaw += 5.0
                elif event.key == pg.K_UP:
                    self.cam_pitch -= 5.0
                elif event.key == pg.K_DOWN:
                    self.cam_pitch += 5.0
        return True

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)

    # Builds camera position by rotating around origin
        yaw = np.radians(self.cam_yaw)
        pitch = np.radians(self.cam_pitch)

        cam_x = self.cam_distance * np.cos(pitch) * np.sin(yaw)
        cam_y = self.cam_distance * np.sin(pitch)
        cam_z = self.cam_distance * np.cos(pitch) * np.cos(yaw)

        view = pyrr.matrix44.create_look_at(
            eye=pyrr.Vector3([cam_x, cam_y, cam_z]),
            target=pyrr.Vector3([0.0, 0.0, 0.0]),
            up=pyrr.Vector3([0.0, 1.0, 0.0]),
            dtype=np.float32
        )  
        glUniformMatrix4fv(self.viewLoc, 1, GL_FALSE, view)  

        glUniform3f(self.viewPosLoc, cam_x, cam_y, cam_z)

        light2_x = self.light2_radius * np.cos(np.radians(self.light2_angle))
        light2_y = self.light2_radius * np.sin(np.radians(self.light2_angle))
        light2_z = 0.0
        glUniform3f(self.light2PosLoc, light2_x, light2_y, light2_z)

        if self.sun_light_on:
            glUniform3f(self.lightColorLoc, 1.0, 1.0, 0.8)
        else:
            glUniform3f(self.lightColorLoc, 0.0, 0.0, 0.0)

        if self.light2_on:
            glUniform3f(self.light2ColorLoc, 0.0, 0.8, 1.0)
        else:
            glUniform3f(self.light2ColorLoc, 0.0, 0.0, 0.0)


                # Sun
        sun_translate = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([0.0, 0.0, 0.0]), dtype=np.float32
        )
        sun_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([0.8, 0.8, 0.8]), dtype=np.float32
        )
        sun_model = pyrr.matrix44.multiply(sun_scale, sun_translate)
        glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, sun_model)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.sunTex)
        glUniform1i(self.texLoc, 0)
        glUniform1i(self.isLightSourceLoc, 1 if self.sun_light_on else 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)

        # Mercury
        mercury_orbit_translate = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([4.0, 0.0, 0.0]), dtype=np.float32
        )
        mercury_rotate = pyrr.matrix44.create_from_z_rotation(
            np.radians(self.mercury_angle), dtype=np.float32
        )
        mercury_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([0.1, 0.1, 0.1]), dtype=np.float32
        )
        mercury_position = pyrr.matrix44.multiply(mercury_orbit_translate, mercury_rotate)
        mercury_position = pyrr.matrix44.multiply(mercury_position, sun_translate)
        mercury_model = pyrr.matrix44.multiply(mercury_scale, mercury_position)
        glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, mercury_model)
        glBindTexture(GL_TEXTURE_2D, self.mercuryTex)
        glUniform1i(self.isLightSourceLoc, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)

        # Earth
        earth_orbit_translate = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([8.0, 0.0, 0.0]), dtype=np.float32
        )
        earth_rotate = pyrr.matrix44.create_from_z_rotation(
            np.radians(self.earth_angle), dtype=np.float32
        )
        earth_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([0.5, 0.5, 0.5]), dtype=np.float32
        )
        earth_position = pyrr.matrix44.multiply(earth_orbit_translate, earth_rotate)
        earth_position = pyrr.matrix44.multiply(earth_position, sun_translate)
        earth_model = pyrr.matrix44.multiply(earth_scale, earth_position)
        glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, earth_model)
        glBindTexture(GL_TEXTURE_2D, self.earthTex)
        glUniform1i(self.texLoc, 0)
        glUniform1i(self.isEarthLoc, 1)
        glUniform1f(self.cloudOffsetLoc, self.cloud_offset)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.cloudTex)
        glUniform1i(self.cloudTexLoc, 1)
        glActiveTexture(GL_TEXTURE0)
        glUniform1i(self.isLightSourceLoc, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)
        glUniform1i(self.isEarthLoc, 0)

        # Moon (inherits earth_position)
        moon_orbit_translate = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([2.0, 0.0, 0.0]), dtype=np.float32
        )
        moon_rotate = pyrr.matrix44.create_from_z_rotation(
            np.radians(self.moon_angle), dtype=np.float32
        )
        moon_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([0.11, 0.11, 0.11]), dtype=np.float32
        )
        moon_position = pyrr.matrix44.multiply(moon_orbit_translate, moon_rotate)
        moon_position = pyrr.matrix44.multiply(moon_position, earth_position)
        moon_model = pyrr.matrix44.multiply(moon_scale, moon_position)
        glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, moon_model)
        glBindTexture(GL_TEXTURE_2D, self.moonTex)
        glUniform1i(self.isLightSourceLoc, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)

        # Mars
        mars_orbit_translate = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([12.0, 0.0, 0.0]), dtype=np.float32
        )
        mars_rotate = pyrr.matrix44.create_from_z_rotation(
            np.radians(self.mars_angle), dtype=np.float32
        )
        mars_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([0.3, 0.3, 0.3]), dtype=np.float32
        )
        mars_position = pyrr.matrix44.multiply(mars_orbit_translate, mars_rotate)
        mars_position = pyrr.matrix44.multiply(mars_position, sun_translate)
        mars_model = pyrr.matrix44.multiply(mars_scale, mars_position)
        glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, mars_model)
        glBindTexture(GL_TEXTURE_2D, self.marsTex)
        glUniform1i(self.isLightSourceLoc, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)

        # Jupiter
        jupiter_orbit_translate = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([18.0, 0.0, 0.0]), dtype=np.float32
        )
        jupiter_rotate = pyrr.matrix44.create_from_z_rotation(
            np.radians(self.jupiter_angle), dtype=np.float32
        )
        jupiter_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([0.65, 0.65, 0.65]), dtype=np.float32
        )
        jupiter_position = pyrr.matrix44.multiply(jupiter_orbit_translate, jupiter_rotate)
        jupiter_position = pyrr.matrix44.multiply(jupiter_position, sun_translate)
        jupiter_model = pyrr.matrix44.multiply(jupiter_scale, jupiter_position)
        glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, jupiter_model)
        glBindTexture(GL_TEXTURE_2D, self.jupiterTex)
        glUniform1i(self.isLightSourceLoc, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)

        # Uranus
        uranus_orbit_translate = pyrr.matrix44.create_from_translation(
            pyrr.Vector3([24.0, 0.0, 0.0]), dtype=np.float32
        )
        uranus_rotate = pyrr.matrix44.create_from_z_rotation(
            np.radians(self.uranus_angle), dtype=np.float32
        )
        uranus_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([0.45, 0.45, 0.45]), dtype=np.float32
        )
        uranus_position = pyrr.matrix44.multiply(uranus_orbit_translate, uranus_rotate)
        uranus_position = pyrr.matrix44.multiply(uranus_position, sun_translate)
        uranus_model = pyrr.matrix44.multiply(uranus_scale, uranus_position)
        glUniformMatrix4fv(self.modelLoc, 1, GL_FALSE, uranus_model)
        glBindTexture(GL_TEXTURE_2D, self.uranusTex)
        glUniform1i(self.isLightSourceLoc, 0)
        glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)

        pg.display.flip()

        #Uncomment this for triangle rendering
        # glDrawArrays(GL_TRIANGLES, 0, self.triangle.vertexCount)

        # Uncomment this for model rendering
        # glDrawArrays(GL_TRIANGLES, 0, self.sphere.vertexCount)


        # Swap the front and back buffers on the window, effectively putting what we just "drew"
        # Onto the screen (whereas previously it only existed in memory)
        # pg.display.flip()

    def loadTexture(self, path):
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pg.image.load(path)
        image = pg.transform.flip(image, False, True)

    # Detect format based on file extension
        if path.lower().endswith('.jpg'):
            image_data = pg.image.tostring(image, "RGB", False)
            fmt = GL_RGB
        else:
            image_data = pg.image.tostring(image, "RGBA", False)
            fmt = GL_RGBA

        width, height = image.get_size()
        glTexImage2D(GL_TEXTURE_2D, 0, fmt, width, height, 0, fmt, GL_UNSIGNED_BYTE, image_data)

        return texture

    def cleanup(self):
        glDeleteVertexArrays(1, (self.vao,))
        # Uncomment for triangle rendering
        # self.triangle.cleanup()
        # Uncomment for model rendering
        self.sphere.cleanup()
