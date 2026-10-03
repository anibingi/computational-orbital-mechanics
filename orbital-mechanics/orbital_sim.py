import numpy as np
import matplotlib.pyplot as plt

# --- Physical Constants & System Parameters ---
G = 6.67430e-11       # Gravitational constant (m^3 kg^-1 s^-2)
M = 5.972e24          # Central body mass (Earth, kg)
m = 1000.0            # Satellite mass (kg)

def acceleration(r_vec):
    """Calculates gravitational acceleration vector a = -GM * r / |r|^3"""
    r_mag = np.linalg.norm(r_vec)
    return -G * M * r_vec / (r_mag**3)

def compute_energy(r_vec, v_vec):
    """Calculates specific mechanical energy (E = Kinetic + Potential)"""
    v_mag = np.linalg.norm(v_vec)
    r_mag = np.linalg.norm(r_vec)
    kinetic = 0.5 * (v_mag**2)
    potential = -G * M / r_mag
    return kinetic + potential

# --- Simulation Setup ---
dt = 5.0              # Time step in seconds
total_time = 20000    # Total simulation duration (~3.3 orbits)
steps = int(total_time / dt)
time = np.linspace(0, total_time, steps)

# Initial conditions: Elliptical orbit (Perigee at 7,000 km, v0 = 8,200 m/s)
r0 = np.array([7.0e6, 0.0])
v0 = np.array([0.0, 8.2e3])

# --- Integrator 1: 4th-Order Runge-Kutta (RK4) ---
r_rk4 = np.zeros((steps, 2))
v_rk4 = np.zeros((steps, 2))
energy_rk4 = np.zeros(steps)

r_curr = r0.copy()
v_curr = v0.copy()

for i in range(steps):
    r_rk4[i] = r_curr
    v_rk4[i] = v_curr
    energy_rk4[i] = compute_energy(r_curr, v_curr)
    
    # RK4 Coefficients for coupled 2nd-order ODE
    k1_v = acceleration(r_curr) * dt
    k1_r = v_curr * dt
    
    k2_v = acceleration(r_curr + 0.5 * k1_r) * dt
    k2_r = (v_curr + 0.5 * k1_v) * dt
    
    k3_v = acceleration(r_curr + 0.5 * k2_r) * dt
    k3_r = (v_curr + 0.5 * k2_v) * dt
    
    k4_v = acceleration(r_curr + k3_r) * dt
    k4_r = (v_curr + k3_v) * dt
    
    v_curr += (k1_v + 2*k2_v + 2*k3_v + k4_v) / 6.0
    r_curr += (k1_r + 2*k2_r + 2*k3_r + k4_r) / 6.0

# --- Plotting Results ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Subplot 1: Orbit Trajectory
ax1.plot(r_rk4[:, 0] / 1e6, r_rk4[:, 1] / 1e6, 'b-', label='RK4 Trajectory')
ax1.plot(0, 0, 'go', markersize=10, label='Earth Center')
ax1.set_title("Orbital Trajectory (RK4 Integration)")
ax1.set_xlabel("X Position ($10^3$ km)")
ax1.set_ylabel("Y Position ($10^3$ km)")
ax1.axis("equal")
ax1.grid(True)
ax1.legend()

# Subplot 2: Energy Conservation Stability
delta_E = (energy_rk4 - energy_rk4[0]) / np.abs(energy_rk4[0])
ax2.plot(time / 60.0, delta_E, 'r-')
ax2.set_title("Relative Energy Conservation Error ($\Delta E / |E_0|$)")
ax2.set_xlabel("Time (minutes)")
ax2.set_ylabel("Relative Error")
ax2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
ax2.grid(True)

plt.tight_layout()
plt.savefig("orbital_simulation_output.png", dpi=300)
plt.show()
