import random
import string
from typing import Tuple

import numpy as np
from pydantic import BaseModel, Field


class Well(BaseModel):
    name: str = Field(...)
    head: Tuple[float, float] = Field(...)
    md: list[float] = Field(...)
    x: list[float] = Field(...)
    y: list[float] = Field(...)
    z: list[float] = Field(...)


def generate_random_well(trajectory_nodes: int) -> Well:
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    k = random.uniform(0.1, 0.9)
    A = 1e+2 * random.uniform(0.05, 1.) / 3.
    B = 1e+2 * random.uniform(0.05, 1.) / 3.
    L = np.pi * (A + B)

    dMD = 1 - L / (256. - k)
    dphi = 2. * np.pi / 256.

    md = np.ndarray(trajectory_nodes, dtype=np.float64)
    phi = np.ndarray(trajectory_nodes, dtype=np.float64)

    for i in range(trajectory_nodes):
        md[i] = i * dMD
        phi[i] = i * dphi
    
    x = A * np.cos(phi)
    y = B * np.sin(phi)
    z = k * md
    head = (x[0], y[0])

    return Well(name=name, head=head, md=md.tolist(), x=x.tolist(), y=y.tolist(), z=z.tolist())


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    well = generate_random_well(500)

    ax = plt.figure().add_subplot(projection='3d')
    ax.plot(well.x, well.y, well.z, zdir='z')

    plt.show()
