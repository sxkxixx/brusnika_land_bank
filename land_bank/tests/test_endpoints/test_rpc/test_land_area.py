import pytest


@pytest.fixture()
async def f() -> dict:
    return {'1': '2'}


@pytest.mark.asyncio
async def test_get_empty_land_area(f):
    print(await f)
    assert 1 == 1
