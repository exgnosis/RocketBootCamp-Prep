# Lab 6-1: Introduction to GitHub Copilot
### Using Claude Sonnet 4.6 in VSCode

## Overview

**_Note: Depending on the setup that has been provided to you, the GitHub Copilot extension may already be installed and authenticated. If you already see the Copilot icon in the VS Code Activity Bar and Status Bar, you can skip to Part 3._**

In this lab, you will install the GitHub Copilot extension in VS Code on Ubuntu Linux, select **Claude Sonnet 4.6** as the active model from Copilot's model picker, and exercise the three chat modes (Ask, Agent, Plan). By the end you will have a working AI pair-programmer that can read your project, propose changes as inline diffs, and run commands with your approval.

**Estimated time:** 30 to 45 minutes
**Difficulty:** Beginner

**Prerequisites:**

- A paid GitHub Copilot plan (Pro, Pro+, Business, or Enterprise). Claude is not available on Copilot Free, and as of March 2026 Copilot Student offers Claude only through Auto mode.
- If you are on a Business or Enterprise plan, your administrator must have enabled the **Anthropic Claude** policy in your organization's Copilot settings on github.com.
- VS Code installed (version 1.99 or later recommended).
- A GitHub account signed in to VS Code.

---

## Learning Objectives

By the end of this lab, you will be able to:

1. Install the GitHub Copilot and GitHub Copilot Chat extensions in VS Code on Ubuntu.
2. Authenticate Copilot against your GitHub account.
3. Select **Claude Sonnet 4.6** as the active model from the model picker.
4. Configure a project with a `.github/copilot-instructions.md` file to provide standing context.
5. Use the three chat modes (Ask, Agent, Plan) appropriately, including the Keep / Undo review flow.
6. Issue prompts that reference specific files and line ranges using `#file` and inline chat.

---

## Part 1: Install the GitHub Copilot Extensions

### Step 1.1: Open VS Code

Press the Super key (Windows key) and search for **Visual Studio Code**, or run `code` from a terminal.

### Step 1.2: Open the Extensions view

Press `Ctrl+Shift+X` to open the Extensions panel.

### Step 1.3: Install GitHub Copilot

In the search box, type:

```
GitHub Copilot
```

You should see two extensions published by **GitHub** (verified publisher):

- **GitHub Copilot** (the inline-suggestions engine)
- **GitHub Copilot Chat** (the chat and agent surface)

Click **Install** on **GitHub Copilot**. The Chat extension installs automatically as a dependency. If it does not, install it manually as well.

> If the extension fails to install, confirm your workspace is not in **Restricted Mode**. Open the Command Palette (`Ctrl+Shift+P`) and run "Workspaces: Manage Workspace Trust" to set the workspace to trusted.

### Step 1.4: Sign in to GitHub

After installation, look at the Status Bar at the bottom of VS Code. You will see a Copilot icon with a "Sign in" prompt, or a notification will appear at the top of the window.

Click **Sign in to GitHub**. A browser window opens. Authorize VS Code against your GitHub account, then return to VS Code. The Status Bar icon should now show the Copilot logo without a strikethrough.

### Step 1.5: Verify Copilot is active

Open the Command Palette (`Ctrl+Shift+P`) and run:

```
GitHub Copilot: Status
```

You should see a status panel reporting that Copilot is enabled and signed in. If it reports an issue, run **Developer: Reload Window** from the Command Palette and try again.

---

## Part 2: Select the Claude Sonnet Model

### Step 2.1: Open Copilot Chat

Press `Ctrl+Alt+I` to open the **Chat view**. The chat panel appears on the side of the VS Code window with a prompt input box at the bottom.

### Step 2.2: Find the model picker

At the bottom of the chat input box, you will see a **model picker** (a dropdown showing the current model name, typically something like "GPT-5" or "Auto" on a fresh install).

### Step 2.3: Select Claude Sonnet 4.6

Click the model picker. On a current Copilot Chat extension, Claude Sonnet 4.6 should be visible directly in the list alongside Auto and GPT-5.x. Select **Claude Sonnet 4.6**.

If Claude Sonnet 4.6 is not visible directly, look for an entry labelled **Other models...** at the bottom of the picker. Click it to expand the full list of available Claude variants (Haiku 4.5, Sonnet 4, Sonnet 4.5, Sonnet 4.6) and pick Sonnet 4.6 from there.

The picker label updates to show the current model. The next time you open the chat, this selection is remembered.

> **Premium request multiplier:** Claude Sonnet 4.6 uses a 1x premium-request multiplier, meaning each chat turn counts as one premium request against your monthly Copilot Pro allowance. For reference, Claude Haiku 4.5 is 0.33x (lighter and cheaper, good for quick questions) and GPT-5.5 is currently offered at a promotional 7.5x. The picker shows the multiplier next to each model name.

> **Why Sonnet rather than Opus?** As of this writing, the GitHub Copilot in-IDE chat picker for Copilot Pro exposes Claude Haiku 4.5 and the Sonnet 4.x line, but not Claude Opus. Claude Opus is available through the **cloud-based Claude coding agent** on github.com (Agents tab), which is a different workflow built around pull requests rather than in-editor edits. Sonnet 4.6 is Anthropic's current flagship coding model and is what most professional developers use day-to-day in Copilot.

> **Note about the "Manage Models..." entry:** If you see a "Manage Models..." option at the bottom of the picker, clicking it opens a provider list. The Anthropic Claude models offered through your Copilot subscription appear under the **Copilot** provider entry, not the "Anthropic" entry. The "Anthropic" entry is for Bring Your Own Key (BYOK) scenarios using a separate Anthropic API key.

**Checkpoint:** The chat panel is open, the model picker reads **Claude Sonnet 4.6**, and the Status Bar shows the Copilot icon as active.

<img src="images/Setup1.png"/>
---

## Part 3: Configure a Test Project

### Step 3.1: Create a project directory

Open a terminal in VS Code (`` Ctrl+` ``) and run:

```bash
mkdir ~/copilot-lab
cd ~/copilot-lab
code .
```

This opens the empty directory in VS Code as a new workspace.

When prompted, click **Yes, I trust the authors** so Copilot can operate fully.

### Step 3.2: Create a simple starter file

Inside VS Code, create a new file called `calculator.py` with the following content:

```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b
```

Save the file (`Ctrl+S`).

### Step 3.3: Generate a `copilot-instructions.md` file

The `.github/copilot-instructions.md` file is Copilot's equivalent of a project-level system prompt. Copilot reads it on every request inside this workspace.

Open the Chat view (`Ctrl+Alt+I`). In the prompt box, type:

```
/init
```

Press Enter. Copilot Chat will analyse the workspace and propose a `.github/copilot-instructions.md` file with project conventions, build commands, and architectural notes.

> If `/init` is not available in your version of the Chat extension, ask Copilot directly: "Create a `.github/copilot-instructions.md` file for this project that documents conventions and any project commands." Then click **Keep** to write the file to disk.

Review the proposed content. Because this project is very small, the file will mostly be a skeleton. That is fine. Click **Keep** to accept it.

Open the file at `.github/copilot-instructions.md` and add the following two lines at the top of the file (or fold them into the existing sections):

```
- Follow PEP 8 and PEP 257 conventions for all Python code.
- All public functions must have docstrings and explicit error handling for invalid inputs.
```

Save the file.

> **What is `copilot-instructions.md`?** It is a plain Markdown file Copilot reads at the start of every request in this workspace. Use it to record build commands, coding conventions, and architectural decisions so you do not have to re-explain them every time.
>
> Recall from the slides that one of the key principles of prompt engineering is to "provide context". `copilot-instructions.md` is the canonical tool for providing persistent context to Copilot across sessions, and it lives in version control alongside your code so the whole team benefits.
>
> **Note for teams migrating from Claude Code:** Copilot CLI will also read a `CLAUDE.md` file at the repository root as primary instructions, so existing `CLAUDE.md` work is not wasted. Inside the VS Code Copilot extension, however, the canonical file is `.github/copilot-instructions.md`.

---

## Part 4: Hands-On Exercises

Copilot Chat has three modes, selectable from the dropdown at the bottom-left of the chat input box:

- **Ask**: Copilot answers questions and explains code but does not modify files.
- **Agent**: Copilot operates autonomously. It reads files, proposes edits with inline diffs (Keep / Undo per chunk), and may run terminal commands. Each tool invocation (file edit, command execution) requires your approval the first time.
- **Plan**: Copilot drafts a written plan in Markdown describing exactly what it intends to do before doing anything. You review and edit the plan, then approve it. Copilot then executes the plan, typically by switching to Agent-mode behaviour.

### Exercise 4.1: Generate code (Agent mode)

Switch the chat mode dropdown to **Agent**.

Make sure `calculator.py` is open in the editor (the active file is part of Copilot's automatic context).

In the prompt box, type:

```
Add docstrings to every function in calculator.py following PEP 257 conventions.
Also add a guard against division by zero in divide().
```

Press Enter. The refactored code should look like this:

```python
def add(a, b):
    """Return the sum of a and b."""
    return a + b

def subtract(a, b):
    """Return the difference of a and b (a - b)."""
    return a - b

def multiply(a, b):
    """Return the product of a and b."""
    return a * b

def divide(a, b):
    """Return the quotient of a and b (a / b).

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**Observe:**

- Copilot reads `calculator.py` automatically because it is the active file.
- An inline diff appears in the editor showing the proposed changes.
- Each change has **Keep** and **Undo** buttons. You can act on individual chunks or use the bar at the top of the file to Keep All or Undo All.
- The chat panel summarises the changed files at the top of the response.

Click **Keep** (or Keep All) to apply the changes.

**Discussion question:** What does the inline diff show, and how does this differ from an autocomplete-style assistant that just inserts text at the cursor?

### Exercise 4.2: Use file references

Copilot uses `#` for explicit context references (the equivalent of `@filename` in Claude Code).

Stay in **Agent** mode. In the prompt box, type `#` and select `calculator.py` from the dropdown that appears. Then continue the prompt:

```
#calculator.py Write a pytest test suite for these functions in a new file called test_calculator.py. Include edge cases.
```

Press Enter.

**Observe:** Copilot proposes a new file `test_calculator.py`. The diff for the new file appears in the editor. Approve the file creation, then click **Keep** to write it to disk.

The resulting `test_calculator.py` should look approximately like this (output may vary slightly between runs because LLMs are non-deterministic):

```python
import pytest

from calculator import add, subtract, multiply, divide


class TestAdd:
    def test_positive(self):
        assert add(2, 3) == 5

    def test_negative(self):
        assert add(-2, -3) == -5

    def test_mixed_signs(self):
        assert add(-5, 3) == -2

    def test_zero(self):
        assert add(0, 0) == 0
        assert add(7, 0) == 7

    def test_floats(self):
        assert add(0.1, 0.2) == pytest.approx(0.3)


class TestSubtract:
    def test_positive(self):
        assert subtract(5, 3) == 2

    def test_negative_result(self):
        assert subtract(3, 5) == -2

    def test_zero(self):
        assert subtract(7, 7) == 0
        assert subtract(7, 0) == 7

    def test_double_negative(self):
        assert subtract(-5, -3) == -2

    def test_floats(self):
        assert subtract(1.0, 0.1) == pytest.approx(0.9)


class TestMultiply:
    def test_positive(self):
        assert multiply(3, 4) == 12

    def test_by_zero(self):
        assert multiply(0, 99) == 0
        assert multiply(99, 0) == 0

    def test_by_one(self):
        assert multiply(1, 42) == 42

    def test_negative(self):
        assert multiply(-3, 4) == -12
        assert multiply(-3, -4) == 12

    def test_floats(self):
        assert multiply(2.5, 4) == 10.0


class TestDivide:
    def test_positive(self):
        assert divide(10, 2) == 5

    def test_negative(self):
        assert divide(-10, 2) == -5
        assert divide(-10, -2) == 5

    def test_zero_numerator(self):
        assert divide(0, 5) == 0

    def test_float_result(self):
        assert divide(1, 4) == 0.25

    def test_divide_by_zero_raises(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_divide_by_zero_with_zero_numerator(self):
        with pytest.raises(ValueError):
            divide(0, 0)
```

### Exercise 4.3: Reference a specific line range with inline chat

Open `calculator.py` and select the lines containing the `divide` function. With the lines highlighted, press `Ctrl+I` to open **inline chat** directly in the editor at the selection.

This is the Copilot equivalent of "ask about this specific range" without sending the whole file as context. The selection is automatically attached.

Type the question:

```
Explain the division-by-zero guard you added and suggest an alternative approach.
```

Press Enter. Copilot responds in an overlay anchored to the selection.

Notice how Copilot can read the specific lines you referenced and frame its answer around them, without re-analysing the entire file. You can dismiss the inline chat with `Esc`, or use it to apply a follow-up edit inline.

> **Tip:** You can also press `Ctrl+I` without a selection to open inline chat at the cursor position, and pass explicit references such as `#file:calculator.py` or `#selection` in the prompt.

### Exercise 4.4: Multi-file refactor with Agent mode

The previous exercises used Agent mode for single-file changes. This exercise shows Agent mode handling a multi-step task that touches multiple files and runs commands.

You should already be in **Agent** mode. Issue this prompt:

```
Refactor calculator.py to use a Calculator class instead of standalone functions.
Preserve all existing behaviour. Update test_calculator.py to match.
Then run the tests with pytest and confirm they pass.
```

Press Enter.

**Observe:** Instead of immediately producing one diff, Copilot:

1. Reads `calculator.py` and `test_calculator.py`.
2. Outlines its approach at the top of the chat response.
3. Edits both files, showing diffs as it goes.
4. Asks for permission the first time it wants to run a terminal command (`pytest` or `pip install pytest`). Click **Allow** for this session.
5. Runs the command, reads the output, and reports back. If tests fail, Copilot iterates and fixes.

Each file edit still uses the **Keep / Undo** flow. You can intervene at any point by clicking **Stop** in the chat panel.

> **Tip:** If you want Copilot to act without asking permission for each terminal command, you can pre-approve specific commands in the workspace settings (`.vscode/settings.json`) under `github.copilot.chat.agent.terminal.allowList`. Treat this with care, since it removes the safety prompt for shell execution.

**Discussion question:** What did Copilot decide to do that you did not explicitly tell it to do? How comfortable are you with that level of autonomy on production code?

### Exercise 4.5: Try Plan mode

Switch the chat mode dropdown from **Agent** to **Plan**.

In Plan mode, Copilot does not start making changes immediately. Instead, it produces a written plan in Markdown describing exactly what it intends to do. You read the plan, edit it if you want to redirect Copilot, and only then approve it. Once approved, Copilot executes the plan (typically by switching to Agent-mode behaviour).

This is the mode to reach for when:

- The task is large enough that you want to see the strategy before any code changes.
- You suspect Copilot may misinterpret the request and you want a cheap way to catch that.
- You are working on shared or production code where unreviewed edits would be risky.

Issue this prompt:

```
Add a memory feature to the Calculator class so it remembers the result of the last
operation and exposes a recall() method and a clear() method. Update the tests to cover
the new behaviour.
```

Press Enter.

**Observe:**

- Copilot opens a Markdown plan in the chat (or as a side panel, depending on extension version) describing the new methods, the state field it will add, edge cases it plans to handle, and the new tests it intends to write.
- No files have been edited yet.
- You can read, comment on, or directly edit the plan.

Review the plan. If it looks correct, approve it (the button is labelled **Run plan**, **Execute**, or similar, depending on extension version). Copilot then executes the plan and applies the changes using the Keep / Undo flow.

**Discussion question:** Compare Plan mode to going straight to Agent mode. What do you gain by reading the plan first? What do you give up?

---

## Part 5: Cleanup and Reflection

### Cleanup

Switch the chat mode back to **Ask** before ending the session. This prevents accidental edits if you keep the chat open.

To remove the lab project:

```bash
rm -rf ~/copilot-lab
```

Your Copilot credentials remain stored against your GitHub login in VS Code's credential store and do not need to be removed.

### Reflection Questions

Answer the following in your lab notebook:

1. Compare GitHub Copilot (with Claude Sonnet selected) to a standalone tool like Claude Code or Cursor. What kinds of tasks does each handle better? Consider integration with the editor, billing model, and breadth of available models.
2. Why does Copilot ask for permission before running terminal commands by default? What are the trade-offs of pre-approving commands in `settings.json`?
3. What information would you include in a `.github/copilot-instructions.md` file for a larger, multi-developer project? How does it differ from a README?
4. The `#file` syntax and inline chat (`Ctrl+I`) let you reference files and ranges explicitly. Why is this useful when working with a large codebase, even though Copilot also picks context automatically?
5. Claude Sonnet 4.6 costs 1x premium requests per turn, while Claude Haiku 4.5 costs 0.33x. For which exercises in this lab might Haiku have been sufficient? Where did Sonnet's stronger reasoning matter? When might you switch to GPT-5.x instead?

---

## Chat Modes Reference

| Mode | What it does | When to use it |
|------|--------------|----------------|
| **Ask** | Read-only. Answers questions, explains code, no file edits. | Code review, learning, exploring an unfamiliar codebase. |
| **Agent** | Autonomous loop: reads files, proposes edits with Keep / Undo, runs terminal commands, iterates on errors. | Targeted refactors, multi-file changes, scaffolding, running tests, anything where you want Copilot to act. |
| **Plan** | Drafts a written plan in Markdown first. You review and approve, then Copilot executes (typically as Agent). | Larger or higher-stakes tasks where you want to see the strategy before any code changes happen. |

**Safety note:** Pre-approving terminal commands in `settings.json` skips the safeguards that protect you from unintended shell execution. Treat the allow-list as you would a sudoers entry: minimal, explicit, and reviewed.

---

## Useful Commands and Shortcuts

| Command / Shortcut | Function |
|---------|----------|
| `Ctrl+Alt+I` | Open the Chat view |
| `Ctrl+I` | Open inline chat at the cursor (or with the current selection as context) |
| `#file:<name>` | Reference a specific file in your prompt |
| `#selection` | Reference the currently selected text |
| `#codebase` | Let Copilot search the whole workspace for relevant context |
| `/init` | Generate a `.github/copilot-instructions.md` for the current workspace |
| `/help` | List available chat slash commands |
| `/clear` | Start a fresh chat session (clears history) |
| Command Palette → "GitHub Copilot: Status" | Diagnose Copilot connection and subscription state |

---

## Troubleshooting

**Claude models do not appear in the model picker.**
First check that you are on a paid Copilot plan (Pro, Pro+, Business, or Enterprise) and signed in to VS Code with the right GitHub account. If you see a "Load Premium Models" button in the picker, click it. If Claude Sonnet 4.6 still does not appear, click **Manage Models...**, click the **Copilot** provider entry (not "Anthropic"), tick Claude Sonnet 4.6, and click OK. If you are on Copilot Business or Enterprise, your admin must have enabled the Anthropic Claude policy in github.com → Organization → Copilot Policies first. Update the GitHub Copilot Chat extension to the latest version if you have not done so recently, since the model picker UI has changed multiple times during 2025-2026.

**"Load Premium Models" button appears in the picker.**
Click it once after signing in to a paid Copilot plan. This populates the list of available models.

**Copilot icon shows a strikethrough in the Status Bar.**
You are not signed in, or your subscription is not active. Click the icon and follow the sign-in prompt. If sign-in fails, run **Developer: Reload Window** from the Command Palette.

**Chat replies are slow.**
Claude Sonnet 4.6 is a large model and individual responses can take several seconds, especially for Agent-mode tasks that involve multiple steps. For very quick questions, switch the picker to **Claude Haiku 4.5** (0.33x multiplier, much faster). Reserve Sonnet for tasks that need stronger reasoning.

**Claude Opus is not in the model picker.**
This is expected on the Copilot Pro in-IDE chat surface. As of this writing, Copilot exposes Claude Haiku 4.5 and the Sonnet 4.x line in VS Code chat, but not Opus. Claude Opus 4.6 is available through the cloud-based Claude coding agent on github.com (Agents tab), which uses a pull-request-based workflow rather than in-editor edits.

**Conflicts with other AI extensions.**
Temporarily disable other AI coding extensions (such as Cline, Continue, or the standalone Claude Code extension), because they can interfere with Copilot's keybindings and inline-chat behaviour.

**Permission prompts on every shell command interrupt your workflow.**
In your workspace `.vscode/settings.json`, add an allow-list. Example:

```json
{
  "github.copilot.chat.agent.terminal.allowList": {
    "git status": true,
    "pytest": true,
    "npm test": true
  }
}
```

**Restricted network or corporate firewall.**
Copilot routes Claude requests through GitHub's service, not directly to Anthropic. Whitelist `github.com`, `api.github.com`, `copilot-proxy.githubusercontent.com`, and `*.githubusercontent.com`. Whitelisting `api.anthropic.com` alone will not work.

---

## Further Reading

- GitHub Copilot in VS Code: <https://code.visualstudio.com/docs/copilot/overview>
- Supported AI models in GitHub Copilot: <https://docs.github.com/en/copilot/reference/ai-models/supported-models>
- Custom instructions (`copilot-instructions.md`) reference: <https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions>
- Copilot Agent mode (VS Code): <https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode>
- GitHub Copilot Trust Center: <https://github.com/features/copilot/trust-center>
