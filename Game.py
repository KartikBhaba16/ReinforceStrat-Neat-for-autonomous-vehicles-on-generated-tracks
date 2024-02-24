import pygame
import math
from math import radians
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class Car:
    def __init__(self, x, y, width=60, height=30, angle=0, max_speed=5):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle  
        self.speed = 0
        self.max_speed = max_speed
        self.color = (255, 0, 0)  
        self.front_color = (255, 255, 0)  

 
        front_color = (0, 255, 0)   
        back_color = (255, 0, 0)   
        left_color = (0, 0, 255)    
        right_color = (255, 255, 0) 

    
        self.sensors = []
        for sensor_angle in range(-180, 181, 45):
            if sensor_angle in [0, 45, -45]: 
                sensor_color = front_color
            elif sensor_angle in [135, 180, -135]:  
                sensor_color = back_color
            elif sensor_angle == 90: 
                sensor_color = right_color
            elif sensor_angle == -90:  
                sensor_color = left_color
            else:  
                sensor_color = (255, 255, 255)  

            self.sensors.append(Sensor(self, sensor_angle, sensor_color))
    def update(self, action, track_lines):  
        turn_speed, acceleration = action
        self.angle += turn_speed
        self.speed = max(0, min(self.max_speed, self.speed + acceleration))
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))

        if self.check_collision(track_lines):
            self.speed = 0  
            return  
        
    def get_rect_points(self):
   
        cx, cy = self.x, self.y

        corners = [
            pygame.Vector2(-self.width / 2, -self.height / 2),
            pygame.Vector2(self.width / 2, -self.height / 2),
            pygame.Vector2(self.width / 2, self.height / 2),
            pygame.Vector2(-self.width / 2, self.height / 2),
        ]


        angle_rad = radians(self.angle)  
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        rotated_corners = []
        for corner in corners:
       
            rotated_corner_x = cx + corner.x * cos_angle - corner.y * sin_angle
            rotated_corner_y = cy + corner.x * sin_angle + corner.y * cos_angle
            rotated_corners.append(pygame.Vector2(rotated_corner_x, rotated_corner_y))

        return rotated_corners
    def line_intersects(self, line1_start, line1_end, line2_start, line2_end):
    
        p = pygame.Vector2(line1_start)
        q = pygame.Vector2(line2_start)
        r = pygame.Vector2(line1_end) - p
        s = pygame.Vector2(line2_end) - q

        if r.cross(s) == 0:
            return False  

       
        t = (q - p).cross(s) / r.cross(s)
        u = (q - p).cross(r) / r.cross(s)


        if 0 <= t <= 1 and 0 <= u <= 1:
            return True

        return False
    def update_sensors(self, track_lines):
        for sensor in self.sensors:
            sensor.update(track_lines)  
    def check_collision(self, track_lines):
        
        rect_points = self.get_rect_points()
        car_lines = list(zip(rect_points, rect_points[1:] + rect_points[:1]))

        for line1_start, line1_end in car_lines:
            for line in track_lines:
                for line2_start, line2_end in zip(line, line[1:]):
                    if self.line_intersects(line1_start, line1_end, line2_start, line2_end):
                        return True
        return False
    
    def draw(self, screen):
 
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, self.color, (0, 0, self.width, self.height))  
        pygame.draw.rect(car_surface, self.front_color, (0, 0, self.width // 2, self.height))  

        rotated_car_surface = pygame.transform.rotate(car_surface, -self.angle)
        new_rect = rotated_car_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_car_surface, new_rect.topleft)
        for sensor in self.sensors:
            sensor.draw(screen)



class Sensor:
    def __init__(self, car, angle_offset, color, max_distance=2000):
        self.car = car
        self.angle_offset = angle_offset  
        self.distance = max_distance
        self.max_distance = max_distance
        self.color = color  # Color for the sensor ray


    def update(self, track_lines):
        self.distance = self.max_distance
        sensor_vector = pygame.Vector2(math.cos(math.radians(self.car.angle + self.angle_offset)),
                                   math.sin(math.radians(self.car.angle + self.angle_offset)))
        sensor_end = pygame.Vector2(self.car.x, self.car.y) + sensor_vector * self.max_distance

        for line in track_lines:
            for start, end in zip(line, line[1:]):
                intersection = self._line_intersects(pygame.Vector2(start), pygame.Vector2(end),
                                                 pygame.Vector2(self.car.x, self.car.y), sensor_end)
                if intersection:
                    distance = (intersection - pygame.Vector2(self.car.x, self.car.y)).length()
                    if distance < self.distance:
                        self.distance = distance
                    break  # Stop checking if we've found an intersection

    def _collides_with_track(self, x, y, track_lines):
        point = pygame.Vector2(x, y)
        for line in track_lines:
            for start, end in zip(line, line[1:]):
                if self._line_intersects(point, pygame.Vector2(start), pygame.Vector2(end)):
                    return True
        return False
    def _line_intersects(self, sensor_start, sensor_end, line_start, line_end):
        # Convert points to vectors
        p = sensor_start
        q = line_start
        r = sensor_end - sensor_start
        s = line_end - line_start
    
        # Check if the vectors are parallel
        if r.cross(s) == 0:
            return None  # Lines are parallel and thus do not intersect
    
        # Calculate the intersection point
        t = (q - p).cross(s) / r.cross(s)
        u = (q - p).cross(r) / r.cross(s)
    
        # Check if intersection is in the correct direction of the ray
        # and within the line segment
        if 0 <= t <= 1 and 0 <= u <= 1:
            return p + t * r
    
        return None
    def draw(self, screen):
        end_x = self.car.x + self.distance * math.cos(math.radians(self.car.angle + self.angle_offset))
        end_y = self.car.y + self.distance * math.sin(math.radians(self.car.angle + self.angle_offset))
        pygame.draw.line(screen, self.color, (self.car.x, self.car.y), (end_x, end_y), 1)
    def cross(self, other):
        return self.x * other.y - self.y * other.x
class CarNN(nn.Module):
    def __init__(self):
        super(CarNN, self).__init__()
        # Adjust for 9 sensor inputs if necessary
        self.fc1 = nn.Linear(9, 128)  # Adjusted from 8 to 9
        self.fc2 = nn.Linear(128, 64) # Second fully connected layer
        self.fc3 = nn.Linear(64, 3)   # Output layer, 3 outputs: accelerate, decelerate, turn

    def forward(self, x):
        x = F.relu(self.fc1(x))  # Activation function after first layer
        x = F.relu(self.fc2(x))  # Activation function after second layer
        x = self.fc3(x)          # No activation function, raw scores
        return x
# Define the Game class
    
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
        self.width, self.height = self.screen.get_size()  # Get current screen size
        self.simulation_width, self.simulation_height = 1280, 720
        pygame.display.set_caption("Race Track Simulation")
        self.track_lines = []
        self.car = Car(640, 360)  # Start in the middle of the simulation area
        self.action = (0, 0)
        self.drawing_goal = False
        self.goal_lines = []
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 18)
        self.car_nn = CarNN()
        self.simulation_width, self.simulation_height = self.width * 0.66, self.height
        self.sensor_info_area = pygame.Rect(self.simulation_width, 0, self.width - self.simulation_width, self.height)
        self.nn_visualizer = NNVisualizer(self.car_nn, self.screen, self.sensor_info_area.topleft, self.sensor_info_area.size)
        self.optimizer = optim.Adam(self.car_nn.parameters(), lr=0.001)
        self.is_training = False  # Flag to control when to train
        self.drawing = False
        self.track_lines = []
        # Dynamically position the buttons at the bottom of the screen
        button_width, button_height = 100, 30
        button_margin = 10
        bottom_margin = 20
        self.clear_button = pygame.Rect(self.width - button_width - button_margin, self.height - bottom_margin - 3 * button_height, button_width, button_height)
        self.save_button = pygame.Rect(self.width - button_width - button_margin, self.height - bottom_margin - 2 * button_height, button_width, button_height)
        self.load_button = pygame.Rect(self.width - button_width - button_margin, self.height - bottom_margin - button_height, button_width, button_height)

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                 return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.drawing_goal:
                    if not self.goal_lines[0]:
                        self.goal_lines[0] = mouse_pos  # Set start point
                    elif not self.goal_lines[1]:
                        self.goal_lines[1] = mouse_pos  # Set end point
                        self.goal_lines.append(self.goal_lines.copy())  # Add completed line to the list
                        self.goal_lines = [None, None]  # Reset for the next line
                if self.clear_button.collidepoint(mouse_pos):
                    self.track_lines.clear()
                elif self.save_button.collidepoint(mouse_pos):
                    # Placeholder for save button functionality
                    print("Save button clicked")
                elif self.load_button.collidepoint(mouse_pos):
                    # Placeholder for load button functionality
                    print("Load button clicked")
                else:
                    self.drawing = True
                    self.track_lines.append([mouse_pos])  # Start a new line
            elif event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False
            elif event.type == pygame.MOUSEMOTION and self.drawing:
                if self.track_lines:  # Check if there's at least one line
                    self.track_lines[-1].append(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.is_training = not self.is_training
                elif event.key == pygame.K_g:
                    self.drawing_goal = True
        return True
    def draw_goal_lines(self):
        for line in self.goal_lines:  # Iterate over all goal lines
            if line[0] and line[1]:  # Check if both points are set
                pygame.draw.line(self.screen, (0, 255, 0), line[0], line[1], 2)  # Draw each green line

    def draw_track(self):
        track_color = (255, 255, 255)  # White color for the track lines
        for line in self.track_lines:
            if len(line) > 1:
                 pygame.draw.lines(self.screen, track_color, False, line, 2)
    def calculate_reward(self):
        # Define your reward function here
        # For example, reward could be negative distance to the center of the track
        return -min(sensor.distance for sensor in self.car.sensors)

    def train(self, state, action, reward, next_state):
        # Convert data to tensors
        state = torch.tensor([state], dtype=torch.float32)
        next_state = torch.tensor([next_state], dtype=torch.float32)
        action = torch.tensor([action], dtype=torch.int64)
        reward = torch.tensor([reward], dtype=torch.float32)

        # Predict Q values for current state
        pred = self.car_nn(state).gather(1, action)

        # Compute the target Q value
        next_pred = self.car_nn(next_state).max(1)[0].detach()
        target = reward + 0.99 * next_pred  # Assume a discount factor of 0.99

        # Calculate loss
        loss = F.smooth_l1_loss(pred, target)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
            
    def convert_nn_output_to_action(self, nn_output):
        # Placeholder example to convert NN output to actions
        # Assuming the NN output has three values: [turn_value, accelerate_value, decelerate_value]
        turn_value = nn_output[0, 0]
        accelerate_value = nn_output[0, 1]
        decelerate_value = nn_output[0, 2]

        # Example control logic (this will need fine-tuning)
        turn_speed = turn_value * 2 - 1  # Convert to range [-1, 1]
        acceleration = accelerate_value - decelerate_value  # Net acceleration

        # Clamp values to the expected ranges for your simulation
        turn_speed = max(-1, min(1, turn_speed))
        acceleration = max(-self.car.max_speed, min(self.car.max_speed, acceleration))

        return (turn_speed, acceleration)
    def draw_ui(self):
        # Define button colors and border thickness
        button_color = (100, 100, 100)  # Dark gray for better contrast
        border_color = (0, 0, 0)  # Black color for the border
        border_thickness = 2
        text_color = (255, 255, 255)  # White text for contrast

        # Function to draw a button with text
        def draw_button(button_rect, text):
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, border_color, button_rect, border_thickness)
            text_surface = self.font.render(text, True, text_color)
            # Centering text in the button
            text_x = button_rect.x + (button_rect.width - text_surface.get_width()) // 2
            text_y = button_rect.y + (button_rect.height - text_surface.get_height()) // 2
            self.screen.blit(text_surface, (text_x, text_y))

        # Draw buttons
        draw_button(self.clear_button, 'Clear')
        draw_button(self.save_button, 'Save')
        draw_button(self.load_button, 'Load')


    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            running = self.handle_events()
            # Update car and sensors
            self.car.update(self.action, self.track_lines)  # Pass 'self.track_lines' here
            self.car.update_sensors(self.track_lines)
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # Clear the screen and draw the track        
            self.screen.fill((0, 0, 0))  # Clear the screen
            self.draw_track()  # Draw the drawn track
            self.car.draw(self.screen)
            self.draw_goal_lines()

            # Handle keys and get action from either NN or user
            if self.is_training:
                # Get sensor values and convert to neural network input
                sensor_values = [sensor.distance for sensor in self.car.sensors]
                sensor_input = torch.tensor([sensor_values], dtype=torch.float32)
                
                # Forward pass through the neural network
                nn_output = self.car_nn(sensor_input)
                
                # Convert neural network output to car actions
                self.action = self.convert_nn_output_to_action(nn_output)
            else:
                # Get action from user input
                self.action = self.handle_keys()
            
            
            # Draw the sensor info area with a white background
            pygame.draw.rect(self.screen, (255, 255, 255), self.sensor_info_area)
            self.draw_sensor_info()
            
            # Draw the neural network visualization
            self.nn_visualizer.draw()
             # Draw the clear button
            self.draw_ui()
            # Update the display
            pygame.display.flip()
            
            # Control the simulation frame rate
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def convert_nn_output_to_action(self, nn_output):
        # Interpret the neural network output and convert to car actions
        # Here you'll implement how the NN output is converted to actions
        # For now, we'll just create a placeholder for the logic
        # This method should return an action tuple (turn, acceleration)
        if nn_output is not None:
            # Example logic for NN output to action conversion
            turn_speed = nn_output[0, 2].item()  # Assuming the third output is for turning
            acceleration = nn_output[0, 1].item() - nn_output[0, 0].item()  # Assuming outputs for acceleration and deceleration
            return (turn_speed, acceleration)
        else:
            # No action if NN output is None
            return (0, 0)
        
    def handle_keys(self):
        # Get user input and convert to car actions
        keys = pygame.key.get_pressed()
        turn_speed = 0
        acceleration = 0
        if keys[pygame.K_a]:
            turn_speed = -1
        elif keys[pygame.K_d]:
            turn_speed = 1
        if keys[pygame.K_w]:
            acceleration = 1
        elif keys[pygame.K_s]:
            acceleration = -1
        return (turn_speed, acceleration)
    
    def draw_sensor_info(self):
        # Draw sensor information in the remaining screen space
        info_area_start_x = self.simulation_width + 10
        sensor_info_background = pygame.Rect(self.simulation_width, 0, self.width - self.simulation_width, self.height)
        pygame.draw.rect(self.screen, (255, 255, 255), sensor_info_background)
        for i, sensor in enumerate(self.car.sensors):
            text_surface = self.font.render(f'Sensor {i+1}: {sensor.distance:.2f}', True, (0, 0, 0))
            self.screen.blit(text_surface, (info_area_start_x, 20 * i + 10))
class NNVisualizer:
    # Initialize with a neural network, the screen to draw on, the top-left position, and the size of the area to draw the NN
    def __init__(self, neural_network, screen, position, size):
        self.neural_network = neural_network
        self.screen = screen
        self.position = position
        self.size = size
        # ... Initialize visualization properties ...

    def draw(self):
        # Draw the neural network nodes and connections
        # Here you will need to implement the logic to visualize the network
        # For now, it just draws a single circle to represent a node
        node_radius = 20
        node_color = (0, 0, 0)
        center_x = self.position[0] + self.size[0] // 2
        center_y = self.position[1] + self.size[1] // 2
        pygame.draw.circle(self.screen, node_color, (center_x, center_y), node_radius)

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()