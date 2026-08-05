# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Two tasks, in order:

1. "Move all the game logic out of `app.py` into `logic_utils.py` so it can
   be tested without Streamlit, then make `pytest` pass."
2. "Add a hot/cold proximity hint feature and improve the UI — I want to see
   my score and attempts at a glance and a history of my guesses."

**What did the agent do?**

For the refactor:

- Pulled `get_range_for_difficulty`, `parse_guess`, `check_guess`, and
  `update_score` out of `app.py` into `logic_utils.py` as pure functions
  with no Streamlit imports.
- Rewrote `app.py` to import them, leaving only UI and session-state
  handling behind.
- Ran `pytest` and iterated until all tests passed.

For the feature work:

- Added `proximity_hint()` to `logic_utils.py`, measuring distance as a
  fraction of the difficulty range so the labels mean the same thing on
  Easy (1–20) and Normal (1–100).
- Added an `st.metric` scoreboard row, an `st.progress` attempt bar, and an
  `st.dataframe` guess history to `app.py`.
- Added input guarding so invalid or out-of-range guesses don't burn an
  attempt.
- Wrote tests for the new function and re-ran the suite.

**What did you have to verify or fix manually?**

- The agent's first pass at `proximity_hint` divided by `high - low` with
  no guard. On a zero-width range that's a `ZeroDivisionError`. I asked for
  a guard and added `test_proximity_handles_degenerate_range_without_dividing_by_zero`
  to lock it down.
- I had to check `st.dataframe(width="stretch")` against the installed
  Streamlit version (1.58.0) — the older API was `use_container_width`, and
  agents tend to write whichever one was more common in their training
  data. It was correct for this version, but it was worth confirming rather
  than assuming.
- Passing tests do not mean the app runs. I launched the app headless and
  hit it with a request to confirm it returned HTTP 200 with a clean
  stderr, because nothing in the test suite imports `app.py` at all.
- The agent left its bug-fix comments describing what it changed. I kept
  those but rewrote a few that described the fix without explaining *why*
  the original code was wrong, which is the part worth remembering.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

**Prompt used:** *"Here are `check_guess`, `parse_guess`,
`get_range_for_difficulty`, and `update_score`. What edge cases am I not
testing? I only have three tests for the happy path."*

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Empty string and `None` input | "What happens if the user submits nothing?" | `test_parse_guess_rejects_empty_string`, `test_parse_guess_rejects_none` | ✅ Pass | Streamlit's `text_input` returns `""` on first load, so this fires on literally every page load. Worth having. |
| A bare `"."` | "Are there strings that get past your dot check but still crash?" | `test_parse_guess_rejects_malformed_decimal` | ✅ Pass | Good catch. `"."` contains a dot so it takes the `float()` branch, and `float(".")` raises. The existing `except` caught it, but nothing proved that until now. |
| Range boundary values | "Test the edges of the guessing range" | `test_guess_at_lower_boundary`, `test_guess_at_upper_boundary` | ✅ Pass | Off-by-one bugs live at boundaries, and this project already had one in the attempt counter. |
| Off-by-one around the secret | "What about guessing 49 and 51 when the secret is 50?" | `test_off_by_one_below_secret`, `test_off_by_one_above_secret` | ✅ Pass | Cheap, and it pins down the `>` vs `>=` behavior in `check_guess` so a future "cleanup" can't silently change it. |
| Lexicographic comparison trap | "Write a test that would fail if someone reintroduced the string bug" | `test_hint_direction_for_lexicographic_trap` (9 vs 50) | ✅ Pass | The most valuable test in the file. 9 vs 50 is exactly where `"9" > "50"` goes wrong, so this is a targeted regression test for the original bug. |
| Zero-width range in `proximity_hint` | "Can this function divide by zero?" | `test_proximity_handles_degenerate_range_without_dividing_by_zero` | ❌ Failed first | This one found a real bug — my first version had no guard and raised `ZeroDivisionError`. Added an early return for `span <= 0`, then it passed. |
| Unknown difficulty string | "What if difficulty doesn't match any branch?" | `test_range_unknown_difficulty_falls_back_to_normal` | ✅ Pass | Confirms the fallback `return 1, 100` is intentional behavior and not dead code. |
| Unrecognized score outcome | "What if `outcome` is a string you didn't plan for?" | `test_score_unknown_outcome_is_unchanged` | ✅ Pass | Slightly paranoid since only three outcomes exist, but it documents that unknown outcomes are a no-op rather than a crash. |

**Suggestions I rejected:** the AI also proposed tests for guesses larger
than `sys.maxsize` and for unicode digit strings like `"٥"`. I skipped both.
They pass either way and don't correspond to anything a real player would
type into the box, so they'd be noise in the suite.

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
I don't have a linter set up on this project. What should I use for a small
Python codebase, and can you walk me through fixing whatever it flags?
```

The AI recommended `ruff` over `flake8` for speed and because it bundles
import sorting, so I installed it with `pip install ruff`.

**Linting output before:**

```
$ python -m ruff check . --statistics
4       RUF059  [ ] unused-unpacked-variable
2       I001    [*] unsorted-imports
1       BLE001  [ ] blind-except
1       PLR1730 [*] if-stmt-min-max
Found 8 errors.
[*] 3 fixable with the `--fix` option
```

**Changes applied:**

- **`I001` (unsorted imports, 2)** — fixed automatically by `ruff check --fix`
  in `app.py` and `tests/test_game_logic.py`.
- **`PLR1730` (if-stmt-min-max, 1)** — auto-fixed. A three-line
  `if points < 10: points = 10` in `update_score` collapsed to
  `points = max(points, 10)`.
- **`BLE001` (blind except, 1)** — fixed by hand. `parse_guess` had a bare
  `except Exception`, which would swallow a `KeyboardInterrupt`-adjacent
  problem or a genuine bug as "that is not a number." Narrowed to
  `except (TypeError, ValueError)`, which is what `int()` and `float()`
  actually raise.
- **`RUF059` (unused unpacked variable, 4)** — fixed by hand. The tests
  wrote `outcome, message = check_guess(...)` and then never used
  `message`. Renamed to `_message` to signal the value is deliberately
  discarded.

**Linting output after:**

```
$ python -m ruff check .
All checks passed!
```

The `BLE001` fix was the only one that changed runtime behavior. The rest
were readability. I'd argue the blind-except was a real (if minor) bug —
it meant any unexpected failure inside `parse_guess` would have been
reported to the player as bad input rather than surfacing as an error.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

*Not attempted.* I did all of the AI work on this project with Claude 4.5
Haiku in VS Code and didn't run the same prompt through a second model, so
I don't have an honest comparison to write up here rather than a guessed
one.
