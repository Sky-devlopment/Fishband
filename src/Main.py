import pygame
import random
import math
import numpy as np
from termcolor import colored
from modules.vector_v1 import Vector
import pygame_gui
import os
from datetime import datetime
from matplotlib import pyplot as plt
import traceback
import logging

# Initialize Pygame
pygame.init()

logging.basicConfig(filename='fish_simulation.log', level=logging.DEBUG)

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fishband")

# Set custom logo
logo = pygame.image.load("data/icon/fish.png")  # Replace with the path to your logo file
pygame.display.set_icon(logo)

# GUI manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'data/themes/theme.json')

# Buttons and UI elements
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                            text='Start',
                                            manager=manager)
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (100, 50)),
                                           text='Stop',
                                           manager=manager)
experience_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((230, 10), (150, 50)),
                                                 text='Launch Experience',
                                                 manager=manager)
bounce_toggle = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((390, 10), (150, 50)),
                                             text='Toggle Bounce',
                                             manager=manager)
fish_count_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((550, 10), (100, 50)),
                                               text='Fish Count:',
                                               manager=manager)
fish_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((660, 10), (50, 50)),
                                                       manager=manager)
update_fish_count = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((720, 10), (100, 50)),
                                                 text='Update',
                                                 manager=manager)

# Popup for experience settings
experience_window = None
experience_dropdown = None
duration_entry = None
start_experience_button = None

fish_count = 5
boundary_behavior_enabled = False

class Fish:
    def __init__(self, id):
        self.id = id
        self.speed = random.uniform(1.5, 2.5)
        self.direction = Vector(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.pos = Vector(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.color = (0, random.randint(100, 255), random.randint(200, 255))
        self.trajectory = []
        self.size = random.randint(3, 7)

    def move(self, quadtree):
        nearby = quadtree.query(self.pos.x, self.pos.y, 75)
        
        separation = self.separate(nearby)
        alignment = self.align(nearby)
        cohesion = self.cohere(nearby)
        
        self.direction = (self.direction + separation * 0.03 + alignment * 0.05 + cohesion * 0.03).normalize()
        self.pos += self.direction * self.speed

        if boundary_behavior_enabled:
            if self.pos.x <= 0 or self.pos.x >= WIDTH:
                self.direction.x *= -1
            if self.pos.y <= 0 or self.pos.y >= HEIGHT:
                self.direction.y *= -1
        else:
            self.pos.x %= WIDTH
            self.pos.y %= HEIGHT

        self.trajectory.append((int(self.pos.x), int(self.pos.y)))
        if len(self.trajectory) > 100:
            self.trajectory.pop(0)

    def separate(self, nearby):
        steering = Vector(0, 0)
        for fish in nearby:
            if fish.id != self.id:
                diff = self.pos - fish.pos
                if diff.norm < 25:
                    steering += diff.normalize()
        return steering

    def align(self, nearby):
        steering = Vector(0, 0)
        count = 0
        for fish in nearby:
            if fish.id != self.id:
                steering += fish.direction
                count += 1
        if count > 0:
            steering /= count
            steering = steering.normalize()
        return steering

    def cohere(self, nearby):
        steering = Vector(0, 0)
        count = 0
        for fish in nearby:
            if fish.id != self.id:
                steering += fish.pos
                count += 1
        if count > 0:
            steering /= count
            steering = (steering - self.pos).normalize()
        return steering

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.size)
        end_pos = self.pos + self.direction * 10
        pygame.draw.line(screen, self.color, (int(self.pos.x), int(self.pos.y)), 
                         (int(end_pos.x), int(end_pos.y)), 2)

class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.fishes = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def insert(self, fish):
        if not self.boundary.contains(fish.pos):
            return False

        if len(self.fishes) < self.capacity:
            self.fishes.append(fish)
            return True

        if not self.divided:
            self.subdivide()

        return (self.northwest.insert(fish) or
                self.northeast.insert(fish) or
                self.southwest.insert(fish) or
                self.southeast.insert(fish))

    def subdivide(self):
        x, y = self.boundary.x, self.boundary.y
        w, h = self.boundary.w / 2, self.boundary.h / 2

        self.northwest = QuadTree(Rectangle(x, y, w, h), self.capacity)
        self.northeast = QuadTree(Rectangle(x + w, y, w, h), self.capacity)
        self.southwest = QuadTree(Rectangle(x, y + h, w, h), self.capacity)
        self.southeast = QuadTree(Rectangle(x + w, y + h, w, h), self.capacity)

        self.divided = True

    def query(self, x, y, radius):
        result = []
        if not self.boundary.intersects(Circle(x, y, radius)):
            return result

        for fish in self.fishes:
            if (fish.pos.x - x)**2 + (fish.pos.y - y)**2 <= radius**2:
                result.append(fish)

        if self.divided:
            result.extend(self.northwest.query(x, y, radius))
            result.extend(self.northeast.query(x, y, radius))
            result.extend(self.southwest.query(x, y, radius))
            result.extend(self.southeast.query(x, y, radius))

        return result

class Rectangle:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def contains(self, point):
        return (self.x <= point.x < self.x + self.w and
                self.y <= point.y < self.y + self.h)

    def intersects(self, circle):
        dx = abs(circle.x - (self.x + self.w/2))
        dy = abs(circle.y - (self.y + self.h/2))

        if dx > (self.w/2 + circle.r): return False
        if dy > (self.h/2 + circle.r): return False

        if dx <= (self.w/2): return True
        if dy <= (self.h/2): return True

        corner_distance_sq = (dx - self.w/2)**2 + (dy - self.h/2)**2

        return corner_distance_sq <= (circle.r**2)

class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

def create_fish(nb: int):
    fishes = []
    for i in range(nb):
        fishes.append(Fish(id=i))
    print(colored("🐟 @fcv1.0 ", "blue") + "process complete!")
    return fishes

def run_experience(experience_type, duration):
    try:
        # Fix for experience_type being a tuple
        if isinstance(experience_type, tuple):
            experience_type = experience_type[0]
        
        logging.info(f"Starting experience: {experience_type} for {duration} seconds")
        fishes = create_fish(fish_count)
        clock = pygame.time.Clock()
        running = True
        start_time = pygame.time.get_ticks()

        if experience_type == 'zone_frequency':
            heatmap = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
        elif experience_type == 'fish_trajectories':
            trajectories = {fish.id: [] for fish in fishes}
        elif experience_type == 'fish_density':
            densities = []
            grid_size = 50  # Size of each grid cell for density measurement
            grid_rows = HEIGHT // grid_size
            grid_cols = WIDTH // grid_size
        else:
            logging.error(f"Unknown experience type: {experience_type}")
            return

        while running:
            time_elapsed = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
            if time_elapsed >= duration:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))  # White background

            quadtree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), 4)
            for fish in fishes:
                quadtree.insert(fish)

            if experience_type == 'fish_density':
                grid = np.zeros((grid_rows, grid_cols))

            for fish in fishes:
                fish.move(quadtree)
                fish.draw(screen)

                if experience_type == 'zone_frequency':
                    x, y = int(fish.pos.x), int(fish.pos.y)
                    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                        heatmap[y, x] += 1
                elif experience_type == 'fish_trajectories':
                    trajectories[fish.id].append((int(fish.pos.x), int(fish.pos.y)))
                elif experience_type == 'fish_density':
                    row = int(fish.pos.y) // grid_size
                    col = int(fish.pos.x) // grid_size
                    if 0 <= row < grid_rows and 0 <= col < grid_cols:
                        grid[row, col] += 1

            if experience_type == 'fish_density':
                avg_density = np.mean(grid)
                densities.append(avg_density)

            pygame.display.flip()
            clock.tick(60)

        logging.info("Experience completed. Preparing to save results.")
        logging.debug(f"Experience type: {experience_type}")

        # Create results directory if it doesn't exist
        results_dir = "./results/"
        try:
            os.makedirs(results_dir, exist_ok=True)
            logging.info(f"Results directory created/confirmed: {results_dir}")
        except Exception as e:
            logging.error(f"Failed to create results directory: {e}")
            raise

        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if experience_type == 'zone_frequency':
            try:
                if np.max(heatmap) == 0:
                    logging.warning("Heatmap is empty. No fish movements detected.")
                    return

                # Normalize the heatmap
                heatmap = heatmap / np.max(heatmap)

                # Create a custom colormap
                colors = [(0,0,0), (0,0,1), (0,1,1), (0,1,0), (1,1,0), (1,0,0), (1,0,1)]  # Black, Blue, Cyan, Green, Yellow, Red, Violet
                n_bins = 100  # Number of bins in the colormap
                cmap = plt.cm.colors.LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

                # Apply the colormap to the heatmap
                colored_heatmap = cmap(heatmap)

                # Convert to 8-bit RGB
                colored_heatmap_8bit = (colored_heatmap[:, :, :3] * 255).astype(np.uint8)

                # Transpose the heatmap to switch from portrait to landscape
                colored_heatmap_8bit = np.transpose(colored_heatmap_8bit, (1, 0, 2))

                # Create a surface with the correct dimensions (WIDTH x HEIGHT)
                heatmap_surface = pygame.Surface((WIDTH, HEIGHT))

                # Use surfarray.blit_array to apply the colored heatmap to the surface
                pygame.surfarray.blit_array(heatmap_surface, colored_heatmap_8bit)

                filename = os.path.join(results_dir, f"heatmap_{timestamp}.png")
                pygame.image.save(heatmap_surface, filename)
                logging.info(f"Heatmap saved as {filename}")
                print(f"Heatmap saved as {filename}")

            except Exception as e:
                logging.error(f"Failed to save heatmap: {e}")
                logging.error(traceback.format_exc())
                print(f"Error saving heatmap: {e}")

        elif experience_type == 'fish_trajectories':
            try:
                logging.debug(f"Number of trajectories: {len(trajectories)}")
                trajectory_surface = pygame.Surface((WIDTH, HEIGHT))
                trajectory_surface.fill((255, 255, 255))
                for fish_id, traj in trajectories.items():
                    logging.debug(f"Fish {fish_id} trajectory length: {len(traj)}")
                    color = fishes[fish_id].color
                    if len(traj) > 1:  # We need at least 2 points to draw a line
                        pygame.draw.lines(trajectory_surface, color, False, traj, 1)
                    else:
                        logging.warning(f"Fish {fish_id} has insufficient trajectory points: {traj}")
                filename = os.path.join(results_dir, f"trajectories_{timestamp}.png")
                pygame.image.save(trajectory_surface, filename)
                logging.info(f"Trajectories saved as {filename}")
                print(f"Trajectories saved as {filename}")
            except Exception as e:
                logging.error(f"Failed to save trajectories: {e}")
                logging.error(traceback.format_exc())
                print(f"Error saving trajectories: {e}")
        elif experience_type == 'fish_density':
            try:
                plt.figure(figsize=(10, 6))
                plt.plot(range(len(densities)), densities)
                plt.xlabel('Time (frames)')
                plt.ylabel('Average Fish Density')
                plt.title('Average Fish Density Over Time')
                filename = os.path.join(results_dir, f"fish_density_{timestamp}.png")
                plt.savefig(filename)
                plt.close()  # Close the plot to free up memory
                logging.info(f"Fish density curve saved as {filename}")
                print(f"Fish density curve saved as {filename}")

                # Also save the raw data
                np.save(os.path.join(results_dir, f"fish_density_data_{timestamp}.npy"), np.array(densities))
            except Exception as e:
                logging.error(f"Failed to save fish density data: {e}")
                logging.error(traceback.format_exc())
                print(f"Error saving fish density data: {e}")
    except Exception as e:
        logging.error(f"An error occurred during the experience: {e}")
        logging.error(traceback.format_exc())
        print(f"An error occurred: {e}")

def main():
    global fish_count, boundary_behavior_enabled
    fishes = create_fish(fish_count)
    clock = pygame.time.Clock()
    running = True
    simulating = False

    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    simulating = True
                elif event.ui_element == stop_button:
                    simulating = False
                elif event.ui_element == experience_button:
                    show_experience_popup()
                elif event.ui_element == bounce_toggle:
                    boundary_behavior_enabled = not boundary_behavior_enabled
                    bounce_toggle.set_text('Bounce: ' + ('On' if boundary_behavior_enabled else 'Off'))
                elif event.ui_element == update_fish_count:
                    try:
                        new_count = int(fish_count_entry.get_text())
                        if new_count > 0:
                            fish_count = new_count
                            fishes = create_fish(fish_count)
                        else:
                            print("Fish count must be a positive integer.")
                    except ValueError:
                        print("Invalid fish count. Please enter a number.")
                elif event.ui_element == start_experience_button:
                    selected_experience = experience_dropdown.selected_option
                    try:
                        duration = int(duration_entry.get_text())
                        experience_window.kill()
                        run_experience(selected_experience, duration)
                    except ValueError:
                        print("Invalid duration. Please enter a number.")

            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                if event.ui_element == experience_window:
                    experience_window.kill()

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill((255, 255, 255))  # White background

        if simulating:
            quadtree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), 4)
            for fish in fishes:
                quadtree.insert(fish)

            for fish in fishes:
                fish.move(quadtree)
                fish.draw(screen)

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

def show_experience_popup():
    global experience_window, experience_dropdown, duration_entry, start_experience_button
    experience_window = pygame_gui.elements.UIWindow(
        pygame.Rect(400, 200, 400, 300),
        manager,
        window_display_title='Launch Experience'
    )

    experience_dropdown = pygame_gui.elements.UIDropDownMenu(
        ['zone_frequency', 'fish_trajectories', 'fish_density'],
        'zone_frequency',
        pygame.Rect(20, 20, 360, 30),
        manager,
        container=experience_window
    )

    duration_label = pygame_gui.elements.UILabel(
        pygame.Rect(20, 70, 200, 30),
        "Duration (seconds):",
        manager,
        container=experience_window
    )

    duration_entry = pygame_gui.elements.UITextEntryLine(
        pygame.Rect(220, 70, 160, 30),
        manager,
        container=experience_window
    )

    start_experience_button = pygame_gui.elements.UIButton(
        pygame.Rect(120, 200, 160, 50),
        'Start Experience',
        manager,
        container=experience_window
    )

if __name__ == "__main__":
    main()