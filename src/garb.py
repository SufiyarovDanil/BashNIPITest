import requests
import numpy as np

from utils.well_generator import generate_random_well


def add_wells():
    wells = [generate_random_well(50) for _ in range(1)]

    for well in wells:
        if not (well.md.size == well.x.size == well.y.size == well.z.size):
            print('arrays dont have same size')
            print(f'md: {well.md.size}, x: {well.x.size}, y: {well.y.size}, z: {well.z.size}')
        
        well.x[0] = well.head[0]
        well.y[0] = well.head[1]
        
        resp = requests.post(
            'http://localhost:8070/api/well.create',
            json={
                "method": "well.create",
                "params": {
                    "name": well.name,
                    "head": well.head,
                    "MD": well.md.tolist(),
                    "X": well.x.tolist(),
                    "Y": well.y.tolist(),
                    "Z": well.z.tolist()
                }
            }
        )

        print(resp.text)


def test_request_well_at():
    resp = requests.post(
        'http://localhost:8070/api/well.at',
        json={
            'method': 'well.at',
            'params': {
                'uuid': 'ac6e1bc6-b68a-4ef7-8e7a-0c6c1c012afb',
                'MD': 33.99884
            }
        }
    )
    print(resp.elapsed)
    print(resp.text)


if __name__ == '__main__':
    add_wells()
    # test_request_well_at()
