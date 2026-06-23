def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int, secret: int):
    """
    Compare an integer guess with an integer secret.

    Returns:
        A tuple: (outcome, message), where outcome is "Win", "Too High",
        or "Too Low".
    """
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"

def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        new_score = current_score + points
    elif outcome == "Too High":
        if attempt_number % 2 == 0:
            new_score = current_score + 5
        else:
            new_score = current_score - 5
    elif outcome == "Too Low":
        new_score = current_score - 5
    else:
        new_score = current_score
    
    # BUG FIX: Score was going negative due to unbounded deductions
    # Penalty deductions on "Too High" (odd attempts) and "Too Low" could reduce score below 0
    # Solution: Clamp score to stay within valid bounds: minimum 1, maximum 100 (no 0 allowed)
    return max(1, min(100, new_score))
