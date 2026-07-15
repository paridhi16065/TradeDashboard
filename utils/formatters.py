def format_currency(value):
    sign = "-" if value < 0 else ""
    value = abs(value)

    if value >= 1_000_000_000_000:
        return f"{sign}${value / 1_000_000_000_000:.2f}T"

    elif value >= 1_000_000_000:
        return f"{sign}${value / 1_000_000_000:.2f}B"

    elif value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f}M"

    return f"{sign}${value:,.0f}"
