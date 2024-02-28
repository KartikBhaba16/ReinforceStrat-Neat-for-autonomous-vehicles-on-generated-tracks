#Tanner Boyle
#Vivek Sheth
#Encapsulates the procedural generation of a racetrack, including the generation of points, tangents, and the Hermite curve
#February 26 2024

import os
import pygame
import random
import math

class ProceduralObject:
    def __init__(self, screenWidth, screenHeight, numPoints, trackRangeX, trackRangeY, skew, trackSize, numberOfCurvePoints):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.screenCenterX = screenWidth / 2
        self.screenCenterY = screenHeight / 2
        self.numPoints = numPoints
        self.trackRangeX = trackRangeX
        self.trackRangeY = trackRangeY
        self.skew = skew
        self.trackSize = trackSize
        self.numberOfCurvePoints = numberOfCurvePoints
        self.points = []
        self.tangents = []

    def generatePoints(self):
        for i in range(self.numPoints):
            angle = ((2 * math.pi) * i) / self.numPoints
            x = self.screenCenterX + (self.trackRangeX * math.cos(angle)) + random.randint(-self.skew, self.skew)
            y = self.screenCenterY + (self.trackRangeY * math.sin(angle)) + random.randint(-self.skew, self.skew)
            self.points.append((x, y))

    def calculateTangets(self):
        for i in range(len(self.points)):
            nextPoint = self.points[(i + 1) % len(self.points)]
            tangent = (nextPoint[0] - self.points[i][0], nextPoint[1] - self.points[i][1])
            self.tangents.append(tangent)
            

    def calculateHermite(self, t, p0, p1, m0, m1):
        h00 = (2 * pow(t, 3)) - (3 * pow(t, 2)) + 1
        h10 = pow(t, 3) - (2 * pow(t, 2)) + t
        h01 = (-2 * pow(t, 3)) + (3 * pow(t, 2))
        h11 = pow(t, 3) - pow(t, 2)
        x = h00 * p0[0] + h10 * m0[0] + h01 * p1[0] + h11 * m1[0]
        y = h00 * p0[1] + h10 * m0[1] + h01 * p1[1] + h11 * m1[1]
        return x, y

    def drawTrack(self, screen):
        trackColour = (53, 57, 53)
        track_pixel_points = []
        for i in range(len(self.points)):
            p0 = self.points[i]
            p1 = self.points[(i + 1) % len(self.points)]
            m0 = self.tangents[i]
            m1 = self.tangents[(i + 1) % len(self.points)]
            for j in range(self.numberOfCurvePoints):
                t = j / self.numberOfCurvePoints
                curvePoints = self.calculateHermite(t, p0, p1, m0, m1)
                track_pixel_points.append(curvePoints)
                pygame.draw.circle(screen, trackColour, curvePoints, self.trackSize)
        for point in self.points:
            pygame.draw.circle(screen, (255, 95, 31), (point[0], point[1]), 10)
        return track_pixel_points

        
    def saveImage(self, image_path):
        pygame.image.save(screen, image_path)

    def saveTrackPoints(self, track_points_path):
        with open(track_points_path, 'w') as file:
            for point in self.points:
                file.write(f"{point[0]},{point[1]}\n")

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption('Procedural Generation Racetrack')
running = True

proceduralObject = ProceduralObject(1920, 1080, 8, 1920 / 3, 1080 / 3, 100, 50, 2000)
proceduralObject.generatePoints()
proceduralObject.calculateTangets()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((80, 200, 120))

    proceduralObject.drawTrack(screen)

    pygame.display.flip()

image_path = os.path.join('assets', 'map.png')
if not os.path.exists('assets'):
    os.makedirs('assets')
proceduralObject.saveImage(image_path)

track_points_path = os.path.join('assets', 'track_points.txt')
proceduralObject.saveTrackPoints(track_points_path)

pygame.quit()
