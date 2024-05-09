"""
kursiv.py - solution of Kuramoto-Sivashinsky equation by ETDRK4 scheme
"""

import numpy as np
from numpy.fft import rfft, irfft, rfftfreq
import matplotlib.pyplot as plt


def rfft_truncated(u):
    uhat = rfft(u)
    (k,) = uhat.shape
    size = int(2 / 3 * k) + 1
    return 2 / 3 * uhat[:size]


def irfft_padded(uhat):
    (n,) = uhat.shape
    size = int(3 / 2 * n)
    padded = np.pad(uhat, (0, size - n))
    return 3 / 2 * irfft(padded)


# spatial grid and initial condition
Nx = 1024
xx = np.linspace(0, 32 * np.pi, Nx + 1)[1:]
u = np.cos(xx / 16) * (1 + np.sin(xx / 16))
v = rfft(u)

# precompute quantities
t = 0.0
h = 1 / 4
k = 2j * np.pi * rfftfreq(Nx, 32 * np.pi / Nx)
L = -(k**2) - k**4
E = np.exp(h * L)
E2 = np.exp(h * L / 2)
M = 16
r = np.exp(1j * np.pi * np.arange(1 - 0.5, M + 1 - 0.5) / M)
LR = h * L[:, None] + r
Q = h * ((np.exp(LR / 2) - 1) / LR).mean(1).real
f1 = h * ((-4 - LR + np.exp(LR) * (4 - 3 * LR + LR**2)) / LR**3).mean(1).real
f2 = h * ((2 + LR + np.exp(LR) * (-2 + LR)) / LR**3).mean(1).real
f3 = h * ((-4 - 3 * LR - LR**2 + np.exp(LR) * (4 - LR)) / LR**3).mean(1).real

vv = [v]
tt = [0.0]
tmax = 150.0
nmax = int(150 // h)
nplt = nmax // 200


def step(t, v):
    t = t + h
    Nv = -0.5 * k * rfft_truncated(irfft_padded(v) ** 2)
    a = E2 * v + Q * Nv
    Na = -0.5 * k * rfft_truncated(irfft_padded(a) ** 2)
    b = E2 * v + Q * Na
    Nb = -0.5 * k * rfft_truncated(irfft_padded(b) ** 2)
    c = E2 * a + Q * (2 * Nb - Nv)
    Nc = -0.5 * k * rfft_truncated(irfft_padded(c) ** 2)
    v = E * v + Nv * f1 + 2 * (Na + Nb) * f2 + Nc * f3
    return t, v


for n in range(nmax):
    t, v = step(t, v)
    if n % nplt == 0:
        tt.append(t), vv.append(v)

vv = np.stack(vv)
uu = irfft(vv, Nx, axis=-1)

plt.imshow(
    uu, origin="lower", aspect="auto", cmap="jet", extent=[0, 32 * np.pi, 0, tmax]
)
plt.xlabel(r"$x$")
plt.ylabel(r"$t$")
plt.colorbar()
plt.tight_layout()
plt.savefig("../figures/kursiv_dealiased.png", format="png")
