# COMP 4431 - Advanced Project
# Group 7
# Inital Track Generation
# - Matthew Richard -

import pygame

# initialize pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # set background colour
    backgroundColour = (80, 200, 120)
    screen.fill(backgroundColour)

    # initialize variables for ellipse
    ellipseWidth = 800
    ellipseHeight = 400
    trackColour = (53, 57, 53)
    ellipseX = (screen.get_width() - ellipseWidth) / 2 # center ellipse in middle of screen
    ellipseY = (screen.get_height() - ellipseHeight) / 2 # center ellipse in middle of screen

    # draw ellipse
    pygame.draw.ellipse(screen, trackColour, (ellipseX, ellipseY, ellipseWidth, ellipseHeight), 100)

    # initiliaze variables for starting line
    startLineWidth = 10
    startLineHeight = ellipseHeight / 4  # start line is 1/4 of the total ellipse height
    startLineX = (ellipseX + ellipseWidth / 2) - (startLineWidth / 2) # center start line in middle of ellipse
    startLineY = ellipseY + ellipseHeight - startLineHeight  # set ellipse y to the bottom of the ellipse

    # draw starting line
    pygame.draw.rect(screen, (255, 255, 255), (startLineX, startLineY, startLineWidth, startLineHeight))

    # update screen
    pygame.display.flip()


pygame.quit()