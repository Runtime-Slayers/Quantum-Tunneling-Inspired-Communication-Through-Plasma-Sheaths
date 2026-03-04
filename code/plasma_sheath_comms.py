"""
Quantum Tunneling-Inspired Multi-Frequency Communication Through Plasma Sheaths
Transfer Matrix Framework for Re-entry Blackout Mitigation
"""
import numpy as np

def plasma_permittivity(f_hz, n_e=1e18, nu_c=1e9):
    """Electron permittivity of plasma layer."""
    eps_0 = 8.854e-12
    e  = 1.6e-19
    m  = 9.11e-31
    wp2 = n_e * e**2 / (m * eps_0)
    omega = 2 * np.pi * f_hz
    eps_r = 1 - wp2 / (omega**2 + 1j * nu_c * omega)
    return eps_r

def transfer_matrix(f_hz, d_m=0.1, n_e=1e18):
    """Transfer matrix for a single plasma slab."""
    c = 3e8
    eps_r = plasma_permittivity(f_hz, n_e)
    k = 2 * np.pi * f_hz / c * np.sqrt(eps_r + 0j)
    kd = k * d_m
    cos_kd = np.cos(kd)
    sin_kd = np.sin(kd)
    eta = np.sqrt(eps_r + 0j)
    M = np.array([[cos_kd, -1j * sin_kd / eta],
                  [-1j * eta * sin_kd, cos_kd]])
    return M

def multi_layer_transmission(f_hz, layers):
    """Total transmission through N plasma slabs via transfer matrices."""
    M_total = np.eye(2, dtype=complex)
    for (d, n_e) in layers:
        M_total = M_total @ transfer_matrix(f_hz, d, n_e)
    T = 1 / np.abs(M_total[0, 0]) ** 2
    return float(min(T, 1.0))

def blackout_profile(f_range_ghz, n_e=1e18, d_m=0.15):
    transmissions = []
    for f_ghz in f_range_ghz:
        t = multi_layer_transmission(f_ghz * 1e9, [(d_m, n_e)])
        transmissions.append(t)
    return np.array(transmissions)

def find_transmission_windows(f_ghz, T, threshold=0.01):
    """Identify frequency windows that penetrate the plasma."""
    windows = f_ghz[T > threshold]
    return windows

if __name__ == "__main__":
    print("Computing plasma sheath transmission spectrum...")
    f_ghz = np.linspace(0.1, 40, 400)  # 100 MHz to 40 GHz
    layers = [(0.05, 1e18), (0.08, 5e17), (0.05, 1e18)]  # 3-layer sheath
    T = np.array([multi_layer_transmission(f*1e9, layers) for f in f_ghz])
    windows = find_transmission_windows(f_ghz, T, threshold=0.01)
    print(f"  Frequency range : {f_ghz.min():.1f} - {f_ghz.max():.1f} GHz")
    print(f"  Blackout bands  : {(T < 0.01).sum()} / {len(T)} bins")
    print(f"  Open windows    : {len(windows)} bins above 1% transmission")
    if len(windows):
        print(f"  Best window     : {windows[0]:.2f} - {windows[-1]:.2f} GHz")
    print("Plasma sheath communication analysis complete.")
