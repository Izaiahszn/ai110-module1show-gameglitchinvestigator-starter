from logic_utils import check_guess, update_score

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"


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
            score = update_score(current_score=score, outcome="Too High", attempt_number=attempt)
    
    assert score >= 1, f"Score should never go below 1, got {score}"


def test_numeric_comparison_for_higher_lower_hints():
    """Test that hints work properly with numeric comparison (not string)"""
    # When comparing 60 > 50 (both numeric), should return "Too High"
    outcome, message = check_guess(guess=60, secret=50)
    assert outcome == "Too High", f"Expected 'Too High', got '{outcome}'"
    
    # When comparing 40 < 50 (both numeric), should return "Too Low"  
    outcome, message = check_guess(guess=40, secret=50)
    assert outcome == "Too Low", f"Expected 'Too Low', got '{outcome}'"
