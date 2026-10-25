import datetime

import pytest
from freezegun import freeze_time

from moto.core.utils import (
    camelcase_to_pascal,
    camelcase_to_underscores,
    iso_8601_datetime_with_milliseconds,
    iso_8601_datetime_with_nanoseconds,
    pascal_to_camelcase,
    rfc_1123_datetime,
    set_value,
    str_to_rfc_1123_datetime,
    underscores_to_camelcase,
    unix_time,
    unix_time_millis,
)


@pytest.mark.parametrize(
    "_input,expected",
    [
        ("theNewAttribute", "the_new_attribute"),
        ("attri bute With Space", "attribute_with_space"),
        ("FirstLetterCapital", "first_letter_capital"),
        ("ListMFADevices", "list_mfa_devices"),
    ],
)
def test_camelcase_to_underscores(_input: str, expected: str) -> None:
    assert camelcase_to_underscores(_input) == expected


@pytest.mark.parametrize(
    "_input,expected",
    [("the_new_attribute", "theNewAttribute"), ("attribute", "attribute")],
)
def test_underscores_to_camelcase(_input: str, expected: str) -> None:
    assert underscores_to_camelcase(_input) == expected


@pytest.mark.parametrize(
    "_input,expected",
    [("TheNewAttribute", "theNewAttribute"), ("Attribute", "attribute")],
)
def test_pascal_to_camelcase(_input: str, expected: str) -> None:
    assert pascal_to_camelcase(_input) == expected


@pytest.mark.parametrize(
    "_input,expected",
    [("theNewAttribute", "TheNewAttribute"), ("attribute", "Attribute")],
)
def test_camelcase_to_pascal(_input: str, expected: str) -> None:
    assert camelcase_to_pascal(_input) == expected


@freeze_time("2015-01-01 12:00:00")
def test_unix_time() -> None:  # type: ignore[misc]
    assert unix_time() == 1420113600.0


def test_rfc1123_dates() -> None:
    with freeze_time("2012-03-04 05:00:05"):
        x = rfc_1123_datetime(datetime.datetime.now())
        assert x == "Sun, 04 Mar 2012 05:00:05 GMT"
        assert str_to_rfc_1123_datetime(x) == datetime.datetime.now()


def test_set_value() -> None:
    basic_dict = {"foo": None}
    set_value(basic_dict, "foo", "bar")
    assert basic_dict["foo"] == "bar"

    class BasicObject:
        foo = None

    basic_object = BasicObject()
    set_value(basic_object, "foo", "bar")
    assert basic_object.foo == "bar"
    nested_dict = {"foo": {"bar": None}}
    set_value(nested_dict, "foo.bar", "baz")
    assert nested_dict["foo"]["bar"] == "baz"

    class NestedObject:
        child = BasicObject()

    nested_object = NestedObject()
    set_value(nested_object, "child.foo", "bar")
    assert nested_object.child.foo == "bar"


@pytest.fixture(params=[True, False], ids=["py311", "pre_py311"])
def python_version_branch(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> bool:
    monkeypatch.setattr("moto.core.utils.PYTHON_311", request.param)
    return request.param


@freeze_time("2024-03-05 12:34:56.789012")
def test_unix_time_default_uses_current_utc_time(python_version_branch: bool) -> None:
    assert unix_time() == 1709642096.789012


@freeze_time("2024-03-05 12:34:56.789012")
def test_unix_time_millis_default_uses_current_utc_time(
    python_version_branch: bool,
) -> None:
    assert unix_time_millis() == pytest.approx(1709642096789.012)


@freeze_time("2024-03-05 12:34:56.789012")
def test_iso_8601_nanoseconds_uses_current_utc_time(
    python_version_branch: bool,
) -> None:
    assert iso_8601_datetime_with_nanoseconds() == "2024-03-05T12:34:56.789012000Z"


@freeze_time("2024-03-05 12:34:56.789012")
def test_iso_8601_milliseconds_default_uses_current_utc_time(
    python_version_branch: bool,
) -> None:
    assert iso_8601_datetime_with_milliseconds() == "2024-03-05T12:34:56.789Z"


def test_unix_time_default_is_current_epoch_seconds(
    python_version_branch: bool,
) -> None:
    before = datetime.datetime.now(datetime.timezone.utc).timestamp()
    value = unix_time()
    after = datetime.datetime.now(datetime.timezone.utc).timestamp()
    assert before - 1 <= value <= after + 1
