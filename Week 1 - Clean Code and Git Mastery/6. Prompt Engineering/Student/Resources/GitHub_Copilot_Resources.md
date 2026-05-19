# GitHub Copilot: Free Online Resources

A curated list of freely accessible resources for learning and teaching GitHub Copilot for software development and testing. Every link here is to material that is free to read online without a paywall. Resources marked with a license are also free to redistribute under that license's terms; the rest are free to link to, free to read, but may not be republished without permission.

All resources were verified accessible as of May 2026.

---

## Quick start: the one-page picture

If you only have time for one link from this page use this one:

- [Quickstart for GitHub Copilot](https://docs.github.com/copilot/quickstart) (GitHub Docs)
  Sign up, install, run your first prompt. Twenty minutes.

If you need a second, this is a good follow-up:

- [Get started with GitHub Copilot in VS Code](https://code.visualstudio.com/docs/copilot/getting-started) (VS Code Docs)
  A hands-on tutorial that builds a working web app while introducing inline suggestions, chat, agents, and customization. About an hour.

---

## Official documentation

These are the canonical references. When the docs and a tutorial disagree, the docs are right (and the tutorial is probably out of date).

- [GitHub Copilot documentation home](https://docs.github.com/en/copilot) (GitHub Docs, CC BY 4.0)
  The full official documentation, organized by feature: Copilot in the IDE, Copilot CLI, Copilot Chat, custom agents, MCP servers, billing, security.

- [What is GitHub Copilot?](https://docs.github.com/en/copilot/get-started/what-is-github-copilot) (GitHub Docs)
  The plain-English overview. Good first reading for students.

- [GitHub Copilot features](https://docs.github.com/en/copilot/get-started/features) (GitHub Docs)
  Enumerates everything Copilot can do today: code completion, chat, CLI, code review, agent mode, cloud agent.

- [Best practices for using GitHub Copilot](https://docs.github.com/en/copilot/get-started/best-practices) (GitHub Docs)
  Concise; printable. Covers prompt crafting, accepting/rejecting suggestions, and validating output.

- [GitHub Copilot in VS Code](https://code.visualstudio.com/docs/copilot/overview) (VS Code Docs, MIT)
  The VS Code-side companion to the Copilot docs. Editor-specific tips and screenshots.

- [Best practices for using AI in VS Code](https://code.visualstudio.com/docs/copilot/prompt-crafting) (VS Code Docs)
  Section "Reviewing AI output" is especially useful in a classroom: it lists the failure modes (bugs, security issues, context pollution) and how to catch them.

> **License note:** The `github/docs` repository is publicly available on GitHub under the MIT License for code and Creative Commons Attribution 4.0 for content. The `microsoft/vscode-docs` repository is MIT-licensed. Both can be redistributed with attribution.

---

## Prompt engineering

This is the single skill that most affects whether you get value out of Copilot. Three short resources cover it well together.

- [Prompt engineering for GitHub Copilot Chat](https://docs.github.com/en/copilot/concepts/prompting/prompt-engineering) (GitHub Docs)
  The official guide. Specific, opinionated, short.

- [How to write better prompts for GitHub Copilot](https://github.blog/developer-skills/github/how-to-write-better-prompts-for-github-copilot/) (GitHub Blog)
  A worked example: two developer advocates iterate on the same prompt until it produces what they want. 

- [Prompt examples (VS Code)](https://code.visualstudio.com/docs/copilot/chat/prompt-examples) (VS Code Docs)
  Copy-paste prompt templates for the most common tasks: code review, refactoring, writing tests, generating documentation.

---

## Testing-specific resources

For the testing with Copilot

- [Writing tests with GitHub Copilot](https://docs.github.com/en/copilot/tutorials/write-tests) (GitHub Docs)
  Full walk-through of using Copilot to write unit tests and integration tests. Uses a `BankAccount` class in Python as the running example.

- [Copilot Chat Cookbook: Testing code](https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook) (GitHub Docs)
  Recipe-style prompts: "generate unit tests," "create mock objects," "generate end-to-end tests," "fix failing tests." Each recipe is short, copy-paste-ready, and labelled by language.

- [Generating unit tests](https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook/testing-code/generate-unit-tests) (GitHub Docs)
  A focused recipe for the `/tests` slash command, with a worked Python example including how the AAA pattern (Arrange-Act-Assert) is produced automatically.

- [Generate unit tests (prompt file)](https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files/generate-unit-tests) (GitHub Docs)
  A reusable `.prompt.md` file students can drop into a repo to standardize the way Copilot generates tests. Useful as a class artifact.

- [How to generate unit tests with GitHub Copilot: Tips and examples](https://github.blog/ai-and-ml/github-copilot/how-to-generate-unit-tests-with-github-copilot-tips-and-examples/) (GitHub Blog)
  Longer-form, discussion-heavy companion to the docs above. Covers what makes a unit test *useful* (not just "passing").

- [Develop Unit Tests using GitHub Copilot Tools](https://learn.microsoft.com/en-us/training/modules/develop-unit-tests-using-github-copilot-tools/) (Microsoft Learn)
  Free interactive module. Uses C# and a `Library` application. About 60 minutes. Free Microsoft Learn account required to track progress; the content is readable without one.

---

## Hands-on courses (free, multi-module)

These take a few hours each, work like a textbook, and are explicitly designed for classroom use or self-study.

- [Mastering GitHub Copilot for Paired Programming](https://github.com/microsoft/Mastering-GitHub-Copilot-for-Paired-Programming) (Microsoft, MIT License)
  A 10-lesson course. Each lesson is a folder in the repo with explanation, exercises, and sample code. Covers chat, agent mode, MCP, the CLI, JavaScript, Python, SQL, legacy code modernization. **MIT-licensed: redistributable.**

- [Copilot CLI for Beginners](https://github.com/github/copilot-cli-for-beginners) (GitHub, MIT License)
  A 10-chapter course focused on the command-line interface. Builds a single Python book-collection app progressively across chapters. **MIT-licensed: redistributable.** Companion blog post: [Getting started with the GitHub Copilot CLI](https://github.blog/ai-and-ml/github-copilot/github-copilot-cli-for-beginners-getting-started-with-github-copilot-cli/).

- [GitHub Copilot Fundamentals Part 1](https://learn.microsoft.com/en-us/training/paths/copilot/) (Microsoft Learn)
  Six modules totalling about four hours. Topics: introduction, prompt engineering, using Copilot across environments, management, productivity, responsible AI. Free.

- [GitHub Copilot Fundamentals Part 2](https://learn.microsoft.com/en-us/training/paths/gh-copilot-2/) (Microsoft Learn)
  The follow-up: agent mode, cloud agent, GitHub MCP Server, code reviews. Free.

- [Get Started with AI-Assisted Development (AZ-2007)](https://learn.microsoft.com/en-us/training/paths/accelerate-app-development-using-github-copilot/) (Microsoft Learn)
  C#-focused. Six modules covering analysis, documentation, new code, unit tests, refactoring, and vibe coding. Free.

- [Introduction to GitHub Copilot (Coursera)](https://www.coursera.org/learn/introduction-to-microsoft-github-copilot) (Microsoft via Coursera)
  Short course (about 90 minutes). The course content is free to audit ("Full Course, No Certificate"); the certificate costs money. Useful as a single-sitting structured introduction.

---

## Customization: instructions, prompt files, custom agents
Helps bend Copilot to a specific style or task. Most useful for advanced work.

- [Your first custom instructions](https://docs.github.com/en/copilot/tutorials/customization-library/custom-instructions/your-first-custom-instructions) (GitHub Docs)
  The starting point. How to create a `.github/copilot-instructions.md` file that applies to every Copilot interaction in a repo.

- [Your first prompt file](https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files/your-first-prompt-file) (GitHub Docs)
  How to create a reusable `.prompt.md` that you can invoke with a slash command.

- [Prompt files (VS Code)](https://code.visualstudio.com/docs/copilot/customization/prompt-files) (VS Code Docs)
  The editor-side reference for prompt-file syntax, with examples.

- [Customize AI in Visual Studio Code](https://code.visualstudio.com/docs/copilot/customization/overview) (VS Code Docs)
  Overview of every customization mechanism: instructions, prompt files, custom agents, MCP servers, hooks. Good map of the territory.

- [Awesome GitHub Copilot Customizations](https://github.com/github/awesome-copilot) (GitHub, community)
  Curated, community-contributed instruction files, prompt files, custom agents, and chat modes. Browse the `instructions/` and `prompts/` folders for ready-to-use examples by language and framework.

- [Awesome Copilot Agents](https://github.com/Code-and-Sorts/awesome-copilot-agents) (Community)
  A separate curated list focused specifically on custom agents and MCP servers. Different scope from the github/awesome-copilot repo above; the two are complementary.

- [Introducing the Awesome GitHub Copilot Customizations repo](https://developer.microsoft.com/blog/introducing-awesome-github-copilot-customizations-repo) (Microsoft Developer Blog)
  Walks through what the repo contains and how to use the pieces. 

---

## Responsible and safe use

For the ethics / professional-practice portion of the course. These are especially worth assigning in an academic context where you may not have considered the legal and security implications.

- [GitHub Copilot Trust Center](https://copilot.github.trust.page/) (GitHub)
  The official statement on security, privacy, compliance, intellectual property, and indemnification. Specifically: how Copilot processes prompts, whether your code is used for training (no, by default), what the duplication-detection filter does.

- [How to responsibly adopt GitHub Copilot](https://github.blog/news-insights/policy-news-and-insights/how-to-responsibly-adopt-github-copilot-with-the-github-copilot-trust-center/) (GitHub Blog)
  The companion blog post. Frames the questions  developer should be asking before adopting any AI coding tool.

- [Establishing trust in using GitHub Copilot](https://resources.github.com/learn/pathways/copilot/essentials/establishing-trust-in-using-github-copilot/) (GitHub Resources)
  Plain-English explanation of the IP and indemnification questions, written for a non-lawyer audience.

- [AI prompt engineering safety best practices](https://github.com/github/awesome-copilot/blob/main/instructions/ai-prompt-engineering-safety-best-practices.instructions.md) (GitHub, community)
  A community-contributed instruction file covering safety, bias mitigation, security, and responsible AI usage. Doubles as a checklist for development work.

---

## Blog posts and additional reading

Useful as supplementary or "if you want to go deeper" material.

- [How to write better prompts for GitHub Copilot](https://github.blog/developer-skills/github/how-to-write-better-prompts-for-github-copilot/) (GitHub Blog)

- [GitHub Copilot tutorials hub](https://github.com/features/copilot/tutorials) (GitHub)
  A landing page that points to every official tutorial, sorted by feature.

- [Copilot Chat Cookbook (index)](https://docs.github.com/en/copilot/tutorials/copilot-chat-cookbook) (GitHub Docs)
  The full menu of recipe-style prompts, not just the testing ones: debugging, refactoring, documentation, security, performance. 

- [Prompt engineering in VS Code (older but still good)](https://code.visualstudio.com/docs/copilot/chat/prompt-crafting) (VS Code Docs)
  Specifically the section "Be specific in your ask and break down large tasks."

- [GitHub Copilot Cheat Sheet (community)](https://github.com/kierunb/CopilotCheatSheet) (Community)
  Community-maintained cheat sheet. Two pages, printable. Note: this is a fork-of-a-fork of GitHub's own quick-reference and is community-maintained, not official.

---

