# menu.py

import pygame
import sys
import os
import initialtrack  # Import the script you want to link to

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Menu Page for Car Simulation")

# Load background image
background_image_path = os.path.join("Assets", "menu_background.jpg")
original_background = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(original_background, (width, height))

# Load button images
start_button_image = pygame.image.load(os.path.join("Assets", "start_btn.png"))
exit_button_image = pygame.image.load(os.path.join("Assets", "exit_btn.png"))

# Fonts
font = pygame.font.Font(None, 36)

# Texts
title_text = font.render("Car Simulation Menu", True, (0, 0, 0))

# Rectangles for buttons
button_width, button_height = 120, 30
start_button_rect = start_button_image.get_rect(topleft=(230, 250), width=button_width, height=button_height)
exit_button_rect = exit_button_image.get_rect(topleft=(430, 250), width=button_width, height=button_height)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                print("Start button clicked")
                # Link to the initialtrack.py script
                initialtrack.main()  # Assuming there's a main function in initialtrack.py
            elif exit_button_rect.collidepoint(event.pos):
                print("Exit button clicked")
                pygame.quit()
                sys.exit()

    # Draw background image
    screen.blit(background_image, (0, 0))

    # Draw title
    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 100))

    # Draw buttons
    screen.blit(start_button_image, start_button_rect)
    screen.blit(exit_button_image, exit_button_rect)

    # Update display
    pygame.display.flip()

    # Control frame rate
    pygame.time.Clock().tick(60)
