# 🎨 Terminal Animation Engine

A high-performance terminal-based animation engine written in Python. Renders stunning 3D wireframes, mathematical visualizations, GPU-style shader effects, and stylish clocks — all in ASCII/Unicode art directly in your terminal.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

- **49 unique animations** across 4 categories
- **Real-time 3D rendering** with perspective projection and z-buffering
- **GPU-style shader engine** using NumPy vectorization
- **Multiple rendering modes**: ASCII, Unicode blocks (▀▄█), and Braille patterns (⠿)
- **20+ color themes** with depth-based gradients
- **Glow/bloom effects** and thick line rendering
- **Cross-platform**: Windows, Linux, macOS

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- NumPy

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `1-4` | Select category |
| `1-99` | Select animation |
| `Q` / `ESC` | Quit / Back |
| `Space` | Pause / Resume |
| `+` / `-` | Increase / Decrease speed |
| `T` / `R` | Next / Previous theme |
| `S` | Toggle stats display |

---

## 📚 Animation Catalog

### Category 1: Standard 3D Animations (18 animations)

| # | Name | Description | Math/Technique |
|---|------|-------------|----------------|
| 1 | **DNA Double Helix** | Two intertwined helical strands with base pairs | Parametric helix: `x = r·cos(θ)`, `y = r·sin(θ)`, `z = c·θ` |
| 2 | **Torus (Donut)** | Classic spinning donut with depth shading | Parametric surface: `(R + r·cos(v))·cos(u)`, uses two angle parameters |
| 3 | **Wireframe Sphere** | Rotating globe with latitude/longitude lines | Spherical coordinates: `x = r·sin(φ)·cos(θ)`, `y = r·sin(φ)·sin(θ)`, `z = r·cos(φ)` |
| 4 | **Rotating Cube** | 3D wireframe cube spinning on all axes | 8 vertices connected by 12 edges, rotation matrices applied |
| 5 | **Tetrahedron** | 4-sided pyramid wireframe | 4 vertices, 6 edges forming triangular faces |
| 6 | **Lorenz Attractor** | Chaos theory butterfly pattern | Differential equations: `dx/dt = σ(y-x)`, `dy/dt = x(ρ-z)-y`, `dz/dt = xy-βz` with σ=10, ρ=28, β=8/3 |
| 7 | **Möbius Strip** | Single-sided surface with half twist | Parametric: twisted rectangular strip with 180° rotation |
| 8 | **Klein Bottle** | 4D shape that passes through itself | Immersion of non-orientable surface into 3D |
| 9 | **Lissajous Knots** | Complex 3D oscillating curves | `x = A·sin(aθ+δ)`, `y = B·sin(bθ)`, `z = C·sin(cθ)` |
| 10 | **Rose Curves (3D)** | Mathematical flower patterns | Polar equation: `r = cos(kθ)` extended to 3D |
| 11 | **Sine Wave Grid** | Rippling water surface | 2D grid with `z = sin(x + t)·cos(y + t)` displacement |
| 12 | **Matrix Rain 3D** | Falling characters in 3D tunnel | Random character streams with depth-based fade |
| 13 | **Starfield / Warp Speed** | Flying through space with glow | Z-sorted particles moving toward camera with perspective |
| 14 | **Superformula** | Shape-shifting mathematical surface | Gielis superformula: generalized ellipse equation |
| 15 | **Perlin Noise Terrain** | Infinite scrolling landscape | Layered Perlin noise for height, scrolling UV offset |
| 16 | **Julia Set / Mandelbrot** | Animated 3D fractal projection | Complex iteration: `z(n+1) = z(n)² + c` with escape-time coloring |
| 17 | **Particle Life / Swarm** | Emergent swarm intelligence behavior | Boids algorithm: separation, alignment, cohesion forces |
| 18 | **Raymarching SDF** | Real-time volumetric rendering with lighting | Sphere-tracing signed distance functions with Phong shading |

---

### Category 2: Screensavers — 16:9 (11 animations)

Centralized volumetric fractals optimized for standard aspect ratios.

| # | Name | Description | Math/Technique |
|---|------|-------------|----------------|
| 1 | **M-21 Mandelbulb** | Ray-marched 3D fractal | 3D extension of Mandelbrot: spherical coordinate power formula |
| 2 | **M-22 Phyllotaxis** | Dynamic sunflower spirals | Golden angle: `θ = n × 137.5°`, Vogel's model |
| 3 | **M-23 Gyroid Tunnel** | Infinite minimal surface | Triply periodic: `sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0` |
| 4 | **M-24 N-Body Potential** | Gravitational field visualization | Scalar field: `Σ 1/|r - rᵢ|` for point masses |
| 5 | **M-25 Parametric Jellyfish** | Oscillating biological form | Sinusoidal bell deformation with tentacle physics |
| 6 | **M-26 Transparent Fish** | Mathematical fish (Yeganeh) | Complex parametric equations by Hamid Naderi Yeganeh |
| 7 | **M-27 Betta Fish** | Parametric line art (Yeganeh) | 10,000+ parametric line segments forming fish shape |
| 8 | **M-29 Black Hole** | Accretion disk & event horizon | Gravitational lensing simulation, Schwarzschild metric |
| 9 | **M-30 Interacting Galaxies** | Spiral galaxy collision | N-body gravitational simulation with spiral arm dynamics |
| 10 | **M-32 Perlin Isovalues** | Flowing contour lines | Marching squares on animated Perlin noise field |
| 11 | **M-33 Tiny Planet Clouds** | Raymarched mini world | Spherical domain warping with volumetric cloud density |

---

### Category 3: Screensavers — Ultrawide (6 animations)

Horizontal flows and infinite fields optimized for ultrawide displays.

| # | Name | Description | Math/Technique |
|---|------|-------------|----------------|
| 1 | **M-16 Gerstner Ocean** | Photorealistic wave simulation | Gerstner wave equation: trochoidal waves with orbital motion |
| 2 | **M-17 Kleinian Limit** | Schottky group fractals | Möbius transformations and circle inversion fractals |
| 3 | **M-18 Synthwave Terrain** | Retro Fourier landscape | FFT-based terrain with neon grid aesthetics |
| 4 | **M-19 Domain Warping** | Fluid noise simulation | Nested Perlin noise: `fbm(p + fbm(p + fbm(p)))` |
| 5 | **M-20 Hyperbolic Flight** | Poincaré disk traversal | Hyperbolic geometry, conformal mapping to unit disk |
| 6 | **M-31 Electrocardiogram** | Traveling ECG heartbeat pulse | PQRST waveform synthesis with traveling wave animation |

---

### Category 4: Time & Utility (14 animations)

Stylish clocks, timers, and countdowns with animated backgrounds.

| # | Name | Description | Visual Effect |
|---|------|-------------|---------------|
| 1 | **T-01 Gravity Clock** | Floating bouncing time digits | Physics simulation with collision detection |
| 2 | **T-02 Metaball Clock** | Organic blob SDF digits | Smooth union of signed distance metaballs |
| 3 | **T-03 Matrix Clock** | Rain freezes to form time | Character rain that consolidates into digit shapes |
| 4 | **T-04 Shadow Clock** | Rotating light with shadows | Dynamic shadow casting from moving light source |
| 5 | **T-05 Star Wars Scroll** | Perspective text crawl | 3D perspective projection of scrolling text |
| 6 | **T-06 Typist Terminal** | Retro typing animation | Typewriter effect with cursor blink |
| 7 | **T-07 Water Timer** | Draining water countdown | Fluid simulation with falling water level |
| 8 | **T-08 Circular Fuse** | Spark traveling countdown | Burning fuse animation around circular path |
| 9 | **T-09 Life Timer** | Conway's Game of Life countdown | Cellular automaton forming countdown numbers |
| 10 | **T-10 Hourglass** | Falling sand timer | Particle sand simulation with hourglass shape |
| 11 | **T-11 Planetary Clock** | Solar system date/time | Orbital mechanics showing planet positions |
| 12 | **T-12 Fire Clock** | Blazing fire background | Procedural fire shader with time overlay |
| 13 | **T-13 Plasma Clock** | Psychedelic plasma waves | Classic plasma effect: `sin(x) + sin(y) + sin(x+y+t)` |
| 14 | **T-14 Snow Clock** | Peaceful snowfall | Particle snowflakes with drift and accumulation |

---

## � Technical Architecture

### Core Components

```
terminal-animation-engine/
├── main.py              # Menu system and entry point
├── engine.py            # 3D rendering engine
├── shader_engine.py     # GPU-style shader renderer
├── colors.py            # Theme system and ANSI codes
└── animations/
    ├── __init__.py      # Animation registry
    ├── [18 animation modules]
    ├── screensavers/    # 17 shader-based screensavers
    ├── time/            # 14 clock/timer apps
    └── utils/           # Shared utilities
```

### Rendering Pipeline

#### 1. 3D Wireframe Engine (`engine.py`)

The engine uses a classic 3D graphics pipeline:

**Rotation Matrices**
```
Rx(θ) = | 1    0       0    |    Ry(θ) = | cos(θ)  0  sin(θ) |
        | 0  cos(θ) -sin(θ) |            |   0     1    0    |
        | 0  sin(θ)  cos(θ) |            |-sin(θ)  0  cos(θ) |
```

**Perspective Projection**
```
screen_x = (x × scale) / (z + distance) + width/2
screen_y = (y × scale) / (z + distance) + height/2
```

**Z-Buffering**: Each pixel stores depth value; closer objects overwrite farther ones.

**Line Drawing**: Bresenham's algorithm for pixel-perfect lines, with optional thickness.

#### 2. Shader Engine (`shader_engine.py`)

A fragment-shader-style renderer using NumPy vectorization:

**Block Mode**: Uses Unicode block characters (`▀▄█`) for 2× vertical resolution
- Each terminal cell represents 2 virtual pixels

**Braille Mode**: Uses Unicode Braille patterns (`⠿`) for 8× resolution
- Each terminal cell represents 2×4 = 8 sub-pixels
- Bit encoding: Each dot maps to a specific bit in range U+2800–U+28FF

**Ordered Dithering**: 4×4 Bayer matrix for smooth gradients:
```
     0   8   2  10
    12   4  14   6
     3  11   1   9
    15   7  13   5
```

#### 3. Color System (`colors.py`)

- **ANSI escape codes** for terminal colors
- **True color (24-bit RGB)** support via `\033[38;2;R;G;Bm`
- **Depth-based gradients**: Objects closer to camera are brighter
- **20+ themes**: matrix, plasma, ocean, fire, arctic, neon, rainbow, etc.

---

## 🎨 Color Themes

| Theme | Colors | Best For |
|-------|--------|----------|
| Matrix | Greens | Matrix rain, code visuals |
| Plasma | Pink/Purple/Blue | Fractals, psychedelic |
| Ocean | Blues/Cyans | Water, waves |
| Fire | Red/Orange/Yellow | Flames, heat |
| Arctic | White/Cyan/Blue | Ice, snow |
| Neon | Pink/Cyan | Synthwave, retro |
| Rainbow | Full spectrum | Colorful shapes |
| Gold | Yellow/Orange | Metallic, elegant |
| Sunset | Orange/Pink/Purple | Warm atmospheres |
| Toxic | Green/Yellow | Biohazard, acid |
| Lavender | Purple/Pink | Soft, calming |
| Void | Dark grays | Space, minimalist |
| Copper | Brown/Orange | Metallic surfaces |
| Forest | Greens/Browns | Nature, terrain |
| Space | Blues/Purples | Galaxies, stars |
| Ice | White/Light blue | Frozen, crystalline |

---

## 💻 System Requirements

- **Terminal**: Any modern terminal with ANSI color support (Windows Terminal, iTerm2, GNOME Terminal, etc.)
- **Minimum size**: 80×24 characters
- **Recommended**: Fullscreen for best detail
- **Font**: Monospace font with Unicode support (for block/Braille characters)

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Hamid Naderi Yeganeh** for mathematical fish artwork formulas
- **demoscene community** for shader and visual effect inspiration
- **Sebastian Lague** and **Inigo Quilez** for raymarching and SDF techniques
- https://github.com/Deybacsi/asciiclock
