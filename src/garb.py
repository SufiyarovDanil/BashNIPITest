import requests
import numpy as np

from utils.well_generator import generate_random_well


def add_wells():
    wells = [generate_random_well(100_000) for _ in range(1)]

    for well in wells:
        well.x[0] = well.head[0]
        well.y[0] = well.head[1]
        
        resp = requests.post(
            'http://localhost:8070/api/well.create',
            json={
                "method": "well.create",
                "params": {
                    "name": well.name,
                    "head": well.head,
                    "MD": well.md,
                    "X": well.x,
                    "Y": well.y,
                    "Z": well.z
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


def test_request_well_get():
    resp = requests.post(
        'http://localhost:8070/api/well.get',
        json={
            'method': 'well.get',
            'params': {
                'uuid': '1ebe3f2e-9add-4352-87b3-4e3b8d3bcdf8',
                'return_trajectory': True
            }
        }
    )
    print(resp.elapsed)

if __name__ == '__main__':
    # add_wells()
    test_request_well_get()
    # test_request_well_at()
