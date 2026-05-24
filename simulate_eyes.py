import pygame
import math
import random
import os
import sys

# Screen dimensions
WIDTH, HEIGHT = 480, 240
DISPLAY_SIZE = 240
CENTER_L = (120, 120)
CENTER_R = (360, 120)

# Colors
BLACK = (0, 0, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dual GC9A01 Eye Simulation")
    clock = pygame.time.Clock()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    sclera_path = os.path.join(base_dir, "assets", "sclera.png")
    iris_path = os.path.join(base_dir, "assets", "iris.png")

    if not os.path.exists(sclera_path) or not os.path.exists(iris_path):
        print("Error: Missing image assets in the 'assets' folder.")
        sys.exit(1)

    sclera_img = pygame.image.load(sclera_path).convert_alpha()
    iris_img = pygame.image.load(iris_path).convert_alpha()

    # Scale images
    sclera_img = pygame.transform.smoothscale(sclera_img, (DISPLAY_SIZE, DISPLAY_SIZE))
    iris_img = pygame.transform.smoothscale(iris_img, (100, 100))

    iris_radius = 50

    # Eye movement state
    target_x, target_y = 0, 0
    current_x, current_y = 0, 0
    move_timer = 0
    
    # Maximum distance the iris can move from center
    # Sclera is 240. Radius 120. Iris is 100, radius 50. Max offset = 120 - 50 = 70. Let's use 60 to be safe.
    max_offset = 60

    running = True
    while running:
        dt = clock.tick(60)
        move_timer -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if move_timer <= 0:
            # Pick a new random target for the eyes
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, max_offset)
            target_x = math.cos(angle) * distance
            target_y = math.sin(angle) * distance
            # Random wait time between 0.5s and 2s
            move_timer = random.randint(500, 2000)
            
        # Smoothly interpolate towards target
        current_x += (target_x - current_x) * 0.1
        current_y += (target_y - current_y) * 0.1

        # --- 3D Spherical Projection Math ---
        d = math.hypot(current_x, current_y)
        R = 120.0 # Radius of the eyeball
        d = min(d, R - 1)
        
        cos_theta = math.cos(math.asin(d / R))
        phi = math.atan2(current_y, current_x)
        
        # Squash and rotate the iris using Pygame transforms
        squashed_width = max(1, int(100 * cos_theta))
        squashed_iris = pygame.transform.smoothscale(iris_img, (squashed_width, 100))
        angle_deg = math.degrees(-phi)
        rotated_iris = pygame.transform.rotate(squashed_iris, angle_deg)
        
        screen.fill(BLACK)

        # Draw Left Eye
        screen.blit(sclera_img, (0, 0))
        rect_l = rotated_iris.get_rect(center=(CENTER_L[0] + current_x, CENTER_L[1] + current_y))
        screen.blit(rotated_iris, rect_l.topleft)

        # Draw Right Eye
        screen.blit(sclera_img, (240, 0))
        rect_r = rotated_iris.get_rect(center=(CENTER_R[0] + current_x, CENTER_R[1] + current_y))
        screen.blit(rotated_iris, rect_r.topleft)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
