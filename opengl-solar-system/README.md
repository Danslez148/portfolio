# OpenGL Solar System

An animated, textured Sun–Earth–Moon system rendered with modern OpenGL: hand-built sphere geometry, GLSL vertex and fragment shaders, lighting and keyboard controls, plus unit tests for the geometry code.

**Context:** Computer Graphics module, UCT Honours (2026). Individual.
**Tech:** Python, PyOpenGL, pygame, pyrr (matrix maths), NumPy, GLSL.

---
SCHDAN066

Setup assumes that you are using a UNIX-based OS with python3 and python3-venv installed.

To build the virtual environment and install necessary packages:

```
> make
```

To activate the virtual environment:

```
> source ./venv/bin/activate
```

To run the code:

```
> python ./src/main.py
```

To control the animation:

| Key   | Action                |
| Space | Start / stop          |
| E / D | Earth faster / slower |
| R / F | Moon faster / slower  |
| Q     | Quit                  |
| 1 / 2 | Toggle lights         |
|UP/DOWN/LEFT/RIGHT| Pan camera |

References:

Khronos OpenGL Documentation https://www.khronos.org/opengl/
Learn OpenGL https://learnopengl.com
Textures https://www.solarsystemscope.com/textures/