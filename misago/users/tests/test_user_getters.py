import pytest

from ..get import (
    get_user_by_email,
    get_user_by_id,
    get_user_by_name,
    get_user_by_name_or_email,
)


@pytest.mark.asyncio
async def test_user_can_be_get_by_id(user):
    assert user == await get_user_by_id(user.id)


@pytest.mark.asyncio
async def test_getting_user_by_nonexistent_id_returns_none(db):
    assert await get_user_by_id(1) is None


@pytest.mark.asyncio
async def test_user_can_be_get_by_email(user):
    assert user == await get_user_by_email(user.email)


@pytest.mark.asyncio
async def test_getting_user_by_nonexistent_email_returns_none(db):
    assert await get_user_by_name("nonexistent@email.com") is None


@pytest.mark.asyncio
async def test_user_can_be_get_by_name(user):
    assert user == await get_user_by_name(user.name)


@pytest.mark.asyncio
async def test_getting_user_by_nonexistent_name_returns_none(db):
    assert await get_user_by_name("nonexistent") is None


@pytest.mark.asyncio
async def test_name_or_email_getter_returns_user_with_matching_name(user):
    assert user == await get_user_by_name_or_email(user.name)


@pytest.mark.asyncio
async def test_name_or_email_getter_returns_user_with_matching_email(user):
    assert user == await get_user_by_name_or_email(user.email)


@pytest.mark.asyncio
async def test_name_or_email_getter_returns_none_if_no_user_is_found(db):
    assert await get_user_by_name_or_email("nonexistent") is None