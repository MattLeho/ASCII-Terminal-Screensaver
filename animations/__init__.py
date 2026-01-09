"""
Animations Package
Contains all procedural animation modules.
"""

from .helix import render_helix
from .torus import render_torus
from .sphere import render_sphere
from .cube import render_cube
from .tetrahedron import render_tetrahedron
from .lorenz import render_lorenz
from .mobius import render_mobius
from .klein import render_klein
from .lissajous import render_lissajous
from .rose import render_rose
from .wave_grid import render_wave_grid
from .matrix_rain import render_matrix_rain
from .starfield import render_starfield
from .superformula import render_superformula
from .terrain import render_terrain
from .julia import render_julia, render_mandelbrot
from .particles import render_particles
from .raymarch import render_raymarch

# Animation registry for menu system
# Each animation has a recommended theme for optimal 3D visualization

from .screensavers import ss_gerstner, ss_kleinian, ss_synthwave, ss_warp, ss_hyperbolic
from .screensavers import ss_mandelbulb, ss_phyllotaxis, ss_gyroid, ss_potential, ss_jellyfish, ss_transparent_fish, ss_betta_fish, ss_blackhole, ss_galaxy
from .screensavers import ss_ecg, ss_isovalues, ss_clouds

# Time & Utility imports
from .time import (
    t_gravity_clock, t_metaball_clock, t_matrix_clock, t_shadow_clock,
    t_starwars, t_typist,
    t_water_timer, t_circular_fuse, t_life_timer, t_hourglass, t_planetary,
    t_fire_clock, t_plasma_clock, t_snow_clock
)

# Animation registry for menu system
ANIMATIONS = {
    "helix": {
        "name": "DNA Double Helix",
        "description": "Two intertwined helical strands with base pairs",
        "render": render_helix,
        "recommended_theme": "toxic",
    },
    "torus": {
        "name": "Torus (Donut)",
        "description": "Classic spinning donut with depth shading",
        "render": render_torus,
        "recommended_theme": "sunset",
    },
    "sphere": {
        "name": "Wireframe Sphere",
        "description": "Rotating globe with latitude/longitude lines",
        "render": render_sphere,
        "recommended_theme": "arctic",
    },
    "cube": {
        "name": "Rotating Cube",
        "description": "3D wireframe cube spinning on all axes",
        "render": render_cube,
        "recommended_theme": "rainbow",
    },
    "tetrahedron": {
        "name": "Tetrahedron",
        "description": "4-sided pyramid wireframe",
        "render": render_tetrahedron,
        "recommended_theme": "gold",
    },
    "lorenz": {
        "name": "Lorenz Attractor",
        "description": "Chaos theory butterfly pattern",
        "render": render_lorenz,
        "recommended_theme": "plasma",
    },
    "mobius": {
        "name": "Möbius Strip",
        "description": "Single-sided surface with half twist",
        "render": render_mobius,
        "recommended_theme": "lavender",
    },
    "klein": {
        "name": "Klein Bottle",
        "description": "4D shape that passes through itself",
        "render": render_klein,
        "recommended_theme": "rainbow",
    },
    "lissajous": {
        "name": "Lissajous Knots",
        "description": "Complex 3D oscillating curves",
        "render": render_lissajous,
        "recommended_theme": "neon",
    },
    "rose": {
        "name": "Rose Curves (3D)",
        "description": "Mathematical flower patterns",
        "render": render_rose,
        "recommended_theme": "sunset",
    },
    "wave_grid": {
        "name": "Sine Wave Grid",
        "description": "Rippling water surface",
        "render": render_wave_grid,
        "recommended_theme": "ocean",
    },
    "matrix_rain": {
        "name": "Matrix Rain 3D",
        "description": "Falling characters in 3D tunnel",
        "render": render_matrix_rain,
        "recommended_theme": "matrix",
    },
    "starfield": {
        "name": "Starfield / Warp Speed",
        "description": "Flying through space with glow",
        "render": render_starfield,
        "recommended_theme": "void",
    },
    "superformula": {
        "name": "Superformula",
        "description": "Shape-shifting mathematical surface",
        "render": render_superformula,
        "recommended_theme": "plasma",
    },
    "terrain": {
        "name": "Perlin Noise Terrain",
        "description": "Infinite scrolling landscape",
        "render": render_terrain,
        "recommended_theme": "forest",
    },
    "julia": {
        "name": "Julia Set / Mandelbrot",
        "description": "Animated 3D fractal projection",
        "render": render_julia,
        "recommended_theme": "plasma",
    },
    "particles": {
        "name": "Particle Life / Swarm",
        "description": "Emergent swarm intelligence behavior",
        "render": render_particles,
        "recommended_theme": "neon",
    },
    "raymarch": {
        "name": "Raymarching SDF",
        "description": "Real-time volumetric rendering with lighting",
        "render": render_raymarch,
        "recommended_theme": "copper",
    }
}

SCREENSAVERS_ULTRAWIDE = {
    "gerstner": {
        "name": "M-16 Geometrics Ocean",
        "description": "Photorealistic Gerstner Waves",
        "render": ss_gerstner.render,
        "recommended_theme": "ocean"
    },
    "kleinian": {
        "name": "M-17 Kleinian Limit",
        "description": "Schottky Group Fractals",
        "render": ss_kleinian.render,
        "recommended_theme": "rainbow"
    },
    "synthwave": {
        "name": "M-18 Synthwave Terrain",
        "description": "Retro Fourier Landscape",
        "render": ss_synthwave.render,
        "recommended_theme": "neon"
    },
    "warp": {
        "name": "M-19 Domain Warping",
        "description": "Fluid Noise Simulation",
        "render": ss_warp.render,
        "recommended_theme": "plasma"
    },
    "hyperbolic": {
        "name": "M-20 Hyperbolic Flight",
        "description": "Poincaré Disk Travel",
        "render": ss_hyperbolic.render,
        "recommended_theme": "matrix"
    },
    "ecg": {
        "name": "M-31 Electrocardiogram",
        "description": "Traveling ECG Heartbeat Pulse",
        "render": ss_ecg.render,
        "recommended_theme": "matrix"
    }
}

SCREENSAVERS_REGULAR = {
    "mandelbulb": {
        "name": "M-21 Mandelbulb",
        "description": "Ray-marched 3D Fractal",
        "render": ss_mandelbulb.render,
        "recommended_theme": "fire"
    },
    "phyllotaxis": {
        "name": "M-22 Phyllotaxis",
        "description": "Dynamic Sunflower Spirals",
        "render": ss_phyllotaxis.render,
        "recommended_theme": "gold"
    },
    "gyroid": {
        "name": "M-23 Gyroid Tunnel",
        "description": "Infinite Minimal Surface",
        "render": ss_gyroid.render,
        "recommended_theme": "arctic"
    },
    "potential": {
        "name": "M-24 N-Body Potential",
        "description": "Gravitational Fields",
        "render": ss_potential.render,
        "recommended_theme": "lavender"
    },
    "jellyfish": {
        "name": "M-25 Parametric Jellyfish",
        "description": "Oscillating Biological Form",
        "render": ss_jellyfish.render,
        "recommended_theme": "ocean"
    },
    "transparent_fish": {
        "name": "M-26 Transparent Fish",
        "description": "Mathematical Fish (Yeganeh)",
        "render": ss_transparent_fish.render,
        "recommended_theme": "rainbow"
    },
    "betta_fish": {
        "name": "M-27 Betta Fish",
        "description": "Parametric Lines (Yeganeh)",
        "render": ss_betta_fish.render,
        "recommended_theme": "rainbow"
    },
    "blackhole": {
        "name": "M-29 Black Hole",
        "description": "Accretion Disk & Event Horizon",
        "render": ss_blackhole.render,
        "recommended_theme": "fire"
    },
    "galaxy": {
        "name": "M-30 Interacting Galaxies",
        "description": "Spiral Galaxy Collision",
        "render": ss_galaxy.render,
        "recommended_theme": "plasma"
    },
    "isovalues": {
        "name": "M-32 Perlin Isovalues",
        "description": "Flowing Contour Lines",
        "render": ss_isovalues.render,
        "recommended_theme": "rainbow"
    },
    "clouds": {
        "name": "M-33 Tiny Planet Clouds",
        "description": "Raymarched Mini World",
        "render": ss_clouds.render,
        "recommended_theme": "ocean"
    }
}

# Time & Utility Apps Registry
TIME_APPS = {
    "gravity_clock": {
        "name": "T-01 Gravity Clock",
        "description": "Floating bouncing time digits",
        "render": t_gravity_clock.render,
        "recommended_theme": "neon"
    },
    "metaball_clock": {
        "name": "T-02 Metaball Clock",
        "description": "Organic blob SDF digits",
        "render": t_metaball_clock.render,
        "recommended_theme": "plasma"
    },
    "matrix_clock": {
        "name": "T-03 Matrix Clock",
        "description": "Rain freezes to form time",
        "render": t_matrix_clock.render,
        "recommended_theme": "matrix"
    },
    "shadow_clock": {
        "name": "T-04 Shadow Clock",
        "description": "Rotating light with shadows",
        "render": t_shadow_clock.render,
        "recommended_theme": "sunset"
    },
    "starwars": {
        "name": "T-05 Star Wars Scroll",
        "description": "Perspective text crawl",
        "render": t_starwars.render,
        "recommended_theme": "gold"
    },
    "typist": {
        "name": "T-06 Typist Terminal",
        "description": "Retro typing animation",
        "render": t_typist.render,
        "recommended_theme": "matrix"
    },
    "water_timer": {
        "name": "T-07 Water Timer",
        "description": "Draining water countdown",
        "render": t_water_timer.render,
        "recommended_theme": "ocean"
    },
    "circular_fuse": {
        "name": "T-08 Circular Fuse",
        "description": "Spark traveling countdown",
        "render": t_circular_fuse.render,
        "recommended_theme": "fire"
    },
    "life_timer": {
        "name": "T-09 Life Timer",
        "description": "Game of Life countdown",
        "render": t_life_timer.render,
        "recommended_theme": "toxic"
    },
    "hourglass": {
        "name": "T-10 Hourglass",
        "description": "Falling sand timer",
        "render": t_hourglass.render,
        "recommended_theme": "gold"
    },
    "planetary": {
        "name": "T-11 Planetary Clock",
        "description": "Solar system date/time",
        "render": t_planetary.render,
        "recommended_theme": "space"
    },
    "fire_clock": {
        "name": "T-12 Fire Clock",
        "description": "Blazing fire background",
        "render": t_fire_clock.render,
        "recommended_theme": "fire"
    },
    "plasma_clock": {
        "name": "T-13 Plasma Clock",
        "description": "Psychedelic plasma waves",
        "render": t_plasma_clock.render,
        "recommended_theme": "plasma"
    },
    "snow_clock": {
        "name": "T-14 Snow Clock",
        "description": "Peaceful snowfall",
        "render": t_snow_clock.render,
        "recommended_theme": "ice"
    }
}

ANIMATION_LIST = list(ANIMATIONS.keys())

