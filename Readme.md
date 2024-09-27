# Fishband

## Introduction

The **Fishband** project is a simulation of fish schooling behavior with analytical functionalities such as heatmaps, trajectory tracking, and density analysis.

## Fishband Algorithm

The Fishband algorithm implemented in this project is based on the **concentric fishband approach** (inspired by [Fouloscopie video](https://www.youtube.com/watch?v=Ch7VxxTBe1c)). This method is simpler than other fish schooling algorithms yet effective. The algorithm involves creating three zones (concentric circles) around each fish to dictate its behavior based on the proximity of other fish:

1. **Avoidance zone** (innermost circle): If another fish gets too close, the fish moves away to avoid collision.
2. **Alignment zone** (middle circle): If a fish is within the optimal distance, the fish aligns its direction with the nearby fish.
3. **Cohesion zone** (outermost circle): If a fish is too far away, the fish moves closer to the group to maintain cohesion.

## Analytics Functionalities

### 1. **Heatmap**

The heatmap represents the frequency of fish passing through specific areas of the simulation space. It helps visualize high-traffic zones and provides insights into fish movement patterns.

### 2. **Fish Trajectories**

Fish trajectories track the paths taken by individual fish over time. These trajectories can be plotted to analyze movement patterns and behavior over the simulation duration.

### 3. **Fish Density**

Fish density analysis calculates the average number of fish present in different regions of the simulation space. This data helps identify clustering patterns and how the density evolves over time.

---

### Code Overview

The simulation uses the **Pygame** library for real-time rendering and interaction with fish, and **matplotlib** for saving analytical visualizations like heatmaps and density curves.

Main classes:

- **Fish**: Represents individual fish with properties like position, direction, speed, and behavior (separation, alignment, and cohesion).
- **QuadTree**: Efficiently handles spatial partitioning to manage fish interactions based on proximity.
- **Rectangle/Circle**: Helper classes for managing boundaries and collision checks.

---

### Running the Simulation

1. **Start and Stop Simulation**: Use the UI buttons to start or stop the fish simulation. The fish will move and interact based on the rules of the concentric fishband algorithm.
2. **Adjust Fish Count**: You can input the number of fish in the simulation using the "Fish Count" input field and update it in real-time.
3. **Boundary Behavior Toggle**: Use the toggle to switch between boundary wrapping (fish reappear on the opposite side of the screen) and boundary bounce (fish bounce off screen edges).
4. **Analytics Experiments**: Launch different analytics experiments from the UI:
   - **Zone Frequency**: Creates a heatmap based on fish movement frequencies.
   - **Fish Trajectories**: Tracks and visualizes individual fish trajectories.
   - **Fish Density**: Measures the average density of fish in different grid regions over time.

### How to Launch an Experience

1. Click on "Launch Experience".
2. Select the type of experiment (zone frequency, fish trajectories, or fish density).
3. Set the duration (in seconds).
4. Start the experiment, and the simulation will run with analytics being collected.

Results will be saved in the `results/` directory, with heatmaps and trajectories saved as `.png` images, and density data saved as `.npy` files for further analysis.

---

### Requirements

- **Python 3.x**
- **Pygame**
- **NumPy**
- **Matplotlib**
- **pygame_gui**
- **termcolor**

To install the dependencies:

```bash
pip install pygame numpy matplotlib pygame_gui termcolor
```

### Logging

The simulation logs important events and errors to `fish_simulation.log` for troubleshooting and performance monitoring.

---

This README now contains correct grammar and structure, improving clarity and readability. Here's a breakdown of some key corrections made:

- **"Comportment"** was corrected to "behavior".
- **"Approch"** was corrected to "approach".
- Some missing conjunctions, prepositions, and articles were added to improve flow and make the text grammatically correct.

Let me know if you'd like to modify or expand any other sections!
