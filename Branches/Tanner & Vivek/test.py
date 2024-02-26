import math
import random
import sys
import os

import neat
import pygame
from proceduralgeneration import *

# Updated screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Updated car dimensions
CAR_WIDTH = 60
CAR_HEIGHT = 60

# Updated to a more descriptive variable name
CRASH_BORDER_COLOR = (80, 200, 120)

gen_counter = 0  # Updated variable name for clarity

numberOfPoints= 8 # Updated variable name for clarity
points = generatePoints(numberOfPoints)
tangents = calculateTangets(points)

# Now, generate the track points
track_points = drawTrack(screen, points, tangents)

class AutonomousCar:
    def __init__(self):
        self.car_image = pygame.image.load('car.png').convert_alpha()
        self.car_image = pygame.transform.scale(self.car_image, (CAR_WIDTH, CAR_HEIGHT))
        self.rotated_car_image = self.car_image
        print(track_points[0], " ", track_points[1])
        self.position = [int(track_points[0]), int(track_points[1])]
        self.direction = 0
        self.movement_speed = 0

        self.initial_speed_set = False

        self.car_center = [self.position[0] + CAR_WIDTH / 2, self.position[1] + CAR_HEIGHT / 2]

        self.sensors = []
        self.sensor_visualization = []

        self.is_active = True

        self.travel_distance = 0
        self.time_alive = 0

    def display_car(self, window):
        window.blit(self.rotated_car_image, self.position)
        self.display_sensors(window)

    def display_sensors(self, window):
        for sensor in self.sensors:
            sensor_pos = sensor[0]
            pygame.draw.line(window, (0, 255, 0), self.car_center, sensor_pos, 1)
            pygame.draw.circle(window, (0, 255, 0), sensor_pos, 5)

    def detect_crash(self, track_layout):
        self.is_active = True
        track_layout.unlock()
        for corner in self.calculate_corners():
            if track_layout.get_at((int(corner[0]), int(corner[1]))) == CRASH_BORDER_COLOR:
                self.is_active = False
                break

    def sensor_detection(self, angle, track_layout):
        distance = 0
        x = int(self.car_center[0] + math.cos(math.radians(360 - (self.direction + angle))) * distance)
        y = int(self.car_center[1] + math.sin(math.radians(360 - (self.direction + angle))) * distance)

        while not track_layout.get_at((x, y)) == CRASH_BORDER_COLOR and distance < 300:
            distance += 1
            x = int(self.car_center[0] + math.cos(math.radians(360 - (self.direction + angle))) * distance)
            y = int(self.car_center[1] + math.sin(math.radians(360 - (self.direction + angle))) * distance)

        dist_to_obstacle = int(math.sqrt((x - self.car_center[0]) ** 2 + (y - self.car_center[1]) ** 2))
        self.sensors.append([(x, y), dist_to_obstacle])

    def update_car(self, track_layout):
        if not self.initial_speed_set:
            self.movement_speed = 20
            self.initial_speed_set = True

        self.rotated_car_image = self.rotate_image(self.car_image, self.direction)
        self.position[0] += math.cos(math.radians(360 - self.direction)) * self.movement_speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], SCREEN_WIDTH - CAR_WIDTH)

        self.travel_distance += self.movement_speed
        self.time_alive += 1

        self.position[1] += math.sin(math.radians(360 - self.direction)) * self.movement_speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], SCREEN_HEIGHT - CAR_HEIGHT)

        self.car_center = [int(self.position[0]) + CAR_WIDTH / 2, int(self.position[1]) + CAR_HEIGHT / 2]

        self.detect_crash(track_layout)
        self.sensors.clear()

        for d in range(-90, 135, 45):
            self.sensor_detection(d, track_layout)

    def rotate_image(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def calculate_corners(self):
        corners = []
        for angle in [30, 150, 210, 330]:
            x = self.car_center[0] + math.cos(math.radians(360 - (self.direction + angle))) * (CAR_WIDTH / 2)
            y = self.car_center[1] + math.sin(math.radians(360 - (self.direction + angle))) * (CAR_HEIGHT / 2)
            corners.append([x, y])
        return corners

    def gather_inputs(self):
        sensor_data = [sensor[1] for sensor in self.sensors]
        input_values = [int(distance / 30) for distance in sensor_data] + [0] * (5 - len(sensor_data))
        return input_values

    def is_functional(self):
        return self.is_active

    def compute_reward(self):
        return self.travel_distance / (CAR_WIDTH / 2)
    
def run_simulation(genomes, config):
        global gen_counter
        gen_counter += 1

        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Car Simulation")

        # Load the track image
        track_image = pygame.image.load('track5.png').convert()

        # Create car instances for each genome
        cars = []
        neural_networks = []
        ge = []

        for genome_id, genome in genomes:
            genome.fitness = 0  # Start with fitness level of 0
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            neural_networks.append(net)
            cars.append(AutonomousCar())
            ge.append(genome)

        clock = pygame.time.Clock()
        run = True
        while run and len(cars) > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()

            # Get input from the network and move the cars
            for x, car in enumerate(cars):
                output = neural_networks[cars.index(car)].activate(car.gather_inputs())
                choice = output.index(max(output))

                if choice == 0:
                    car.direction += 10
                elif choice == 1:
                    car.direction -= 10
                elif choice == 2 and car.movement_speed > 10:
                    car.movement_speed -= 2
                elif choice == 3:
                    car.movement_speed += 2

                car.update_car(track_image)

                # Adjust fitness
                ge[x].fitness += car.compute_reward()

                if not car.is_functional():
                    ge[x].fitness -= 1  # Penalize for crashing
                    cars.pop(x)
                    neural_networks.pop(x)
                    ge.pop(x)

            # Drawing
            screen.blit(track_image, (0, 0))
            for car in cars:
                car.display_car(screen)

            pygame.display.flip()
            clock.tick(60)  # FPS

        pygame.quit()

if __name__ == "__main__":
    # Load the NEAT configuration
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Create the population, which is the top-level object for a NEAT run
    population = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run for up to 50 generations
    winner = population.run(run_simulation, 50)

    print(f"\nBest genome:\n{winner}")
