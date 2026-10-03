import numpy as np
import matplotlib.pyplot as plt

# --- Physical Constants & Particle Parameters (Deuterium Ion in Fusion Plasma) ---
q = 1.602e-19       # Charge (C)
m = 3.344e-27       # Mass of Deuteron (kg)

def magnetic_field(r_vec):
    """Magnetic field with a gradient along x: B = B0 * (1 + x / L) z_hat"""
    B0 = 2.0        # Base magnetic field in Tesla (typical for tokamaks/stellarators)
    L = 1.0         # Gradient scale length in meters
    Bx = 0.0
    By = 0.0
    Bz = B0 * (1.0 + r_vec[0] / L)
    return np.array([Bx, By, Bz])

def electric_field(r_vec):
    """Static background electric field (can be set to 0 for pure magnetic drift)"""
    return np.array([0.0, 0.0, 0.0])

# --- Simulation Setup ---
dt = 1.0e-10        # Sub-nanosecond time step to resolve cyclotron gyro-radius
total_time = 2.0e-6 # 2 microseconds
steps = int(total_time / dt)

# Initial conditions (energetic fusion alpha/ion)
r = np.array([0.05, 0.0, 0.0])              # Initial position (m)
v = np.array([1.5e5, 1.0e5, 5.0e4])         # Initial velocity (m/s)

positions = np.zeros((steps, 3))
kinetic_energies = np.zeros(steps)

# --- Boris Push Algorithm (Standard in Fusion Energy Research) ---
for i in range(steps):
    positions[i] = r
    kinetic_energies[i] = 0.5 * m * np.dot(v, v) / 1.602e-19 # in eV
    
    E = electric_field(r)
    B = magnetic_field(r)
    
    # 1. Half-step electric acceleration
    v_minus = v + (q * E / m) * (0.5 * dt)
    
    # 2. Magnetic rotation
    t_vec = (q * B / m) * (0.5 * dt)
    s_vec = 2.0 * t_vec / (1.0 + np.dot(t_vec, t_vec))
    v_prime = v_minus + np.cross(v_minus, t_vec)
    v_plus = v_minus + np.cross(v_prime, s_vec)
    
    # 3. Final half-step electric acceleration
    v = v_plus + (q * E / m) * (0.5 * dt)
    
    # Update position
    r += v * dt

# --- Plotting the Gyromotion & Guiding Center Drift ---
fig = plt.figure(figsize=(12, 5))

# 3D Trajectory Plot
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.plot(positions[:, 0] * 1000, positions[:, 1] * 1000, positions[:, 2] * 1000, 'b-', lw=0.6)
ax1.set_title("Energetic Ion Gyromotion & $\\nabla B$ Drift")
ax1.set_xlabel("X (mm)")
ax1.set_ylabel("Y (mm)")
ax1.set_zlabel("Z (mm)")

# Kinetic Energy Conservation
ax2 = fig.add_subplot(1, 2, 2)
relative_E_err = (kinetic_energies - kinetic_energies[0]) / kinetic_energies[0]
time_us = np.linspace(0, total_time * 1e6, steps)
ax2.plot(time_us, relative_E_err, 'r-')
ax2.set_title("Boris Solver Energy Conservation ($\Delta K / K_0$)")
ax2.set_xlabel("Time ($\mu s$)")
ax2.set_ylabel("Relative Energy Drift")
ax2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax2.grid(True)

plt.tight_layout()
plt.savefig("particle_drift_output.png", dpi=300)
plt.show()
