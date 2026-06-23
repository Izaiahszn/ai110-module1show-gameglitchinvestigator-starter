# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
The game looked like a guessing game where it would take an input and you would just input a number and have a certain amount of guess to guess that number correctly.
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  the hint was broken
  the restart game didn't work
  was getting a negative value for the correct number
  
  
  


**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|The hints would say higher and lower with the same number | to say higher or lower depending on the secret value |does not change even when you are higher or closer | none |
|the actual value would be a negative number when it was suppoed to be from 1-100 | the value needed to be from 1-100 | it was a negative number  | negative number would be the answer|
|the new game feature doesn't work | would restart the game | would not restart |game would freeze / stay the same|
on the second to last submission after you submit you get the real answer if you don't guess correctly.| This should only happen after the last submission which is 1, where if you guess incorrectly you see the real answer| none |


---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  Claude for VS Code 4.5 Haiku
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  The AI agent used a minimum function (which was 1) in the 1 - 100 to make sure we would not get negative numbers for the secret value.
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
An example is where the hint function wasn't working even though it was supposedly fixed properly and it happened in the logic on even attempts because the secret is converted into a string, so when it checks in the comparison function it would fail.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
I would run the streamlit on a terminal so it refreshes and then check the bug which would be the attempts being even it would break the hint, so I would make sure that the new game would have an even number amount of attempts to see if the hint functionaility worked.
- Describe at least one test you ran (manual or using pytest)  
I would manually keep checking every attempt but will ask the chatbot in the future.
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?
No, most of these tests were really common sense and not very complex to solve.
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
That every interaction in the script will rerun from top to bottom without needing to go to the terminal and refreshing for new changes. Session state's pretty much saves these interactions and remember what you did across different runs.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
Using comments after every bug fix. I would ask the AI chat agent what the program is doing and comparing it to what the assignment does and see if there's any bugs. It changed in the sense that most AI generated code needs tweaking most of the time and makes a lot of assumptions when you're vague.
