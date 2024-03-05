import requests
import numpy as np

from utils.well_generator import generate_random_well


uuids = [
    "03287f95-f986-412f-bb9a-2223861f1e9d",
    "10ddeed6-4872-4e60-87ac-7a0811d1e96e",
    "19933974-40af-4c9a-913b-06043071a885",
    "1d3ea493-285a-496a-9b4e-71b3cf39fc58",
    "40c4a04b-6cc2-4336-8bd3-93afad525a36",
    "75e54c16-4b22-40fd-b561-cb7d86f125b8",
    "7a3b4aba-b326-4b03-9ffa-d0abe48886ee",
    "89856d77-0e10-4ac1-9460-73d48f66301f",
    "d665f212-2752-46f4-be14-fc996b94a6ad",
    "edf0f3f0-1cf3-4f7e-a435-568e9b3e23c3"
]


def add_wells():
    wells = [generate_random_well(100_000) for _ in range(2)]

    for well in wells:
        well.x[0] = well.head[0]
        well.y[0] = well.head[1]
        print(well.name)
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
    session = requests.session()

    for uuid in uuids:
        resp = session.post(
            'http://localhost:8070/api/well.at',
            json={
            'method': 'well.at',
            'params': {
                'uuid': '75e54c16-4b22-40fd-b561-cb7d86f125b8',
                'MD': 34.190147399902344
                }
            })
        print(int(resp.elapsed.total_seconds() * 1000))
        print(resp.text)


def test_request_well_get():
    session = requests.session()
    for _ in range(10):
        resp = session.post(
            'http://localhost:8070/api/well.get',
            json={
                'method': 'well.get',
                'params': {
                    'uuid': '291a683d-6abf-4c3f-a356-6f91597c9a77',
                    'return_trajectory': True
                }
            })
        print(int(resp.elapsed.total_seconds() * 1000))


def test_request_well_delete():
    session = requests.session()
    for uuid in uuids:
        resp = session.post(
            'http://localhost:8070/api/well.remove',
            json={
                'method': 'well.remove',
                'params': {
                    'uuid': uuid,
                }
            })
        print(resp.text)

if __name__ == '__main__':
    # add_wells()
    # test_request_well_get()
    # test_request_well_at()
    test_request_well_delete()
