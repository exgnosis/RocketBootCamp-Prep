# Lab 1-1: Code Generation with GitHub Copilot

## Overview

This lab is the practical counterpart to the module on writing specifications for AI-assisted development. The module argued that the quality of code an AI assistant produces is determined almost entirely by the quality of the specification you give it. This lab is where that argument becomes concrete.

You will give the same fundamental request, "build me a Flask Hello World application," to GitHub Copilot **five times in a row**, adding one layer of specification each time: first a vague one-liner, then a clear problem statement, then explicit error handling, then security requirements, then coding standards. Each round you will compare the code Copilot produces against the previous round. The point of the comparison is not which round is "best"; the point is that each round's output differs from the previous one in ways you can trace back to specific words you added to the prompt. By the end of Part 5 you will have a small but real production-quality Flask application, generated entirely by Copilot, that you can read line by line and confirm matches what you specified.

Parts 6 and 7 then change one dimension of the prompt rather than adding more requirements. Both parts hold the underlying application constant but reframe the role Copilot is acting in: a QA engineer in Part 6, a DevOps engineer in Part 7. You will see that the role label, plus the same Hello World code as input, drives Copilot to produce entirely different artifacts (a test suite, a Dockerfile) without you having to spell out what those artifacts look like in detail.

The lab is therefore part **prompting exercise** (write each prompt carefully, save each output) and part **reading exercise** (compare the outputs and trace each new piece of code back to the specification line that requested it). When you are done, you will have direct, side-by-side evidence of how prompt quality affects code quality.

**This lab is hands-on.** You write the prompts yourself; reading the outputs critically is the skill being practiced.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Recognize the symptoms of an underspecified prompt by reading the code it produces.
2. Convert a one-line request into a structured engineering specification that names problem, error handling, security, and coding standards.
3. Predict which omissions in a prompt will lead to which omissions in the generated code.
4. Use role-based framing in a prompt (act as a QA engineer, act as a DevOps engineer) to redirect Copilot to a different deliverable while holding the input code constant.
5. Use file attachment in Copilot Chat to supply existing source as context, rather than pasting it inline.
6. Compare two pieces of generated code and articulate which prompt changes are responsible for the differences.

---

## Part 1: Set Up the Workspace

### Step 1.1: Create the lab folder in VS Code

1. Open VS Code.
2. From the menu, choose **File > Open Folder**.
3. Create a new folder called `prompt-lab` in your usual workspace location, then open it.
4. When VS Code asks whether you trust the authors of the files in this folder, click **Yes, I trust the authors**.

You should now see an empty Explorer panel on the left with `PROMPT-LAB` at the top.

### Step 1.2: Confirm Copilot is configured for this lab

1. Open the Chat view with `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Alt+I` (macOS).
2. In the chat mode dropdown at the bottom of the chat panel, select **Ask**. You will stay in Ask mode for the entire lab. Do not switch to Edit or Agent mode at any point.
3. In the model picker, select **Claude Sonnet 4.6**.

If Claude Sonnet 4.6 is not available in your model picker, two situations are possible:

- You are on the free Copilot Student tier, where premium models are reached through "Auto" mode. Selecting **Auto** is acceptable for this lab, although the responses may differ slightly from what is described below.
- You are on a Business or Enterprise plan and your organization administrator has not enabled Claude Sonnet 4.6 in the Copilot policy settings. In that case, ask your administrator to enable it, or use **Auto** in the meantime.

### Step 1.3: Create a lab notebook

Create a file called `notebook.md` in the workspace. You will record observations as you go through each part. Start it with:

```markdown
# Prompt Lab Notebook

## Part 1: Unstructured prompt

## Part 2: Clear problem statement

## Part 3: Error handling requirements

## Part 4: Security requirements

## Part 5: Coding standards

## Part 6: Role switch to QA engineer

## Part 7: Role switch to DevOps engineer

## Part 8: Reflection
```

Save it.

### Step 1.4: Understand the workflow you will repeat

For Parts 1 through 5, you will repeat this loop:

1. In Copilot Chat, click the **+ icon** (New Chat) at the top of the chat panel to start a fresh conversation. **Do this every time.** A new chat ensures Copilot does not retain context from the previous prompt, which would defeat the comparison.
2. Paste the prompt for the current part exactly as shown.
3. Send the prompt and read the response.
4. Save the response (or the salient portion of it) to a file named `output-partN.md` in the workspace, where N is the part number.
5. Write two or three sentences in your notebook about what the response did and did not include.

The "save the response" step is what makes the lab work. Without saved outputs you cannot do the comparison in Part 8. To save:

1. Click anywhere in the chat response.
2. Press `Ctrl+A` to select all of the response text, then `Ctrl+C` to copy.
3. In the Explorer panel, create a new file `output-part1.md` (and so on for each part).
4. Paste and save.

---

## Part 2: An Unstructured Prompt

Open a new chat (`+` icon) and send this prompt exactly as shown:

```
Write a simple Python Flask hello world application.
```

That is the entire prompt. No version, no error handling, no security, no standards. Look at what Copilot produces and answer in your notebook:

1. Does the response specify a Python version?
2. Does it include error handling?
3. Does it mention security at all?
4. Does it follow PEP 8 (style) or PEP 257 (docstrings)?
5. Does it pin dependency versions, or give a `requirements.txt`?
6. Does it include any kind of input validation?
7. Is `debug=True` set? (This is a real production security risk; check carefully.)

Save the response as `output-part1.md`.

> **What you should observe.** Copilot will produce working code; that is not the issue. The issue is what the working code does and does not do. Most responses to this prompt produce a one-file Flask app with `debug=True`, no error handlers, no logging, no version pinning, and no type hints. A model cannot implement requirements you did not specify; that is the entire lesson of this lab. The model is not being lazy or wrong; it is doing exactly what was asked.

---

## Part 3: Add a Clear Problem Statement

Open a new chat and send this prompt:

```
Create a minimal but production-quality Python 3.11 Flask web application
that exposes a single HTTP GET endpoint at the root path ("/") and
returns the text "Hello, World!".
```

Compare this response to the Part 2 response. What changed? Look specifically for:

1. Is the Python version now specified in any comment, header, or `requirements.txt`?
2. Is the endpoint actually restricted to GET? (Look for `methods=["GET"]` or equivalent.)
3. Is "production-quality" reflected anywhere in the code, or only as a wish in the prompt?

Save the response as `output-part2.md` and write two or three sentences in your notebook about which improvements appeared and which did not.

> **What you should observe.** "Production-quality" by itself is too vague to drive code changes; the model will read it as flavoring rather than a requirement. The improvements that do appear come from the parts of the prompt that are precise (the Python version, the path, the method, the literal return string). This is the cleanest demonstration in the lab of why every requirement must be both stated and stated specifically. "Make it secure" and "make it production-quality" will be largely ignored; "disable debug mode" and "log errors with the logging module" will be acted on.

---

## Part 4: Add Error Handling Requirements

Open a new chat and send this prompt:

```
Create a minimal but production-quality Python 3.11 Flask web application
that exposes a single HTTP GET endpoint at the root path ("/") and
returns the text "Hello, World!".

The application must:

- Return HTTP 405 for unsupported HTTP methods.
- Return HTTP 404 for unknown routes.
- Include a global error handler for unhandled exceptions.
- Avoid exposing stack traces to the client.
- Log errors using Python's logging module.
```

Compare the response to Part 3. Specifically:

1. Are there now `@app.errorhandler(404)` and `@app.errorhandler(405)` decorators (or equivalent)?
2. Is there a generic error handler for `Exception` or `500`?
3. Is `logging` actually imported and configured, or only mentioned?
4. What does the 500 handler return to the client? Confirm it does not leak the exception's `repr` or traceback.

Save as `output-part3.md`. Write a few sentences in your notebook.

> **What you should observe.** Each bullet in the requirements list typically maps to one or two lines of generated code, in the order you wrote the bullets. This is a useful property: bullet-by-bullet specification gives bullet-by-bullet traceability in the output. If you cannot find code corresponding to a specific bullet, the requirement was missed and you can ask Copilot a follow-up to add it.

---

## Part 5: Add Security Requirements

Open a new chat and send this prompt:

```
Create a minimal but production-quality Python 3.11 Flask web application
that exposes a single HTTP GET endpoint at the root path ("/") and
returns the text "Hello, World!".

The application must:

- Return HTTP 405 for unsupported HTTP methods.
- Return HTTP 404 for unknown routes.
- Include a global error handler for unhandled exceptions.
- Avoid exposing stack traces to the client.
- Log errors using Python's logging module.

Security Requirements:

- Disable Flask debug mode.
- Do not expose internal exception details.
- Use environment variables for configuration.
- Follow OWASP secure coding principles where applicable.
- Ensure no hardcoded secrets are present.
- Validate and sanitize all external input (even if not currently used).
```

Compare to Part 4. Look for:

1. Is `debug=False` explicit, or is `debug` left to default? (Flask's default is `False`, but for a teaching example, an explicit `debug=False` documents the intent.)
2. Are configuration values pulled from `os.environ` or `os.getenv`?
3. Is there at least a placeholder for input validation, given that the application has no current inputs to validate?
4. Did "OWASP secure coding principles" cause Copilot to add specific things, like security headers via `flask-talisman`, or to merely reference OWASP in a comment?

Save as `output-part4.md`. Note that bullets that name a specific control (disable debug mode, use environment variables) produce code; bullets that name a framework or philosophy (OWASP, "where applicable") tend to produce comments or general mentions. This is a known pattern.

---

## Part 6: Add Coding Standards

Open a new chat and send this prompt:

```
Create a minimal but production-quality Python 3.11 Flask web application
that exposes a single HTTP GET endpoint at the root path ("/") and
returns the text "Hello, World!".

The application must:

- Return HTTP 405 for unsupported HTTP methods.
- Return HTTP 404 for unknown routes.
- Include a global error handler for unhandled exceptions.
- Avoid exposing stack traces to the client.
- Log errors using Python's logging module.

Security Requirements:

- Disable Flask debug mode.
- Do not expose internal exception details.
- Use environment variables for configuration.
- Follow OWASP secure coding principles where applicable.
- Ensure no hardcoded secrets are present.
- Validate and sanitize all external input (even if not currently used).

Coding Standards:

- Follow PEP 8 style guidelines.
- Follow PEP 257 for docstrings.
- Include type hints (PEP 484).
- Organize code using functions and a main guard:
    if __name__ == "__main__":
- Include a requirements.txt file.
- Include comments explaining key sections.
```

Compare to Part 5. Specifically look for:

1. Are there type hints on function signatures (`-> Response`, `name: str`, etc.)?
2. Are there docstrings on the module and each function, formatted in a recognizable PEP 257 style?
3. Is there an `if __name__ == "__main__":` guard?
4. Is a `requirements.txt` actually included as a separate code block in the response?
5. Are there inline comments explaining what each section does?

Save the response as `output-part5.md`. **This is the final, target-quality version of the application.** Save the Python source code from this response (just the code, not the surrounding markdown explanation) to a file called `Hello.py` in your workspace folder. This file becomes the input for Parts 7 and 8.

> **What you should observe.** This response should look substantially more like production Python than the response from Part 2. Type hints, docstrings, named functions, structured logging configuration. The code is now traceable to specific bullets in the spec. If you read the source one line at a time, almost every line corresponds to something you asked for. This is the property the module called "verifiability": each requirement is testable against the resulting code.

---

## Part 7: Switch the Role to QA Engineer

For this part you will hold the underlying application constant (the `Hello.py` file you saved at the end of Part 5) and change only the role label and the deliverable type. The goal is to see how role-based framing redirects Copilot to a different output without you having to spell out the deliverable's format in detail.

### Step 7.1: Attach the file

Open a new chat. Click the **paperclip icon** in the chat input area (or type `#` and select from the file picker), and attach `Hello.py`. The chat input field should now show `Hello.py` as an attached context item.

Attaching a file is the Copilot equivalent of the original lab's `with open("Hello.py") as f: flask_code = f.read()` plus an f-string interpolation. It is the canonical, clean way to give Copilot existing code as input. Do not paste the code into the prompt itself; that will work, but it is wasteful and harder to read.

### Step 7.2: Send the QA prompt

With `Hello.py` attached, send this prompt:

```
You are a senior QA automation engineer.

Analyze the attached Python Flask application and generate a
comprehensive set of test cases.

Requirements:

1. Provide functional test cases.
2. Provide negative test cases.
3. Provide security-related test cases.
4. Provide edge case scenarios.
5. Identify any potential failure points.
6. Provide pytest-based automated test examples.
7. Explain the reasoning behind each test.

Follow best practices for testing Flask applications.
Assume Python 3.11 and pytest.
```

Save the response as `output-part6.md`.

> **What you should observe.** The role label "senior QA automation engineer" is the single most influential phrase in this prompt. The same code, the same numbered requirements, but with a different role label ("write code that does X" vs. "review code that does X") would produce a different output. The role label tells Copilot what kind of artifact you want. The numbered requirements tell Copilot what that artifact must contain.
>
> Look specifically for:
> - Are the test cases organized by category (functional, negative, security, edge)?
> - Is each test case explained with a "why" comment or section?
> - Are the pytest examples actually runnable, or just sketches?
> - Did Copilot identify failure points the application could plausibly hit (like the global error handler not catching a specific exception type)?
>
> This is the practical demonstration of the module's claim that AI specifications work the same way for humans and for AI assistants: a QA engineer given the same brief would produce the same kind of artifact.

---

## Part 8: Switch the Role to DevOps Engineer

### Step 8.1: Open a new chat and attach `Hello.py`

Open a new chat. Attach `Hello.py` the same way as in Part 7. Confirm the attachment is present before you send the prompt.

### Step 8.2: Send the DevOps prompt

```
You are a senior DevOps engineer specializing in containerization.

Analyze the attached Flask application and generate a production-ready
Dockerfile.

Requirements:

1. Use Python 3.11.
2. Use a minimal base image (prefer slim or alpine).
3. Do not run the container as root.
4. Use best practices for Docker layering.
5. Install dependencies from requirements.txt.
6. Disable debug mode.
7. Expose the correct port.
8. Use a production-ready WSGI server (e.g., gunicorn).
9. Minimize image size.
10. Follow Docker security best practices.

Provide:
- The complete Dockerfile
- An explanation of each section
- Any recommended improvements to the Flask app for containerization
```

Save the response as `output-part7.md`.

> **What you should observe.** Same attached code, different role, completely different output: a `Dockerfile`, not a `.py` file. None of the numbered requirements names the keyword "Dockerfile"; the role label and the phrase "Analyze the attached Flask application and generate a production-ready Dockerfile" carry that information. Once again the role is the most influential phrase in the prompt.
>
> Look specifically for:
> - Did Copilot use multi-stage builds, slim/alpine, or both?
> - Does the Dockerfile create a non-root user explicitly with `USER` and `RUN useradd` (or similar), or does it silently default to root?
> - Is gunicorn included in the recommended `requirements.txt` changes, or was the existing `requirements.txt` left alone?
> - Did Copilot suggest improvements to `Hello.py` itself, such as binding to `0.0.0.0` rather than `127.0.0.1`?
>
> The third item ("recommended improvements to the Flask app") is interesting. A real DevOps engineer reviewing a containerized Flask app would notice things the Flask author may not have considered. Copilot's reasonableness on this last point is a good informal test of how well it has internalized the role.

---

## Part 9: Compare and Reflect

You now have seven response files (`output-part1.md` through `output-part7.md`) plus the source code `Hello.py`. The comparison is the lesson.

### Step 9.1: Side-by-side compare consecutive parts

Use VS Code's **Compare Selected** feature to view consecutive part outputs side by side:

1. In the Explorer, click `output-part1.md` to select it.
2. `Ctrl+click` (Windows/Linux) or `Cmd+click` (macOS) on `output-part2.md` so both files are selected.
3. Right-click either file and choose **Compare Selected**.
4. A side-by-side diff opens in the editor.

Do this for each consecutive pair (1 vs 2, 2 vs 3, 3 vs 4, 4 vs 5). You are not looking for textual diff in the usual code-review sense; you are looking at *which features appeared* in each new response that were not in the previous one, and *which requirements bullets caused them*.

For each pair, write one to three sentences in your notebook answering:

- Which lines or sections in the new file did not exist in the older one?
- Which bullet in the new prompt caused each new section?
- Were there any bullets in the new prompt that did NOT produce visible new code? If so, why might that be? (The module's discussion of "vague verbs" and "philosophy bullets" is the hint.)

### Step 9.2: Compare Parts 6 and 7 to each other

Parts 6 and 7 attached the same code and used very similar prompt structure, but produced completely different artifacts. Open `output-part6.md` and `output-part7.md` side by side (`Compare Selected`). Then in your notebook:

1. List the three most influential differences in the two prompts (excluding the role label).
2. Estimate, in your judgment, how much of the difference in output is attributable to the role label vs. how much to the numbered requirements.
3. Could you have produced the same Dockerfile by asking the QA prompt with "DevOps engineer" substituted in but no other changes? Why or why not?

### Step 9.3: Reflection questions

Answer in your notebook. These are open-ended; spend at least ten minutes.

1. **Cost of vagueness.** In Part 1 the prompt was nine words. The total code generated, summed across all five parts, is several hundred lines. If you had started with the Part 5 prompt directly, how much of that intermediate code would never have been generated? What does that say about the practical cost of starting from a vague prompt?

2. **The bullets that did not work.** Looking at Parts 4 and 5, identify at least one bullet whose effect on the generated code is hard to see. Common candidates: "Follow OWASP secure coding principles where applicable", "Ensure no hardcoded secrets are present", "Validate and sanitize all external input (even if not currently used)". For each one you identify, propose a more specific replacement that would produce visible code.

3. **The role label as a lever.** Parts 6 and 7 hold the underlying code constant and change the role. What other roles could you frame the same Hello.py for, and what would each produce? Possibilities: "performance engineer", "accessibility auditor", "technical writer", "security researcher". Pick one and predict the deliverable; if you have time, run a chat and see if your prediction was right.

4. **What this lab is not testing.** This lab measures prompt quality by reading the output, not by running it. The Flask app from Part 5 may or may not actually start. The tests from Part 6 may or may not actually pass. The Dockerfile from Part 7 may or may not actually build. Spell out why running the code would still be a meaningful next step, even though it is outside the scope of this lab.

5. **Specification as a transferable skill.** Compare the prompts you wrote in Parts 5, 6, and 7 to the structure recommended in the module ("anatomy of a good Copilot spec": goal, scope, interfaces, constraints, acceptance). For each prompt, which of these elements were present? Which were missing? Would adding the missing ones improve the output, or would they be redundant?

6. **The next iteration.** Suppose your next task is to add a new endpoint, `GET /healthz`, that returns `{"status": "ok"}` as JSON. Write the prompt you would now use, based on what you have learned in this lab. Predict, before sending it, what Copilot will produce, then send it and compare.

---

## Reference: Why Each Section of the Prompt Matters

A summary of which parts of the prompt drive which behavior, based on the comparisons you just did.

| Prompt element | Effect on generated code |
|----------------|--------------------------|
| Language and version | Determines syntax, available standard library, dependency versions |
| Framework name and version | Determines API surface, idiomatic patterns, expected file layout |
| Endpoint path and method | Determines routing decorators and method restrictions |
| Bulleted error-handling rules | Each bullet typically produces one or two lines of code |
| Bulleted security controls (specific) | Each specific bullet (disable debug, use env vars) produces code |
| Bulleted security philosophy (vague) | "Follow OWASP" alone usually produces only a comment or reference |
| Bulleted coding standards (PEP 8, PEP 257, PEP 484) | Drives style, docstring presence, type hints |
| Required artifacts (`requirements.txt`, main guard) | Drives multiple files or sections in the response |
| Role label ("You are a senior X engineer") | Determines the type of deliverable (code, tests, Dockerfile, review) |
| Attached file via `#` or paperclip | Provides existing context without inflating the prompt |

The first eight rows govern Parts 2 through 6. The last two govern Parts 7 and 8.

---

## Reference: The Most Important Habit

The habit this lab is training is: **open a new chat for each prompt, and save the output before you change anything**. Without these two disciplines, the comparison in Part 9 cannot be done, and the lab's lessons disappear into a single noisy stream of chat history.

In real work, the same habits apply at lower frequency. When you are trying to debug an inconsistent response from Copilot, the first questions are: "Did I start a new chat?" and "Do I have the previous good response saved somewhere?" Without those, every comparison is forensic guesswork.

---

## Reference: Useful Chat-View Shortcuts in VS Code

| Action | Shortcut or location |
|--------|----------------------|
| Open the Chat view | `Ctrl+Alt+I` (Windows/Linux), `Cmd+Alt+I` (macOS) |
| Start a new chat | `+` icon at the top of the Chat panel |
| Attach a file as context | Paperclip icon in the chat input, or type `#` and pick |
| Switch chat mode | Dropdown at the bottom of the chat input (Ask / Edit / Agent) |
| Switch model | Model picker at the bottom of the chat input |
| Copy the response | Click the response, `Ctrl+A`, `Ctrl+C` |
| Compare two files | Select two files in Explorer (`Ctrl+click`), right-click, **Compare Selected** |

---

## Troubleshooting

**Claude Sonnet 4.6 is not in the model picker.**
Your plan or your organization's policy may not include it. On a free Student plan, premium models are only reachable via **Auto** mode. On a Business or Enterprise plan, the administrator must explicitly enable Claude Sonnet 4.6 in the Copilot policy settings. Switch to **Auto** as a fallback; responses will differ slightly but the lesson is the same.

**The response from Part 1 already includes error handling.**
Copilot's training data sometimes pushes it toward better defaults than the prompt requires. This does not break the lab; it just means that one comparison (Part 1 to Part 2) is narrower. The point of the lab is the trend across all five prompts, not the magnitude of any single jump.

**The same prompt produces noticeably different output two days in a row.**
LLMs are stochastic and the underlying model may have been updated between sessions. The lab does not require byte-identical output; it requires that the *features* in the output track the *requirements* in the prompt. If they do, the comparison works regardless of stylistic variation.

**Part 7 or Part 8 produced advice that contradicts Part 6.**
The "recommended improvements to the Flask app" section in Part 8 can suggest changes that would invalidate Part 6's tests. This is realistic; a real QA engineer and a real DevOps engineer often disagree about the same code. Notice the disagreement in your notebook; it is itself an interesting observation about how role framing biases the response.

**`Hello.py` does not appear in the Part 6 or Part 7 attachment dropdown.**
You may not have saved the file to the workspace folder, or the workspace folder may not be open in VS Code. Confirm the file is in the same folder as `notebook.md` and that VS Code's Explorer panel shows it.

**Copilot's response in Part 5 says the requirements were "added" but actually omits the requirements.txt file.**
This is common; Copilot sometimes lists what it intends to provide without providing it. Read the response carefully and, if the `requirements.txt` block is missing, send a follow-up: "You said you would include a requirements.txt but it is not in the response. Please include it." Save the corrected response, not the original.

**Copilot suggests `flask-talisman` or another OWASP-related dependency that you did not ask for.**
This is acceptable. Copilot may interpret "OWASP secure coding principles" as license to add hardening dependencies. Note in your notebook which dependencies it added without your asking, and whether you would accept them in a real code review.

---

## Further Reading

- **GitHub Copilot Chat documentation** at <https://docs.github.com/copilot/how-tos/use-chat>. The canonical reference for all the Copilot Chat features used in this lab.
- **GitHub Copilot model picker** at <https://docs.github.com/copilot/about-github-copilot/choosing-the-right-ai-model-for-your-task>. Background on the available models and how to choose between them.
- **"Spec-driven development: Using Markdown as a programming language when building with AI"** (GitHub Blog, 2025) at <https://github.blog/ai-and-ml/generative-ai/spec-driven-development-using-markdown-as-a-programming-language-when-building-with-ai/>. A deeper treatment of the workflow this lab introduces in miniature.
- **Awesome GitHub Copilot Customizations** at <https://github.com/github/awesome-copilot>. The repository of community-contributed prompts and instructions. The QA-engineer and DevOps-engineer prompts in this lab are simplified versions of patterns from this repo.
- **OWASP Top 10** at <https://owasp.org/Top10/>. For the security requirements section, the canonical reference if you want to write more specific bullets than "follow OWASP".
- **PEP 8, PEP 257, PEP 484** at <https://peps.python.org>. The Python style guide, docstring conventions, and type-hint specification respectively. The "Coding Standards" bullets in Part 6 reference all three.
