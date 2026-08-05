# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

**What did the game look like the first time you ran it?**

It looked like a normal guessing game. There was a text box, a Submit
button, a difficulty picker in the sidebar, and a Developer Debug Info
panel that showed the secret number. You type a number, you get told
higher or lower, and you have a limited number of attempts. It looked
fine until I actually tried to win, and then nothing about it worked the
way it was supposed to.

**Concrete bugs I noticed at the start:**

1. The higher/lower hints were backwards. It would tell me to go HIGHER
   when I was already above the secret number.
2. The secret number changed every single time I hit Submit. I could see
   it changing in the Debug Info panel, which meant the game was
   impossible to win by design, not by bad luck.
3. The New Game button did nothing once the round ended. I would win or
   lose and then be stuck on the game-over screen forever.
4. The score would go negative after a few wrong guesses.
5. The game revealed the answer on the second-to-last attempt instead of
   the last one, so I lost a guess I should have had.

**Bug Reproduction Log**

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Secret is 50 (from Debug Info). Guess `80`, then `90`. | Both should say "Go LOWER". | First said "Go LOWER", second said "Go HIGHER" even though 90 is further above 50. The hint flipped depending on whether the attempt count was even or odd. | No error. Silent wrong answer, which is why it took so long to spot. |
| Note the secret in Debug Info, submit any guess, look again. | Secret stays the same for the whole round. | Secret was a different number every submit. Guessing correctly was impossible. | No error. `st.session_state` was never actually holding the value. |
| Win or lose a round, then click "New Game 🔁". | Game resets and is playable again. | Nothing happened. The game-over message stayed and the input did nothing. | No error. The script hit `st.stop()` before the reset could take effect. |
| On Normal (8 attempts), guess wrong 7 times. | Should still have 1 attempt left. | Game ended and revealed the secret with 1 attempt still showing. | No error. Off-by-one in the end-of-game check. |
| Guess wrong repeatedly from a low score. | Score should have a floor. | Score dropped below 0 and kept going negative. | No error, just a nonsense number in the UI. |

---

## 2. How did you use AI as a teammate?

**Which AI tools did you use on this project?**

Claude in VS Code (Claude 4.5 Haiku), mostly in chat, and then in agent
mode for the refactor and the stretch features.

**An AI suggestion that was correct:**

I asked it why my score was showing negative numbers. It pointed out that
`update_score` subtracts 5 for wrong guesses with nothing stopping it at
the bottom, and suggested clamping the return value with
`max(1, min(100, new_score))`. I verified it two ways: I ran the app and
deliberately guessed wrong over and over until the score bottomed out at 1
and stayed there, and I wrote `test_score_clamped_at_lower_bound` and
`test_score_clamped_at_upper_bound` to prove it in isolation. Both passed,
and the manual run matched.

**An AI suggestion that was incorrect or misleading:**

When I first asked about the broken hints, it told me the comparison
operators in `check_guess` were simply flipped and that swapping `>` for
`<` would fix it. I tried that and the game got *worse* — now the hints
were wrong on the attempts that used to be right. That's when I realized
the AI had only looked at `check_guess` and not at how `app.py` was
calling it. The real problem was upstream: on even attempts the secret was
being converted to a string before being passed in, so Python was
comparing `"9" > "50"` lexicographically, and `"9"` sorts after `"5"`.
The lesson was that the AI confidently diagnosed the function I showed it
instead of asking to see the caller, and I should have given it the whole
picture up front.

---

## 3. Debugging and testing your fixes

**How did you decide whether a bug was really fixed?**

At first I just ran `streamlit run app.py` and played the game with the
Developer Debug Info panel open so I could see the secret. That was enough
to catch the obvious stuff, but it was slow and unreliable for the hint bug
specifically, because that one only broke on even attempts. I had to
remember to check the attempt count every time, and I missed it more than
once. So I stopped trusting manual play as proof and started writing tests
for anything I claimed to have fixed.

**Describe at least one test you ran and what it showed you:**

The most useful one was `test_hint_direction_for_lexicographic_trap`,
which asserts that `check_guess(9, 50)` returns `"Too Low"`. The 9 vs 50
pair is the exact case that string comparison gets backwards, so if anyone
ever reintroduces a string conversion, that test fails immediately instead
of the bug hiding until someone happens to guess a single-digit number on
an even attempt. I also wrote `test_parse_guess_rejects_malformed_decimal`
for the input `"."`, which I only thought to try because the parsing code
branches on whether there's a dot in the string — a bare dot goes down the
`float()` path and would have crashed if it weren't caught. The full suite
is 35 tests and all of them pass.

**Did AI help you design or understand any tests?**

Yes, more than I expected. The three starter tests were straightforward
and I wrote those myself. But when I asked the AI for edge cases I might
be missing, it suggested things I hadn't considered: `None` input, a bare
`"."`, the boundary values at each end of the range, off-by-one guesses on
either side of the secret, and a zero-width range for the proximity
function so it can't divide by zero. Some of those were paranoid, but the
zero-width range one was a real hole — my first version of
`proximity_hint` would have thrown `ZeroDivisionError`.

---

## 4. What did you learn about Streamlit and state?

**How would you explain Streamlit "reruns" and session state to a friend?**

Every time you touch anything in a Streamlit app — click a button, type in
a box, change a dropdown — Streamlit throws away the whole page and reruns
your Python file from line 1 to the bottom. It's not like a normal web app
where you update one piece; the entire script executes again from scratch.
That means any regular variable you create is brand new every single time,
which is exactly why the secret number kept changing: `random.randint()`
was running on every rerun. `st.session_state` is the one thing that
survives, like a dictionary Streamlit keeps in its pocket between reruns.
The pattern that fixed it is checking `if "secret" not in st.session_state`
first, so the value gets created once and then left alone. Once that
clicked, three of the bugs turned out to be the same misunderstanding
wearing different hats.

---

## 5. Looking ahead: your developer habits

**One habit or strategy from this project I want to reuse:**

Writing a test the moment I think I've fixed something, before I move on.
The hint bug was intermittent and I "fixed" it twice before it was
actually fixed — manual play kept fooling me because I wasn't tracking
whether the attempt number was even. A test doesn't get fooled. Running
`pytest` before committing takes two seconds and would have told me
immediately.

**One thing I would do differently next time working with AI:**

Give it the caller, not just the broken function. The single worst
detour I took was because I showed the AI `check_guess` in isolation and
it confidently told me to flip the operators, when the actual bug was in
`app.py` converting the secret to a string before calling it. The AI
answered the question I asked instead of the question I meant, and that's
on me for scoping it too narrowly. Next time I'll paste the surrounding
code or describe how the function gets used.

**How this project changed the way I think about AI generated code:**

AI-generated code can look completely finished and still be broken in ways
that produce no error at all. Every one of these bugs was silent — no
stack trace, no red text, just wrong behavior — and the original code came
with a comment claiming it was production-ready. I also noticed the AI
fills in a lot of assumptions when the prompt is vague, and those
assumptions are where the bugs live. I trust it now as something that
gets me a fast first draft, but the verifying is my job, and tests are the
only version of verifying that actually holds up.
