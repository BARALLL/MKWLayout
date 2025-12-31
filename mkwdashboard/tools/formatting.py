from datetime import timedelta


def to_ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return str(n) + suffix


def format_number(value):
    value = float(value)
    integer_part, _, fractional_part = f"{value:.10f}".partition(".")
    if len(integer_part) >= 5:
        scientific_notation = f"{value:.5e}"
        coefficient, exponent = scientific_notation.split("e")
        coefficient = coefficient.rstrip("0").rstrip(".")
        return f"{coefficient}e{exponent}"

    else:
        if len(fractional_part.rstrip("0")) > 5:
            return f"{value:.5e}"
        else:
            formatted_value = f"{value:.5f}".rstrip("0").rstrip(".")
            return formatted_value


def format_ms(milliseconds):
    delta = timedelta(milliseconds=milliseconds)
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = delta.microseconds // 1000

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    else:
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
