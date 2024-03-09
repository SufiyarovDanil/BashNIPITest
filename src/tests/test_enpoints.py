from uuid import UUID, uuid4

import pytest
import requests

from utils.well_generator import generate_random_well, Well


well: Well = generate_random_well(100)
session: requests.Session = requests.session()
uuids: list[UUID] = []


def test_well_create():
    resp = session.post(
        'http://localhost:8070/api/well.create',
        json={
            'method': 'well.create',
            'params': {
                'name': well.name,
                'head': well.head,
                'MD': well.md,
                'X': well.x,
                'Y': well.y,
                'Z': well.z
            }
        }
    )

    try:
        uuid = resp.json()['data']['uuid']
    except KeyError:
        assert False
    else:
        assert uuid is not None
        uuids.append(uuid)


def test_well_create_existing_name():
    well_with_existing_name: Well = generate_random_well(100)
    well_with_existing_name.name = well.name
    resp = session.post(
        'http://localhost:8070/api/well.create',
        json={
            'method': 'well.create',
            'params': {
                'name': well_with_existing_name.name,
                'head': well_with_existing_name.head,
                'MD': well_with_existing_name.md,
                'X': well_with_existing_name.x,
                'Y': well_with_existing_name.y,
                'Z': well_with_existing_name.z
            }
        }
    )

    result = resp.json()

    try:
        error_message: str =  result['error']['message']
    except KeyError:
        uuids.append(result['data']['uuid'])
        assert False
    else:
        assert error_message == 'Well already exists!'


def test_well_create_inconsistent_head():
    well_with_inconsistent_head: Well = generate_random_well(100)
    head = well_with_inconsistent_head.head
    new_head = (head[0] + 1., head[1] + 1.)
    resp = session.post(
        'http://localhost:8070/api/well.create',
        json={
            'method': 'well.create',
            'params': {
                'name': well_with_inconsistent_head.name,
                'head': new_head,
                'MD': well_with_inconsistent_head.md,
                'X': well_with_inconsistent_head.x,
                'Y': well_with_inconsistent_head.y,
                'Z': well_with_inconsistent_head.z
            }
        }
    )

    result = resp.json()

    try:
        error_message: str = result['error']['message']
    except KeyError:
        uuids.append(result['data']['uuid'])
        assert False
    else:
        assert error_message == 'Well head and trajectory are inconsistent!'


@pytest.mark.parametrize(
    ('name', 'head', 'md', 'x', 'y', 'z'),
    [
        (1,           (1., 4.), [0, 3], [1., 0], [4., 0], [0, 3]),
        ('invalid_2', (1., '4.'), [0, 3], [1., 0], [4., 0], [0, 3]),
        ('invalid_3', (1., 4.), 'measured depth', [1., 0], [4., 0], [0, 3]),
        ('invalid_4', (1., 4.), [0, 3], ['x1', 'x2'], [4., 0], [0, 3]),
        ('invalid_5', (1., 4.), [0, 3], [1., 0], ['y1', 'y2'], [0, 3]),
        ('invalid_6', (1., 4.), [0, 3], [1., 0], [4., 0], ['z1', 'z2']),
    ]
)
def test_well_create_invalid_data(name, head, md, x, y, z):
    resp = session.post(
        'http://localhost:8070/api/well.create',
        json={
            'method': 'well.create',
            'params': {
                'name': name,
                'head': head,
                'MD': md,
                'X': x,
                'Y': y,
                'Z': z
            }
        }
    )

    assert resp.json()['error'] is not None


@pytest.mark.parametrize(
    ('return_trajectory'),
    [
        (False),
        (True)
    ]
)
def test_well_get(return_trajectory: bool):
    for uuid in uuids:
        resp = session.post(
            'http://localhost:8070/api/well.get',
            json={
                'method': 'well.get',
                'params': {
                    'uuid': uuid,
                    'return_trajectory': return_trajectory
                }
            }
        )

        result = dict(resp.json())
        data = result.get('data')

        if data is None:
            assert False

        if return_trajectory:
            for item in data.keys():
                assert item in ['name', 'head', 'MD', 'X', 'Y', 'Z']
        else:
            for item in data.keys():
                assert item in ['name', 'head']


@pytest.mark.parametrize(
    ('return_trajectory'),
    [
        (False),
        (True)
    ]
)
def test_well_get_not_existing(return_trajectory: bool):
    resp = session.post(
        'http://localhost:8070/api/well.get',
        json={
            'method': 'well.get',
            'params': {
                'uuid': str(uuid4()),
                'return_trajectory': return_trajectory
            }
        }
    )

    result = dict(resp.json())
    data = result.get('data')

    assert data is None


def test_well_at():
    for uuid in uuids:
        session.post(
            'http://localhost:8070/api/well.at',
            json={
                "method": "well.at",
                "params": {
                    "uuid": uuid,
                    "MD": 10.1546
                }
            }
        )


def test_well_at_not_existing_id():
    resp = session.post(
        'http://localhost:8070/api/well.at',
        json={
            "method": "well.at",
            "params": {
                "uuid": str(uuid4()),
                "MD": 10.1546
            }
        }
    )

    try:
        error_message: str = resp.json()['error']['message']
    except KeyError:
        assert False
    else:
        assert error_message == 'Well not found!'


def test_well_remove():
    for uuid in uuids:
        resp = session.post(
            'http://localhost:8070/api/well.remove',
            json={
                'method': 'well.remove',
                'params': {
                    'uuid': uuid,
                }
            }
        )

        assert resp.json()['error'] is None
