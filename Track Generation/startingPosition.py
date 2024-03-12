

import math
import random
import sys
import os

import neat
import pygame
from proceduralobject import ProceduralObject
import functools
import operator
import statistics
import visualize

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 50    
CAR_SIZE_Y = 50

BORDER_COLOR = (80, 200, 120) # Color To Crash on Hit

current_generation = 0 # Generation counter

class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        sprite_path = os.path.join(r":\Users\beake\OneDrive\Documents\GitHub\COMP4431\Assets", "car.png")
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        
        self.clock = pygame.time.Clock()
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        self.position = [1000, 920] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False


        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Calculate Center

        self.radars = [] # List For Sensors / Radars
        self.drawing_radars = [] # Radars To Be Drawn

        self.alive = True # Boolean To Check If Car is Crashed

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Driven
        self.checkpoints = 0 # Checkpoints Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position) # Draw Sprite
        self.draw_radar(screen) #OPTIONAL FOR SENSORS

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.alive = True
        map_width=WIDTH
        map_height=HEIGHT
        for point in self.corners:
            # Check if point is within the boundaries of the game_map
            if 0 <= int(point[0]) < map_width and 0 <= int(point[1]) < map_height:
            # If any corner touches border color -> crash
                if game_map.get_at((int(point[0]), int(point[1]))) == (255, 95, 31):
                    self.checkpoints +=1
                if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                    self.alive = False
                    break
            else:
                # Consider out of bounds as a collision
                self.alive = False
                break


    def check_radar(self, degree, game_map):
        # Initialize length
        length = 0
        # Calculate x and y outside the loop to initialize them
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Get the size of the game map to ensure radar checks stay within bounds
        map_width, map_height = game_map.get_size()

        # Continue to extend the radar until it hits the border or reaches its maximum length
        while length < 300:
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
            
            # Check if the radar point is within the bounds of the game map
            if x < 0 or y < 0 or x >= map_width or y >= map_height:
                # Radar point is out of bounds
                distance = length  # Use the length as the distance if out of bounds
                break  # Break out of the loop since we hit the boundary or the radar max length

            # If the radar detects the border color, stop extending the radar
            if game_map.get_at((x, y)) == BORDER_COLOR:
                # Calculate the distance to the border or obstacle and break
                distance = length
                break

            # Increment the radar length for the next iteration
            length += 1
        else:  # This else corresponds to the while, it executes if no break was hit
            distance = length  # Use the length as the distance if no collision was detected

        # Append the radar information including the distance to the self.radars list
        self.radars.append([(x, y), distance])


    
    def update(self, game_map):
        # Set The Speed To 5 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 5px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 5)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.clock.tick(60)
        self.time = self.clock.get_time()
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        return (self.time / 10000) + (self.distance / 10) + (self.checkpoints / 10)

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


def run_simulation(genomes, config):
    
    # Empty Collections For Nets and Cars
    nets = []
    cars = []
    
    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        cars.append(Car())
    
    start_point = track_points[6]   # set starting point to point 6 (Top of the track)
    next_point = track_points[7] # set next point to point 7
    tangent_x = next_point[0] - start_point[0] # calculate x value for the slope of the tangent
    tangent_y = next_point[1] - start_point[1] # calculate y value for the slope of the tangent
    start_angle = math.degrees(math.atan2(tangent_y, tangent_x)) # calculate angle

    for car in cars:
        car.position = [start_point[0], start_point[1]]
        car.angle = start_angle

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)


    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
        print
        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10 # Left
            elif choice == 1:
                car.angle -= 10 # Right
            elif choice == 2:
                if(car.speed - 1 >= 20):
                    car.speed -= 1 # Slow Down
            else:
                car.speed += 1 # Speed Up
        
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()
        

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.topleft = (10, 10)  # Set the top left position of the text
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (10, 50)  # Set the top left position of the text
        screen.blit(text, text_rect)
        
        pygame.display.update() # update screen to show cars drawn
        clock.tick(60) # 60 FPS

if __name__ == "__main__":

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.WINDOWMAXIMIZED)

    # Load Config
    config_path = "Branches\TannerVivek\config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # create track, find its variables, and draw the track to the screen
    track = ProceduralObject(WIDTH, HEIGHT, 8, WIDTH / 3, HEIGHT / 3, 100, 75, 2000)
    track.generatePoints()
    track.calculateTangets()
    global track_points 
    track_points = track.points
    track.drawTrack(screen)
    game_map_path = os.path.join("Assets", "map.png")
    global game_map
    game_map = pygame.image.load(game_map_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 100)
    print("Simulation Finished")