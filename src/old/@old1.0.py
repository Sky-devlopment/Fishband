# v1.py
import pygame
import random
import math
import numpy as np
from termcolor import colored
from modules.vector_v1 import Vector
import pygame_gui

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Band Simulation Advanced")

# GUI manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Buttons
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((10, 10), (100, 50)),
                                            text='Start',
                                            manager=manager)
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((120, 10), (100, 50)),
                                           text='Stop',
                                           manager=manager)
experience_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((230, 10), (150, 50)),
                                                 text='Launch Experience',
                                                 manager=manager)

class Fish:
    def __init__(self, id):
        self.id = id
        self.speed = 2
        self.direction = Vector(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.pos = Vector(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.trajectory = []

    def move(self, quadtree):
        nearby = quadtree.query(self.pos.x, self.pos.y, 75)
        
        separation = self.separate(nearby)
        alignment = self.align(nearby)
        cohesion = self.cohere(nearby)
        
        self.direction = (self.direction + separation * 0.03 + alignment * 0.05 + cohesion * 0.03).normalize()
        self.pos += self.direction * self.speed
        
        self.pos.x %= WIDTH
        self.pos.y %= HEIGHT

        self.trajectory.append((int(self.pos.x), int(self.pos.y)))
        if len(self.trajectory) > 100:  # Limit trajectory length
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
            steering = steering.normalize() * self.speed - self.direction
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
            return (steering - self.pos).normalize() * self.speed - self.direction
        return steering

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), 5)
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
    print(colored("🐟 @fcv1.0 ", "blue") + "processus complete !")
    return fishes

def run_experience(experience_type, duration):
    fishes = create_fish(200)
    clock = pygame.time.Clock()
    running = True
    start_time = pygame.time.get_ticks()

    if experience_type == 'zone_frequency':
        heatmap = np.zeros((HEIGHT, WIDTH))
    elif experience_type == 'fish_trajectories':
        trajectories = {fish.id: [] for fish in fishes}

    while running:
        time_elapsed = (pygame.time.get_ticks() - start_time) / 1000  # Convert to seconds
        if time_elapsed >= duration:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        quadtree = QuadTree(Rectangle(0, 0, WIDTH, HEIGHT), 4)
        for fish in fishes:
            quadtree.insert(fish)

        for fish in fishes:
            fish.move(quadtree)
            fish.draw(screen)

            if experience_type == 'zone_frequency':
                heatmap[int(fish.pos.y), int(fish.pos.x)] += 1
            elif experience_type == 'fish_trajectories':
                trajectories[fish.id].append((int(fish.pos.x), int(fish.pos.y)))

        pygame.display.flip()
        clock.tick(60)

    if experience_type == 'zone_frequency':
        heatmap = heatmap / np.max(heatmap)
        heatmap_surface = pygame.surfarray.make_surface(heatmap * 255)
        pygame.image.save(heatmap_surface, "heatmap.png")
        print("Heatmap saved as heatmap.png")
    elif experience_type == 'fish_trajectories':
        trajectory_surface = pygame.Surface((WIDTH, HEIGHT))
        trajectory_surface.fill((0, 0, 0))
        for fish_id, traj in trajectories.items():
            color = fishes[fish_id].color
            pygame.draw.lines(trajectory_surface, color, False, traj, 1)
        pygame.image.save(trajectory_surface, "trajectories.png")
        print("Trajectories saved as trajectories.png")

def main():
    fishes = create_fish(200)
    clock = pygame.time.Clock()
    running = True
    simulating = False

    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_button:
                        simulating = True
                    elif event.ui_element == stop_button:
                        simulating = False
                    elif event.ui_element == experience_button:
                        experience_type = random.choice(['zone_frequency', 'fish_trajectories'])
                        duration = random.randint(10, 30)  # Random duration between 10 and 30 seconds
                        print(f"Running {experience_type} experience for {duration} seconds")
                        run_experience(experience_type, duration)

            manager.process_events(event)

        manager.update(time_delta)

        screen.fill((255, 255, 255))

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

if __name__ == "__main__":
    main()