# COMP 4431 - Advanced Project
# Group 7
# Procedural Generation
# - Matthew Richard -

# import libraries
import pygame
import random
import math

car = pygame.image.load('Track Generation\obstacleAssets\carObstacle.png')
car = pygame.transform.scale(car, (50, 50))

# method to randomly generate points
def generatePoints(numPoints):

    # initialize variables
    screenWidth = screen.get_width()
    screenHeight = screen.get_height()
    screenCenterX = screenWidth / 2
    screenCenterY = screenHeight / 2
    trackRangeX = screenWidth / 3
    trackRangeY = screenHeight / 3
    skew = 100
    trackPoints = []

    for i in range(numPoints):
        angle = ((2 * math.pi) * i) / numPoints # calculate where the point would lie on a circle evenly divided by the number of points
        x = screenCenterX + (trackRangeX * math.cos(angle)) + random.randint(-skew, skew) # parametric equation of ellipse for X value
        y = screenCenterY + (trackRangeY * math.sin(angle)) + random.randint(-skew, skew) # parametric equation of ellipse for Y value
        trackPoints.append((x, y)) # add points to the list

    # return track points
    return trackPoints


# method to calculate tangets of points
def calculateTangets(points):

    # create vector
    tangents = []

    for i in range(len(points)):
        nextPoint = points[(i + 1) % len(points)] # get next point
        tangent = (nextPoint[0] - points[i][0], nextPoint[1] - points[i][1]) # calculate tangent between points
        tangents.append(tangent) # add tangent to vector
        
    return tangents


# method to calculate hermite curve points
def calculateHermite(t, p0, p1, m0, m1):

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


# method to draw track to the screen
def drawTrack(screen, points, tangents):

    # initialize variables
    trackColour = (53, 57, 53) # grey for road
    trackSize = 50 # width of track
    numberOfCurvePoints = 2000 # points along hermite curve

    for i in range(len(points)):
        # Get points and tangents from vectors
        p0 = points[i]
        p1 = points[(i + 1) % len(points)]
        m0 = tangents[i]
        m1 = tangents[(i + 1) % len(points)]

        for j in range(numberOfCurvePoints):
            t = j / numberOfCurvePoints
            curvePoints = calculateHermite(t, p0, p1, m0, m1) # calculate point on hermite curve
            pygame.draw.circle(screen, trackColour, curvePoints, trackSize) # draw point on hermite curve

    startingPoint = (points[0][0], points[0][1])
    startingTangent = tangents[0]
    startingAngle = math.degrees(math.atan2(startingTangent[1], startingTangent[0]))
    transformedCar = pygame.transform.rotate(car, startingAngle)
    screen.blit(transformedCar, transformedCar.get_rect(center=startingPoint))

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Procedural Generation Racetrack')
running = True

# initialize variables
numberOfPoints = 8 # number of points on the track
points = generatePoints(numberOfPoints) # call random point generation method
tangents = calculateTangets(points) # call method to calculate tangets
backgroundColour = (80, 200, 120) # green for grass background

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(backgroundColour) # fill background with green to resemble grass

    drawTrack(screen, points, tangents) # call method to draw the track

    pygame.display.flip()

pygame.quit()