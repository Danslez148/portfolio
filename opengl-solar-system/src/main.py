import pygame as pg
from GLWindow import *

def main():
	""" The main method where we create and setup our PyGame program """

	running = True
	window = OpenGLWindow()
	window.initGL()

	while running:

		running = window.handleInput()
		window.update()
		window.render()
		window.clock.tick(60)

	pg.quit()
	window.cleanup()


if __name__ == "__main__":
	main()