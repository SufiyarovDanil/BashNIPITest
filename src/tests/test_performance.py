import random
from uuid import UUID

import requests

from utils.well_generator import Well, generate_random_well


def test_api_well_at(benchmark):
    wells: list[Well] = [generate_random_well(100_000) for _ in range(10)]
    uuids: list[UUID] = []

    session: requests.Session = requests.session()

    for well in wells:
        resp = session.post(
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
        uuids.append(resp.json()['data']['uuid'])

    def call():
        for uuid in uuids:
            min_md = min(well.md)
            max_md = max(well.md)

            session.post(
                'http://localhost:8070/api/well.at',
                json={
                    "method": "well.at",
                    "params": {
                        "uuid": uuid,
                        "MD": float(random.randint(int(min_md), int(max_md)))
                    }
                }
            )

    benchmark(call,)

    for uuid in uuids:
        requests.post(
            'http://localhost:8070/api/well.remove',
            json={
                "method": "well.remove",
                "params": {
                    "uuid": uuid
                }
            }
        )
