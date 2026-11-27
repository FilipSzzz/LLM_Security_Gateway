import pytest

from app.services.pesel_checksum import check_validation


@pytest.mark.parametrize(
    ("pesel", "expected"),
    [
        ("44051401359", True),  # 1944-05-14
        ("02270803624", True),  # 2002-07-08, month 27 = July + 20
        ("00222900016", True),  # 2000-02-29, 2000 is a leap year
        ("00022900010", False),  # 1900-02-29, 1900 is not a leap year
        ("44131401350", False),  # month 13 does not exist
        ("44051401358", False),  # wrong check digit
        ("4405140135", False),  # too short
        ("440514013590", False),  # too long
        ("4405140135²", False),  # Unicode digit, used to crash int()
    ],
)
def test_check_validation(pesel, expected):
    assert check_validation(pesel) is expected
