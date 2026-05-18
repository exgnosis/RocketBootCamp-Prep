Multiple-Choice Questions on Prompt Engineering

- 9/15 version 1.0

---

1 Which of the following is not something prompting can do?
1. Influence output format
2. Reduce ambiguity
3. **_Install new knowledge permanently into the model_**
4. Shape probability distributions
5. Do not know
---

2 What happens when a prompt exceeds the context window?
1. The model refuses to respond
2. The model automatically summarizes the input
3. _**Earlier instructions are truncated and behavior may drift_**
4. The API silently doubles the context size
5. Do not know
---

3 When should you prefer examples (few-shot) over instructions alone?
1. When the task is trivial
2. **_When format is complex, reasoning pattern matters, or consistency is critical_**
3. When you want to minimize token usage
4. When the model has no instruction tuning
5. Do not know
---

4 Which of the following is true about the claude.ai system prompt?
1.Users can fully edit it from settings
2. It is a closely-guarded secret never published by Anthropic
3. **_It is set by Anthropic, fixed per session, and partly published openly_**
4. It is regenerated automatically from user messages
5. Do not know
---

5 What does chain-of-thought (CoT) prompting encourage the model to do?
1. Produce only the final answer with no explanation
2. **_Produce intermediate reasoning steps before the final answer_**
3. Use only short, terse responses
4. Skip uncertain calculations
5. Do not know


---

6 Why does spec-driven prompting work well for code generation?
1. The model randomly guesses better when given more text
2. Specifications bypass the model's safety training
3. Specs disable temperature sampling
4. **_The model has seen API docs, RFC-style specs, and GitHub READMEs during training, so structured prompts activate those patterns_**
5. Do not know

---

7 Why are prompt templates recommended in production systems?
1. They eliminate the need for testing
2. **_They make prompts modular, reusable, versioned, and testable, treating them like code artifacts_**
3. They allow prompts to bypass the model's system role
4. They are required by the Anthropic API
5. Do not know
---

8 Why are constraints important in prompts?
1. _**They reduce entropy, improve determinism, and reduce hallucination space_**
2. They make the model think more creatively
3. They allow the model to ignore the system prompt
4. They expand the context window
5. Do not know
---

9 Which scenario is best suited for using low temperature (≈ 0–0.3)?
1. Brainstorming marketing slogans
2. Generating creative fiction
3. _**Extracting structured data and generating code_**
4. Exploring alternative ideas
5. Do not know

---

10 What is the recommended way for advanced production systems to ensure outputs conform to a strict structure?
1. Trust the model output without checks
2. **_Validate against a JSON schema, reject invalid outputs, and retry with corrective instructions_**
3. Reduce temperature and top-p until the output stabilizes
4. Use an external validation tool to reject malformed outputs
5. Do not know

--- 

## End