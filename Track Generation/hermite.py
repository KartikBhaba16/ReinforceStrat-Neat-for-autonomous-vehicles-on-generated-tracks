# COMP 4431 - Advanced Project
# Group 7
# Hermite Curve Test
# - Matthew Richard -

import pygame

# method to calculate hermite curve points
def hermite(t, p0, p1, m0, m1):

    # hermite functions
    h00 = (2 * pow(t, 3)) - (3 * pow(t, 2)) + 1
    h10 = pow(t, 3) - (2 * pow(t, 2)) + t
    h01 = (-2 * pow(t, 3)) + (3 * pow(t, 2))
    h11 = pow(t, 3) - pow(t, 2)

    # apply hermite spline formula for x and y coorindates
    x = h00 * p0[0] + h10 * m0[0] + h01 * p1[0] + h11 * m1[0]
    y = h00 * p0[1] + h10 * m0[1] + h01 * p1[1] + h11 * m1[1]

    # return curve point coordinates
    return x, y

# initialize pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Hermite Curve')
running = True

# initialize point variables
pointRadius = 10
pointY = (screen.get_height() - pointRadius) / 2 # vertically center points in middle of the screen
leftPointX = (screen.get_width() - pointRadius) / 4 # set starting point X to 1/4 of the screen
rightPointX = (screen.get_width() - pointRadius) * 3 / 4 # set ending point X to 3/4 of the screen
leftTangent = (leftPointX - 100, pointY) # tangent for starting point
rightTangent = (rightPointX + 100, pointY) # tangent for ending point

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # set colours
    backgroundColour = (0, 0, 0)
    screen.fill(backgroundColour)
    pointColour = (255, 255, 255)
    curveColour = (255,0,0)

    # draw starting and end points
    pygame.draw.circle(screen, pointColour, (leftPointX, pointY), pointRadius)
    pygame.draw.circle(screen, pointColour, (rightPointX, pointY), pointRadius)

    # draw curve with 1000 points
    numCurvePoints = 1000
    for i in range(numCurvePoints):
        t = i / numCurvePoints # find current location in curve
        curvePoint = hermite(t, (leftPointX, pointY), (rightPointX, pointY), leftTangent, rightTangent) # calculate point in hermite curve
        pygame.draw.circle(screen, curveColour, curvePoint, 1) # draw curve points on screen

    # update screen
    pygame.display.flip()

pygame.quit()
