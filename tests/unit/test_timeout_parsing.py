"""Test timeout parsing utilities"""

import pytest
from arcsim.models.timeout import parse_duration


def test_parse_seconds():
    assert parse_duration("30s") == 30
    assert parse_duration("5s") == 5


def test_parse_minutes():
    assert parse_duration("5m") == 300
    assert parse_duration("1m") == 60


def test_parse_hours():
    assert parse_duration("1h") == 3600
    assert parse_duration("2h") == 7200


def test_parse_milliseconds():
    assert parse_duration("30000ms") == 30
    assert parse_duration("5000ms") == 5


def test_parse_plain_number():
    assert parse_duration("30") == 30
    assert parse_duration("120") == 120


def test_parse_invalid():
    assert parse_duration("") is None
    assert parse_duration(None) is None
    assert parse_duration("invalid") is None


def test_parse_case_insensitive():
    assert parse_duration("30S") == 30
    assert parse_duration("5M") == 300
