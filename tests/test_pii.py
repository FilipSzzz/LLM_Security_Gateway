import pytest

from app.services.pii import mask_cards, mask_pesels, mask_pii


def test_valid_pesel_is_masked():
    assert mask_pesels("my id is 44051401359 ok") == ("my id is [PESEL] ok", 1)


@pytest.mark.parametrize("text", ["44051401358", "440514013590"])
def test_invalid_or_too_long_pesel_is_left(text):
    assert mask_pesels(text) == (text, 0)


@pytest.mark.parametrize(
    "card", ["4111 1111 1111 1111", "4111-1111-1111-1111", "4111111111111111", "5555555555554444"]
)
def test_valid_cards_are_masked(card):
    assert mask_cards(f"card {card} end") == ("card [CARD] end", 1)


def test_card_failing_luhn_is_left():
    assert mask_cards("4111111111111112") == ("4111111111111112", 0)


def test_mask_pii_all_kinds():
    text = "44051401359 jan@example.com 4111 1111 1111 1111"
    assert mask_pii(text) == (
        "[PESEL] [EMAIL] [CARD]",
        {"card": 1, "pesel": 1, "email": 1},
    )


def test_no_pii_unchanged():
    assert mask_pii("hello world 123") == ("hello world 123", {"card": 0, "pesel": 0, "email": 0})
