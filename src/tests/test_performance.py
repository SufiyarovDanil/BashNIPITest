import pytest
import json
import random
import requests

from utils.well_generator import generate_random_well


PERFORMANCE_ITERATIONS = 1


def test_api_well_at(benchmark, iterations=PERFORMANCE_ITERATIONS, **kwargs):
    wells = [generate_random_well(100_000) for i in range(10)]
    uuids = []

    min_md = wells[0].md.min()
    max_md = wells[0].md.max()

    for well in wells:
        resp = requests.post(
            'http://localhost:8070/api/well.create',
            data={
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
        uuids.append(resp.json()['data']['uuid'])

    def call():
        requests.post(
            'http://localhost:8070/api/well.at',
            data={
                "method": "well.at",
                "params": {
                    "uuid": uuids[0],
                    "MD": random.random(min_md, max_md)
                }
            }
        )

    benchmark.pedantic(call, args=(), kwargs=kwargs, iterations=iterations, rounds=1)

    for uuid in uuids:
        requests.post(
            'http://localhost:8070/api/well.remove',
            data={
                "method": "well.remove",
                "params": {
                    "uuid": uuid
                }
            }
        )
