import pygame
import os
import math  # Import math module for cos and sin functions

# Initialize pygame
pygame.init()

# Set up display
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Initial Track Generation")

# Load menu image
menu_image_path = os.path.join("Assets", "menu_image.png")  # Replace with the actual menu image file path
menu_image = pygame.image.load(menu_image_path)

# Define colors
WHITE = (255, 255, 255)
GREEN = (80, 200, 120)
GRAY = (53, 57, 53)

# Car properties
CAR_WIDTH = 40
CAR_HEIGHT = 20
CAR_COLOR = (255, 0, 0)  # Red

# Sensor properties
NUM_SENSORS = 5
SENSOR_LENGTH = 100
SENSOR_COLORS = [(0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0

    def draw(self, screen):
        # Draw car
        pygame.draw.rect(screen, CAR_COLOR, (self.x, self.y, CAR_WIDTH, CAR_HEIGHT))
        # Draw sensors
        for i in range(NUM_SENSORS):
            sensor_angle = self.angle - 90 + i * (180 / (NUM_SENSORS - 1))
            sensor_end_x = self.x + CAR_WIDTH // 2 + int(SENSOR_LENGTH * math.cos(math.radians(sensor_angle)))
            sensor_end_y = self.y + CAR_HEIGHT // 2 + int(SENSOR_LENGTH * math.sin(math.radians(sensor_angle)))
            pygame.draw.line(screen, SENSOR_COLORS[i], (self.x + CAR_WIDTH // 2, self.y + CAR_HEIGHT // 2), (sensor_end_x, sensor_end_y), 2)

# Initialize car
car = Car(screen_width // 2 - CAR_WIDTH // 2, screen_height // 2 - CAR_HEIGHT // 2)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Set background color
    screen.fill(GREEN)

    # Draw track
    pygame.draw.ellipse(screen, GRAY, (screen_width // 2 - 400, screen_height // 2 - 200, 800, 400), 100)

    # Draw starting line
    pygame.draw.rect(screen, WHITE, (screen_width // 2 - 5, screen_height // 2 + 150, 10, 50))

    # Draw car
    car.draw(screen)

    # Load menu image and draw it on the top right section
    menu_image = pygame.transform.scale(menu_image, (50, 50))  # Adjust size as needed
    menu_image_rect = menu_image.get_rect(topright=(screen_width - 20, 20))  # Adjust position as needed
    screen.blit(menu_image, menu_image_rect)

    # Update screen
    pygame.display.flip()

pygame.quit()

