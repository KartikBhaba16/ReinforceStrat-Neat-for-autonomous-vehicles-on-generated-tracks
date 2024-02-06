# COMP 4431 - Advanced Project
# Group 7
# Tanner Boyle, Vivek Sheth
# Beginning Process of Neural Network Creation
# Track Code from Matthew Richard to use as early testing for implementation

#January 28th, reorganised track into OOP structure to make things easier to work with in modules

import pygame
import sys

class Game:
    def __init__(self): # Constructor for Game()
        pygame.init() # Initialize pygame
        self.screen = pygame.display.set_mode((1280, 720)) #Screen Width/Height
        self.running = True # Boolean to keep track of game state
        self.backgroundColour = (80, 200, 120) # Green Background
        self.track = Track(self.screen) # Var to call track Class with pygame display passed
    
    def run(self):
        while self.running:
            for event in pygame.event.get(): #Event handling for quitting game
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.screen.fill(self.backgroundColour) #Draw screen color
            self.track.draw() #Call method to draw track
            pygame.display.flip() #Pushes all drawings to track
        
        pygame.quit()
        sys.exit() #Exit app and pygame

class Track:
    def __init__(self, screen):
        self.screen = screen #Localize passed argument
        self.trackColour = (53, 57, 53) #Set track Color
        self.ellipseWidth = 800
        self.ellipseHeight = 400
        self.ellipseX = (self.screen.get_width() - self.ellipseWidth) / 2
        self.ellipseY = (self.screen.get_height() - self.ellipseHeight) / 2
        self.trackWidth = 100 #Set Track Parameters

    def draw(self): #Helper method to draw track components to screen
        pygame.draw.ellipse(self.screen, self.trackColour, (self.ellipseX, self.ellipseY, self.ellipseWidth, self.ellipseHeight), self.trackWidth)
        self.draw_start_line() 

    def draw_start_line(self): #Helper method to draw starting Line
        # Initialize variables for starting line
        startLineWidth = 10
        startLineHeight = self.ellipseHeight / 4
        startLineX = (self.ellipseX + self.ellipseWidth / 2) - (startLineWidth / 2)
        startLineY = self.ellipseY + self.ellipseHeight - startLineHeight
        # Draw starting line
        pygame.draw.rect(self.screen, (255, 255, 255), (startLineX, startLineY, startLineWidth, startLineHeight))
if __name__ == "__main__":
    game = Game()
    game.run()#Tells program which Class to start from