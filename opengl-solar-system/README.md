# OpenGL Solar System

An animated, textured Sun–Earth–Moon system rendered with modern OpenGL: hand-built sphere geometry, GLSL vertex and fragment shaders, lighting and keyboard controls, plus unit tests for the geometry code.

**Context:** Computer Graphics module, UCT Honours (2026). Individual.
**Tech:** Python, PyOpenGL, pygame, pyrr (matrix maths), NumPy, GLSL.

## Run

### Linux / macOS
Needs python3 and python3-venv. To build the virtual environment and install the packages:

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

### Windows
```
> python -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
> python src\main.py
```
`PyOpenGL_accelerate` (in `post_requirements.txt`) is an optional speed-up and can be skipped on Windows. The project was developed and tested on Linux.

### Controls

| Key   | Action                |
|-------|-----------------------|
| Space | Start / stop          |
| E / D | Earth faster / slower |
| R / F | Moon faster / slower  |
| Q     | Quit                  |
| 1 / 2 | Toggle lights         |
| Arrow keys | Pan camera |

References:

Khronos OpenGL Documentation https://www.khronos.org/opengl/
Learn OpenGL https://learnopengl.com
Textures https://www.solarsystemscope.com/textures/