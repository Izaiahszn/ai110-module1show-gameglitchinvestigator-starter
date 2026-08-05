import random

import streamlit as st

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    proximity_hint,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("A number guessing game — debugged, refactored, and tested.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 1

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Wins and losses persist across rounds so the player can track a session.
if "wins" not in st.session_state:
    st.session_state.wins = 0

if "losses" not in st.session_state:
    st.session_state.losses = 0

attempts_left = attempt_limit - st.session_state.attempts

# --- Scoreboard -----------------------------------------------------------
# STRETCH (UI): a metrics row gives the player the whole game state at a
# glance instead of burying it in prose.
score_col, attempts_col, wins_col, losses_col = st.columns(4)
score_col.metric("Score", st.session_state.score)
attempts_col.metric("Attempts left", max(0, attempts_left))
wins_col.metric("Wins", st.session_state.wins)
losses_col.metric("Losses", st.session_state.losses)

# STRETCH (UI): a progress bar makes running out of attempts feel visible.
used_fraction = min(1.0, st.session_state.attempts / attempt_limit)
st.progress(used_fraction, text=f"{st.session_state.attempts} of {attempt_limit} attempts used")

st.subheader("Make a guess")

st.info(f"Guess a number between {low} and {high}.")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}",
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # BUG FIX: the New Game button did nothing once a round ended.
    # The status stayed "won" or "lost", so the game-over check below
    # stopped the script before any new guess could be made.
    # Solution: reset every piece of game state, including status.
    # BUG FIX: attempts must start at 0, not 1 (off-by-one in the counter).
    st.session_state.attempts = 0
    st.session_state.score = 1
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.error(err)
        # A rejected input should not burn an attempt.
        st.session_state.attempts -= 1
    elif guess_int < low or guess_int > high:
        st.warning(f"Guess must be between {low} and {high}.")
        st.session_state.attempts -= 1
    else:
        # BUG FIX: the higher/lower hints were backwards on even attempts.
        # The old code converted the secret to a string first, so Python
        # compared them lexicographically ("9" > "50" is True) instead of
        # numerically. Solution: always compare two ints.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        # STRETCH (UI): record the direction alongside the guess so the
        # history table can show why each guess failed.
        st.session_state.history.append(
            {"Guess": guess_int, "Hint": outcome}
        )

        if show_hint:
            st.warning(message)

            # STRETCH (feature): hot/cold proximity feedback on top of the
            # plain higher/lower hint.
            if outcome != "Win":
                label, emoji = proximity_hint(
                    guess_int, st.session_state.secret, low, high
                )
                st.caption(f"{emoji} {label}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.session_state.wins += 1
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        # BUG FIX: the game used to reveal the answer one guess early.
        # The comparison was `>=` against `attempt_limit - 1`, ending the
        # round on the second-to-last attempt. Solution: only end the game
        # once attempts actually reach the limit.
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.session_state.losses += 1
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )

# STRETCH (UI): a running table of past guesses so the player can narrow
# down the range without keeping notes on paper.
if st.session_state.history:
    st.divider()
    st.subheader("Your guesses so far")
    st.dataframe(
        st.session_state.history,
        width="stretch",
        hide_index=True,
    )

st.divider()
st.caption("Bugs found, fixes applied, tests passing.")
