"""
Black Hole Screensaver
Numpy Optimized.
Verbatim translation of Hamid Naderi Yeganeh's Black Hole equations.
"""

import numpy as np

def calculate_black_hole_frame(u, v, t):
    # u, v are from shader_engine, typically -1..1 or aspect corrected.
    # The math expects specific grid: x = (m-1000)/160, y = (601-n)/160
    # m=1..2000, n=1..1200
    # Width ~ 12.5 units, Height ~ 7.5 units
    
    # Map u,v to x,y
    # u is approx -1.77..1.77, v -1..1
    # Scale u,v to match the domain x ~ -6..6, y ~ -3..3
    
    x = u * 4.0
    y = v * 4.0
    
    # Function definitions Verbatim
    
    # Q(x,y) = 3/10 x + 3/20 y
    Q = 0.3 * x + 0.15 * y
    
    # P(x,y) = y - x/2
    P = y - x / 2.0
    
    # E(x,y) = sqrt(Q^2 + P^2) * e^-e
    # python exp goes crazy with large numbers, but math domain is small x,y
    exp_e = np.exp(1.0) # e
    E = np.sqrt(Q**2 + P**2) * np.exp(-exp_e)
    
    # Jr(x,y) - Accretion Disk / Jet Texture
    # Angle has time injection 't'
    # angle = pi/4 - 4.5 * ln(E) + t
    # E can be 0 at center, add epsilon
    angle = (np.pi / 4.0) - (4.5 * np.log(E + 1e-7)) + t * 2.0 # Speed up swirl
    
    term_q = (Q - E) * np.cos(angle)
    term_p = (P - E) * np.sin(angle)
    argument = term_q**2 + term_p**2
    # Power -0.1
    # Avoid zero division
    Jr = np.exp(-(argument + 1e-9)**(-0.1))
    
    # K(x,y) - Accretion Disk Grain
    # sum s=1 to 70
    # Optimized to 20 for realtime
    K = np.zeros_like(x)
    s_limit = 20
    for s in range(1, s_limit + 1):
        # cos^10((5+s/6)(cos(s^2 x + sin(s^2 y)) + 10 sin(10s)))
        # Animation: add t to inner phases? The user code added t to sin(s^2 y + t)
        
        inner_trig = np.cos(s**2 * x + np.sin(s**2 * y + t)) + 10.0 * np.sin(10.0 * s)
        angle_k = (5.0 + s / 6.0) * inner_trig
        term_k = np.cos(angle_k)**10
        
        K += (4.0 / 25.0) * np.exp(-100.0 * term_k)
        
    # W(x,y) - Event Horizon Mask
    # exp(-exp(-500(x - 1.7/10)^2 - 500(y - 3/10)^2))
    # Note: The prompt code had -500*(x-0.17)^2 ...
    
    W = np.exp(-np.exp(-500.0 * (x - 0.17)**2 - 500.0 * (y - 0.3)**2))
    
    # R(x,y) - Relativistic Jet Mask
    # exp(-exp(20*(x + 0.3 cos(10y)) - 1000(y - x/2)))
    # Wait, the prompt code says:
    # R = exp(-exp(20 * (x + 3/10 * cos(10 * y)) - 1000 * (y - x/2)))
    
    R = np.exp(-np.exp(20.0 * (x + 0.3 * np.cos(10.0 * y)) - 1000.0 * (y - x / 2.0)))
    
    # Background Stars L(x,y)
    # The prompt code loop 1..10
    L = np.zeros_like(x)
    
    # hv calculation
    def get_channel(v):
        # Term 1
        # (3v^2 - 5v + 7)/4 * R * K
        coeff1 = (3.0 * v**2 - 5.0 * v + 7.0) / 4.0
        term1 = coeff1 * R * K
        
        # Term 2
        # (2-v)/2 * Jr * K * (1-R)
        coeff2 = (2.0 - v) / 2.0
        term2 = coeff2 * Jr * K * (1.0 - R)
        
        # Term 3
        # coeff1 * W * K * Jr
        term3 = coeff1 * W * K * Jr
        
        return term1 + term2 + term3 # + L
        
    # F(x) Color Filter
    def F(val):
        val = np.clip(val, 0, 1)
        # 255 * exp(-exp(-1000x) * |x|^exp(-exp(1000(x-1))))
        # We return 0..1 float
        # inner = exp(-exp(-1000 * val)) * abs(val)**(exp(-exp(1000*(val-1))))
        
        # Simplified for speed/stability:
        return val # The math is basically a window 0..1. The engine maps it.
        
    r = F(get_channel(0))
    g = F(get_channel(1))
    b = F(get_channel(2))
    
    # Stack for RGB return
    # The shader_engine expects (H, W, 3) for RGB mode.
    # We change axis=0 to axis=-1
    return np.stack((r, g, b), axis=-1)

def render(buffer, width, height, time, theme_manager):
    from shader_engine import run_shader_animation
    return run_shader_animation(buffer, width, height, time, theme_manager, calculate_black_hole_frame)
