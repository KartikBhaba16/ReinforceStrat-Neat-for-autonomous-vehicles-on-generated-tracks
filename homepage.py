import pygame
import os
import math


pygame.init()


screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Initial Track Generation")


menu_image_path = os.path.join("Assets", "menu_image.png")
menu_image = pygame.image.load(menu_image_path)


car_image_path = os.path.join("Assets", "car.png")
car_image = pygame.image.load(car_image_path).convert_alpha()  


WHITE = (255, 255, 255)
GREEN = (80, 200, 120)
GRAY = (53, 57, 53)


CAR_WIDTH = 40
CAR_HEIGHT = 20
CAR_SPEED = 5
CAR_ROTATE_SPEED = 5


NUM_SENSORS = 5
SENSOR_LENGTH = 100
SENSOR_COLORS = [(0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
SENSOR_THRESHOLD = 20  

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(car_image, self.angle)  # Rotate car image
        screen.blit(rotated_image, (self.x, self.y))
     
        for i in range(NUM_SENSORS):
            sensor_angle = self.angle - 90 + i * (180 / (NUM_SENSORS - 1))
            sensor_end_x = self.x + CAR_WIDTH // 2 + int(SENSOR_LENGTH * math.cos(math.radians(sensor_angle)))
            sensor_end_y = self.y + CAR_HEIGHT // 2 + int(SENSOR_LENGTH * math.sin(math.radians(sensor_angle)))
            pygame.draw.line(screen, SENSOR_COLORS[i], (self.x + CAR_WIDTH // 2, self.y + CAR_HEIGHT // 2), (sensor_end_x, sensor_end_y), 2)

    def move_forward(self):
        self.x += int(CAR_SPEED * math.cos(math.radians(self.angle)))
        self.y += int(CAR_SPEED * math.sin(math.radians(self.angle)))

    def move_backward(self):
        self.x -= int(CAR_SPEED * math.cos(math.radians(self.angle)))
        self.y -= int(CAR_SPEED * math.sin(math.radians(self.angle)))

    def rotate_left(self):
        self.angle += CAR_ROTATE_SPEED

    def rotate_right(self):
        self.angle -= CAR_ROTATE_SPEED

    def detect_collision(self, obstacles):
        for i in range(NUM_SENSORS):
            sensor_angle = self.angle - 90 + i * (180 / (NUM_SENSORS - 1))
            sensor_end_x = self.x + CAR_WIDTH // 2 + int(SENSOR_LENGTH * math.cos(math.radians(sensor_angle)))
            sensor_end_y = self.y + CAR_HEIGHT // 2 + int(SENSOR_LENGTH * math.sin(math.radians(sensor_angle)))
            sensor_rect = pygame.Rect(sensor_end_x, sensor_end_y, 1, 1)
            for obstacle in obstacles:
                if sensor_rect.colliderect(obstacle):
                    return True
        return False


car = Car(screen_width // 2 - CAR_WIDTH // 2, screen_height // 2 - CAR_HEIGHT // 2)

obstacles = [pygame.Rect(200, 200, 50, 50), pygame.Rect(600, 300, 100, 80), pygame.Rect(900, 400, 80, 120)]

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                car.move_forward()
            elif event.key == pygame.K_DOWN:
                car.move_backward()
            elif event.key == pygame.K_LEFT:
                car.rotate_left()
            elif event.key == pygame.K_RIGHT:
                car.rotate_right()

    screen.fill(GREEN)


    pygame.draw.ellipse(screen, GRAY, (screen_width // 2 - 400, screen_height // 2 - 200, 800, 400), 100)


    pygame.draw.rect(screen, WHITE, (screen_width // 2 - 5, screen_height // 2 + 150, 10, 50))


    for obstacle in obstacles:
        pygame.draw.rect(screen, WHITE, obstacle)

  
    car.draw(screen)

    
    if car.detect_collision(obstacles):
        print("Collision detected!")

    menu_image = pygame.transform.scale(menu_image, (50, 50))
    menu_image_rect = menu_image.get_rect(topright=(screen_width - 20, 20))
    screen.blit(menu_image, menu_image_rect)


    pygame.display.flip()

pygame.quit()
