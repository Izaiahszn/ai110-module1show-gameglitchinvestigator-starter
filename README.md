# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

An AI was asked to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and left the game unplayable:

- You couldn't win.
- The hints lied to you.
- The secret number had commitment issues.

This repo documents the bugs I found, the fixes I applied, and the tests
that keep those fixes honest.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python -m streamlit run app.py`
3. Run the tests: `python -m pytest tests/`

## 🎯 Game Purpose

The player picks a difficulty, which sets a number range and an attempt
limit. The app draws a secret number in that range, and the player has a
limited number of guesses to find it. After each guess the game says
whether to go higher or lower, plus a hot/cold proximity hint. Guessing
correctly before running out of attempts wins the round and awards a score
based on how quickly you got there.

| Difficulty | Range | Attempts |
|------------|-------|----------|
| Easy | 1–20 | 6 |
| Normal | 1–100 | 8 |
| Hard | 1–50 | 5 |

## 🐛 Bugs Found

| # | Bug | What the player saw |
|---|-----|---------------------|
| 1 | **Backwards higher/lower hints** | The hint told you to go HIGHER when the secret was lower. It looked random because it only broke on *even* attempts. |
| 2 | **Secret number reset on every submit** | The secret changed each time you clicked Submit, so the game was unwinnable. Debug Info showed a different number every rerun. |
| 3 | **"New Game" button did nothing** | After winning or losing, clicking New Game left you stuck on the game-over screen. |
| 4 | **Answer revealed one guess early** | With 1 attempt still showing, a wrong guess ended the round and revealed the secret. |
| 5 | **Score went negative** | Repeated wrong guesses subtracted 5 each time with no floor, so the score dropped below zero. |
| 6 | **Attempt counter started at 1** | An off-by-one meant you effectively lost one of your allowed guesses. |

## 🔧 Fixes Applied

1. **Hints (bug 1)** — the old code converted the secret to a string on
   even attempts, so Python compared `"9" > "50"` *lexicographically*
   instead of numerically. `check_guess()` now takes two ints and compares
   them numerically, always.
2. **Secret persistence (bug 2)** — the secret was being regenerated on
   every script rerun. It is now created once inside an
   `if "secret" not in st.session_state` guard, so Streamlit's reruns leave
   it alone.
3. **New Game (bug 3)** — the reset handler left `status` as `"won"` or
   `"lost"`, so the game-over check stopped the script before the new round
   could start. The handler now resets *every* piece of state — secret,
   attempts, score, history, and status — then calls `st.rerun()`.
4. **Early reveal (bug 4)** — the end-of-game check compared against
   `attempt_limit - 1`. Changed to `st.session_state.attempts >= attempt_limit`
   so the round only ends after the final guess is actually used.
5. **Negative score (bug 5)** — `update_score()` now clamps its result with
   `max(1, min(100, new_score))`, keeping the score in a valid 1–100 range.
6. **Attempt counter (bug 6)** — attempts initialize to `0` instead of `1`.

All game logic now lives in [logic_utils.py](logic_utils.py) as pure
functions with no Streamlit dependency, which is what makes it testable
from [tests/test_game_logic.py](tests/test_game_logic.py).

## 📸 Demo Walkthrough

1. Launch with `python -m streamlit run app.py`. The scoreboard at the top
   shows Score, Attempts left, Wins, and Losses, with a progress bar
   underneath tracking attempts used.
2. Pick a difficulty in the sidebar. On Normal you get 8 attempts to find a
   number between 1 and 100.
3. Type a guess and click **Submit Guess 🚀**. Say the secret is 50 and you
   guess 80 — the app shows "📉 Go LOWER!" and a "🧊 Freezing" proximity
   caption.
4. Open **Developer Debug Info** and confirm the secret is *the same number*
   as before the submit. This is the state bug, fixed.
5. Guess 40. The hint flips to "📈 Go HIGHER!" and the proximity warms up to
   "♨️ Hot". The guess history table below shows both guesses and which
   direction each one was wrong in.
6. Enter something invalid like `abc` or an out-of-range number like `500`.
   The app rejects it with an error and **does not** consume an attempt.
7. Guess 50. Balloons fire, the app confirms "You won! The secret was 50",
   the Wins counter increments, and the score reflects how few attempts you
   used.
8. Click **New Game 🔁**. Everything resets — a fresh secret, attempts back
   to 0, empty history — and the game is immediately playable again. Losing
   a round works the same way: the app reveals the secret only after the
   *last* attempt is spent, and New Game recovers from it.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

35 tests covering the hint logic, input parsing, difficulty ranges, score
bounds, and the proximity feature.

```
$ python -m pytest tests/
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\imkil\Downloads\ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.13.0
collected 35 items

tests\test_game_logic.py ...................................       [100%]

============================= 35 passed in 0.20s ==============================
```

## 🚀 Stretch Features

**Enhanced UI and formatting**

- **Scoreboard metrics row** — Score, Attempts left, Wins, and Losses shown
  as `st.metric` tiles instead of buried in a sentence.
- **Attempt progress bar** — a visual `st.progress` bar showing how much of
  the attempt budget is spent.
- **Guess history table** — an `st.dataframe` listing every guess with the
  direction hint it produced, so the player can narrow the range without
  taking notes.
- **Win/loss session tracking** — wins and losses persist across rounds in
  session state, so New Game keeps the running tally.
- **Input guarding** — invalid or out-of-range guesses show a clear message
  and no longer waste an attempt.

**New gameplay feature: hot/cold proximity hints**

`proximity_hint()` in [logic_utils.py](logic_utils.py) reports how close a
guess is as Boiling 🔥 / Hot ♨️ / Warm 🌤️ / Cool ❄️ / Freezing 🧊. Distance is
measured as a *fraction of the difficulty's range*, so "close" means the
same thing on Easy (1–20) as on Normal (1–100). It's a pure function, so
it's covered by 7 of the 35 tests.

**Testing and style**

- Edge-case tests for empty input, `None`, letters, symbols, a bare `.`,
  decimal truncation, range boundaries, off-by-one guesses, unknown
  difficulty, and a zero-width range.
- `ruff check .` passes clean. See [ai_interactions.md](ai_interactions.md)
  for the before/after linting output.
