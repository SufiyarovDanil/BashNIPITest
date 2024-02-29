import random
import string
import numpy as np

from typing import Tuple
from pydantic import BaseModel, Field


class Well(BaseModel):
    name: str = Field(...)
    head: Tuple[float, float] = Field(...)
    md: np.ndarray[float] = Field(...)
    x: np.ndarray[float] = Field(...)
    y: np.ndarray[float] = Field(...)
    z: np.ndarray[float] = Field(...)

    class Config:
        arbitrary_types_allowed = True


def generate_random_well(trajectory_nodes: int) -> Well:
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    head = (1e+5 * np.random.randn(), 1e+5 * np.random.randn())

    k = random.uniform(0.1, 0.9)
    A = 1e+2 * random.uniform(0.05, 1.) / 3.
    B = 1e+2 * random.uniform(0.05, 1.) / 3.
    L = np.pi * (A + B)
    dMD = 1 - L / (256. - k)
    dphi = 2. * np.pi / 256.

    md = np.arange(0., (trajectory_nodes - 1) * dMD, dMD, dtype=np.float32)
    phi = np.arange(0., (trajectory_nodes - 1) * dphi, dphi, dtype=np.float32)
    x = A * np.cos(phi)
    y = B * np.sin(phi)
    z = k * md

    return Well(name=name, head=head, md=md, x=x, y=y, z=z)


if __name__ == "__main__":
    import matplotlib
    # matplotlib.use('QtAgg')
    import matplotlib.pyplot as plt

    well = generate_random_well(500)
    # print(well)

    ax = plt.figure().add_subplot(projection='3d')
    ax.plot(well.x, well.y, well.z, zdir='z')

    plt.show()
