"""
Particle Life / Swarm Intelligence Animation
Particles attract or repel based on species, creating organic movement.
"""

import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import project_point, rotate_y


class ParticleSystem:
    """Manages a system of particles with species-based interactions."""
    
    def __init__(self, num_particles=150, num_species=5):
        self.num_particles = num_particles
        self.num_species = num_species
        self.particles = []
        self.velocities = []
        self.species = []
        
        # Interaction matrix: how each species affects others
        # Positive = attraction, Negative = repulsion
        self.interactions = []
        
        self.reset()
    
    def reset(self):
        """Initialize particles with random positions and species."""
        self.particles = []
        self.velocities = []
        self.species = []
        
        for _ in range(self.num_particles):
            # Random position in 3D space
            self.particles.append([
                random.uniform(-3, 3),
                random.uniform(-3, 3),
                random.uniform(-3, 3)
            ])
            self.velocities.append([0.0, 0.0, 0.0])
            self.species.append(random.randint(0, self.num_species - 1))
        
        # Random interaction matrix
        self.interactions = []
        for i in range(self.num_species):
            row = []
            for j in range(self.num_species):
                # Random attraction/repulsion between -1 and 1
                row.append(random.uniform(-0.5, 0.5))
            self.interactions.append(row)
    
    def update(self, dt=0.02):
        """Update particle positions based on interactions."""
        friction = 0.98
        max_speed = 0.5
        min_distance = 0.3
        max_distance = 3.0
        
        # Calculate forces
        forces = [[0.0, 0.0, 0.0] for _ in range(self.num_particles)]
        
        for i in range(self.num_particles):
            for j in range(self.num_particles):
                if i == j:
                    continue
                
                # Distance between particles
                dx = self.particles[j][0] - self.particles[i][0]
                dy = self.particles[j][1] - self.particles[i][1]
                dz = self.particles[j][2] - self.particles[i][2]
                
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist < 0.01:
                    continue
                
                # Normalize direction
                dx /= dist
                dy /= dist
                dz /= dist
                
                # Get interaction strength
                interaction = self.interactions[self.species[i]][self.species[j]]
                
                # Force calculation with distance falloff
                if dist < min_distance:
                    # Strong repulsion when too close
                    force = -1.0 / (dist * dist)
                elif dist < max_distance:
                    # Apply species interaction
                    force = interaction / (dist + 1)
                else:
                    force = 0
                
                forces[i][0] += dx * force
                forces[i][1] += dy * force
                forces[i][2] += dz * force
        
        # Apply forces to velocities
        for i in range(self.num_particles):
            self.velocities[i][0] += forces[i][0] * dt
            self.velocities[i][1] += forces[i][1] * dt
            self.velocities[i][2] += forces[i][2] * dt
            
            # Apply friction
            self.velocities[i][0] *= friction
            self.velocities[i][1] *= friction
            self.velocities[i][2] *= friction
            
            # Limit speed
            speed = math.sqrt(
                self.velocities[i][0]**2 + 
                self.velocities[i][1]**2 + 
                self.velocities[i][2]**2
            )
            if speed > max_speed:
                self.velocities[i][0] *= max_speed / speed
                self.velocities[i][1] *= max_speed / speed
                self.velocities[i][2] *= max_speed / speed
            
            # Update position
            self.particles[i][0] += self.velocities[i][0]
            self.particles[i][1] += self.velocities[i][1]
            self.particles[i][2] += self.velocities[i][2]
            
            # Wrap around boundaries
            for axis in range(3):
                if self.particles[i][axis] > 4:
                    self.particles[i][axis] = -4
                elif self.particles[i][axis] < -4:
                    self.particles[i][axis] = 4


# Global particle system
_particle_system = None


def render_particles(buffer, width, height, time, theme_manager):
    """
    Render the particle life simulation.
    
    Features:
    - Multiple species with different behaviors
    - Organic emergent patterns
    - 3D rotation for viewing angle
    """
    global _particle_system
    
    # Initialize or reset if needed
    if _particle_system is None:
        _particle_system = ParticleSystem(num_particles=120, num_species=5)
    
    # Update simulation
    _particle_system.update(dt=0.03)
    
    # Rotation angle for 3D view
    rot_y = time * 0.2
    
    # Species characters (different for each species)
    species_chars = ['●', '○', '◆', '◇', '★']
    species_chars_fallback = ['@', 'O', '#', '*', '+']
    
    all_z = []
    points_to_draw = []
    
    for i, particle in enumerate(_particle_system.particles):
        x, y, z = particle
        
        # Apply rotation
        rotated = rotate_y((x, y, z), rot_y)
        x, y, z = rotated
        
        # Project to 2D
        proj = project_point(x, y, z, width, height, distance=8)
        if proj:
            sx, sy = proj
            species = _particle_system.species[i]
            all_z.append(z)
            points_to_draw.append((sx, sy, z, species))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    # Draw particles
    for sx, sy, z, species in points_to_draw:
        char = species_chars_fallback[species % len(species_chars_fallback)]
        
        # Color based on depth and species
        # Mix species hue with depth
        normalized_z = (z - z_min) / (z_max - z_min + 0.001)
        
        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        
        buffer.set_pixel(sx, sy, char, z, color)
        # Add slight glow effect
        buffer.set_pixel(sx + 1, sy, '.', z + 0.1, color)
        buffer.set_pixel(sx - 1, sy, '.', z + 0.1, color)
    
    return (z_min, z_max)
