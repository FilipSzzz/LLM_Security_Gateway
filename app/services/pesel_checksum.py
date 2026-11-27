from datetime import date

CENTURY_BY_MONTH_OFFSET = {80: 1800, 0: 1900, 20: 2000, 40: 2100, 60: 2200}
WEIGHTS = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]


def check_validation(pesel: str) -> bool:
    if len(pesel) != 11 or not (pesel.isascii() and pesel.isdigit()):
        return False

    encoded_month = int(pesel[2:4])
    offset = encoded_month // 20 * 20
    year = CENTURY_BY_MONTH_OFFSET[offset] + int(pesel[:2])
    try:
        date(year, encoded_month - offset, int(pesel[4:6]))
    except ValueError:
        return False

    total = sum(int(digit) * weight for digit, weight in zip(pesel[:10], WEIGHTS, strict=True))
    return (10 - total % 10) % 10 == int(pesel[10])
