"""Photo print order helpers, hardened against invalid input (Lab 7).

Contract: none of these functions raise an exception for bad input.
They return a result for valid input and ``None`` for invalid input.
"""
import math


def parse_order(text):
    """Parse ``"size:copies"`` into ``(SIZE, copies)``.

    Returns ``None`` if ``text`` is not a string, does not contain exactly one
    colon, has an empty size, or has a copies value that is not a whole number
    of at least 0.
    """
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    size = parts[0].strip().upper()
    if not size:
        return None
    try:
        copies = int(parts[1])
    except ValueError:
        return None
    if copies < 0:
        return None
    return size, copies


def file_size_average(sizes_csv):
    """Return the whole-number average of a CSV list of file sizes in MB.

    Returns ``None`` for non-string input, empty/non-numeric entries or
    negative sizes (this also removes the old divide-by-zero risk).
    """
    if not isinstance(sizes_csv, str):
        return None
    try:
        values = [int(r) for r in sizes_csv.split(',')]
    except ValueError:
        return None
    if not values or any(v < 0 for v in values):
        return None
    return sum(values) // len(values)


def payable_amount(text):
    """Return ``amount * 1.18 - discount`` (never below 0) for ``"amount|discount"``.

    Returns ``None`` for non-string input, anything other than exactly two
    numbers, negative or non-finite (nan/inf) values, or an overflowing total.
    """
    if not isinstance(text, str):
        return None
    parts = text.split('|')
    if len(parts) != 2:
        return None
    try:
        amount = float(parts[0])
        discount = float(parts[1])
    except ValueError:
        return None
    if not (math.isfinite(amount) and math.isfinite(discount)):
        return None
    if amount < 0 or discount < 0:
        return None
    total = amount * 1.18 - discount
    if not math.isfinite(total):
        return None
    return max(total, 0)


def main():
    print("==== Running parse_order ====")
    user_input = input("Enter print size:copies (e.g. 4x6:25): ")
    result = parse_order(user_input)
    if result is None:
        print("Invalid input. Expected size:copies, e.g. 4x6:25")
    else:
        print("Size and Copies:", result)

    print("\n==== Running file_size_average ====")
    user_input = input("Enter file sizes in MB as CSV (e.g. 4,8,12): ")
    result = file_size_average(user_input)
    if result is None:
        print("Invalid input. Expected whole-number sizes, e.g. 4,8,12")
    else:
        print("Average File Size:", result)

    print("\n==== Running payable_amount ====")
    user_input = input("Enter amount|discount (e.g. 450|50): ")
    result = payable_amount(user_input)
    if result is None:
        print("Invalid input. Expected amount|discount, e.g. 450|50")
    else:
        print("Payable Amount:", result)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
