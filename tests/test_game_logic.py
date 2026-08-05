from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    proximity_hint,
    update_score,
)

# ---------------------------------------------------------------------------
# check_guess: the core hint logic (the bug that made the game unwinnable)
# ---------------------------------------------------------------------------


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _message = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _message = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _message = check_guess(40, 50)
    assert outcome == "Too Low"


def test_numeric_comparison_for_higher_lower_hints():
    """Hints must use numeric comparison, not string comparison.

    The original bug converted the secret to a string on even attempts, so
    "9" > "50" was True (lexicographic) and the hint pointed the wrong way.
    """
    outcome, _message = check_guess(guess=60, secret=50)
    assert outcome == "Too High", f"Expected 'Too High', got '{outcome}'"

    outcome, _message = check_guess(guess=40, secret=50)
    assert outcome == "Too Low", f"Expected 'Too Low', got '{outcome}'"


def test_hint_direction_for_lexicographic_trap():
    """9 vs 50 is the exact pair that string comparison got backwards."""
    outcome, _message = check_guess(guess=9, secret=50)
    assert outcome == "Too Low"


def test_hint_message_matches_outcome():
    """The message shown to the player must agree with the outcome."""
    _outcome, high_message = check_guess(60, 50)
    _outcome, low_message = check_guess(40, 50)
    assert "LOWER" in high_message
    assert "HIGHER" in low_message


# ---------------------------------------------------------------------------
# Edge cases at the boundaries of the guessing range
# ---------------------------------------------------------------------------


def test_guess_at_lower_boundary():
    outcome, _message = check_guess(1, 1)
    assert outcome == "Win"


def test_guess_at_upper_boundary():
    outcome, _message = check_guess(100, 100)
    assert outcome == "Win"


def test_off_by_one_below_secret():
    outcome, _message = check_guess(49, 50)
    assert outcome == "Too Low"


def test_off_by_one_above_secret():
    outcome, _message = check_guess(51, 50)
    assert outcome == "Too High"


# ---------------------------------------------------------------------------
# parse_guess: input validation
# ---------------------------------------------------------------------------


def test_parse_guess_accepts_plain_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


def test_parse_guess_truncates_decimal():
    ok, value, _err = parse_guess("42.9")
    assert ok is True
    assert value == 42


def test_parse_guess_accepts_negative_number():
    """Out-of-range values still parse; the game logic handles the range."""
    ok, value, _err = parse_guess("-5")
    assert ok is True
    assert value == -5


def test_parse_guess_rejects_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_parse_guess_rejects_none():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_parse_guess_rejects_letters():
    ok, value, err = parse_guess("fifty")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


def test_parse_guess_rejects_symbols():
    ok, _value, err = parse_guess("!!")
    assert ok is False
    assert err == "That is not a number."


def test_parse_guess_rejects_malformed_decimal():
    """A bare dot hits the float() branch and must not raise."""
    ok, _value, err = parse_guess(".")
    assert ok is False
    assert err == "That is not a number."


# ---------------------------------------------------------------------------
# get_range_for_difficulty
# ---------------------------------------------------------------------------


def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)


def test_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 100)


def test_range_hard():
    assert get_range_for_difficulty("Hard") == (1, 50)


def test_range_unknown_difficulty_falls_back_to_normal():
    assert get_range_for_difficulty("Impossible") == (1, 100)


def test_range_low_is_never_negative():
    """Regression: the secret must never be drawn from a negative range."""
    for difficulty in ["Easy", "Normal", "Hard", "Unknown"]:
        low, high = get_range_for_difficulty(difficulty)
        assert low >= 1, f"{difficulty} produced a low bound of {low}"
        assert high > low


# ---------------------------------------------------------------------------
# update_score: bounds checking
# ---------------------------------------------------------------------------


def test_score_clamped_at_lower_bound():
    """Test that score cannot go below 1 (fix for negative score bug)"""
    # Start with score 1, make a "Too Low" guess (subtracts 5)
    # Without clamping: 1 - 5 = -4, but it should clamp to 1
    result = update_score(current_score=1, outcome="Too Low", attempt_number=1)
    assert result >= 1, f"Score should not go below 1, got {result}"
    assert result == 1


def test_score_clamped_at_upper_bound():
    """Test that score cannot go above 100 (fix for negative score bug)"""
    # Start with score 95, win with early attempt (adds many points)
    # Without clamping: 95 + 90 = 185, but it should clamp to 100
    result = update_score(current_score=95, outcome="Win", attempt_number=1)
    assert result <= 100, f"Score should not exceed 100, got {result}"
    assert result == 100


def test_score_stays_within_bounds_after_multiple_deductions():
    """Test that repeated penalty deductions don't push score below 1"""
    # Simulate multiple "Too High" odd attempts (each subtracts 5)
    score = 10
    for attempt in range(1, 6):  # attempts 1, 3, 5, 7, 9
        if attempt % 2 == 1:  # Odd attempts on "Too High" subtract 5
            score = update_score(
                current_score=score,
                outcome="Too High",
                attempt_number=attempt,
            )

    assert score >= 1, f"Score should never go below 1, got {score}"


def test_score_unknown_outcome_is_unchanged():
    assert update_score(current_score=40, outcome="Sideways", attempt_number=2) == 40


def test_win_late_still_awards_minimum_points():
    """A very late win should still award the 10-point floor, not 0 or less."""
    result = update_score(current_score=10, outcome="Win", attempt_number=20)
    assert result == 20  # 10 existing + the 10-point floor


# ---------------------------------------------------------------------------
# proximity_hint: the hot/cold stretch feature
# ---------------------------------------------------------------------------


def test_proximity_exact_match_is_correct():
    label, _emoji = proximity_hint(50, 50, 1, 100)
    assert label == "Correct"


def test_proximity_very_close_is_boiling():
    label, _emoji = proximity_hint(52, 50, 1, 100)
    assert label == "Boiling"


def test_proximity_far_away_is_freezing():
    label, _emoji = proximity_hint(99, 5, 1, 100)
    assert label == "Freezing"


def test_proximity_is_symmetric_above_and_below():
    """Being 10 away should read the same whether you are high or low."""
    above, _ = proximity_hint(60, 50, 1, 100)
    below, _ = proximity_hint(40, 50, 1, 100)
    assert above == below


def test_proximity_scales_with_difficulty_range():
    """Being 3 away is close on Normal (1-100) but not on Easy (1-20)."""
    normal, _ = proximity_hint(13, 10, 1, 100)
    easy, _ = proximity_hint(13, 10, 1, 20)
    assert normal == "Boiling"
    assert easy == "Warm"


def test_proximity_handles_degenerate_range_without_dividing_by_zero():
    """A zero-width range must not raise ZeroDivisionError."""
    label, _emoji = proximity_hint(5, 7, 3, 3)
    assert label == "Freezing"


def test_proximity_always_returns_an_emoji():
    for guess in [1, 25, 50, 75, 100]:
        label, emoji = proximity_hint(guess, 50, 1, 100)
        assert label
        assert emoji
