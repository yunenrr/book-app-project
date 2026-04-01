import pytest

from utils import get_book_details, MIN_YEAR, CURRENT_YEAR
from exceptions import MaxRetriesExceededError


def _mock_inputs(monkeypatch, inputs):
    it = iter(inputs)
    monkeypatch.setattr('builtins.input', lambda prompt='': next(it))


def test_get_book_details_accepts_valid_year(monkeypatch):
    _mock_inputs(monkeypatch, ['My Title', 'My Author', str(CURRENT_YEAR)])
    title, author, year = get_book_details()
    assert title == 'My Title'
    assert author == 'My Author'
    assert year == CURRENT_YEAR


def test_get_book_details_rejects_empty_year_then_accept(monkeypatch):
    # First year attempt is empty (invalid), second attempt is MIN_YEAR (valid)
    _mock_inputs(monkeypatch, ['T', 'A', '', str(MIN_YEAR)])
    title, author, year = get_book_details()
    assert year == MIN_YEAR


def test_get_book_details_rejects_non_numeric_then_accept(monkeypatch):
    _mock_inputs(monkeypatch, ['T', 'A', 'abcd', '2000'])
    title, author, year = get_book_details()
    assert year == 2000


def test_get_book_details_max_retries_exceeded(monkeypatch):
    # Provide three invalid year attempts to trigger MaxRetriesExceededError
    inputs = ['T', 'A', 'bad', 'also bad', 'still bad']
    _mock_inputs(monkeypatch, inputs)
    with pytest.raises(MaxRetriesExceededError):
        get_book_details()


def test_get_book_details_accepts_min_and_max(monkeypatch):
    # MIN_YEAR
    _mock_inputs(monkeypatch, ['T1', 'A1', str(MIN_YEAR)])
    t1, a1, y1 = get_book_details()
    assert y1 == MIN_YEAR

    # CURRENT_YEAR
    _mock_inputs(monkeypatch, ['T2', 'A2', str(CURRENT_YEAR)])
    t2, a2, y2 = get_book_details()
    assert y2 == CURRENT_YEAR
