We thank the reviewer for the insightful and positive feedback. Please see below for our response.
**1. Agent-centric evaluation:**
We appreciate this suggestion. We conduct agent-centric evaluations using OpenHands[1] on our dataset, and please see below for results. We use the default setting from openhands code repo and change the LLM provider to the following three models in secure coding tasks:

| Model             | Python        | Python         | C/C++         | C/C++          | 
|-------------------|---------------|----------------|---------------|----------------|
|                   | original eval | Openhands eval | original eval | Openhands eval | 
| GPT-4o-2024-08-06 | 51%           | 54%            | 10%           | 14%            | 
| Claude-3.7-Sonnet | 63%           | 65%            | 19%           | 26%            | 
| DeepSeek-R1-0528  | 53%           | 52%            | 7%            | 8%             | 

We observe that agentic evaluations yield higher performance than our original evaluation.
Claude-3.7-Sonnet achieves the highest improvement, with a 50% increase in Python and a 15% increase in C/C++.
DeepSeek-R1-0528 shows the lowest improvement and even a slight decrease in python.
In language aspect, we find that Python shows the lowest improvement, while C/C++ shows the highest improvement.
We think this is because our Python dataset is relatively easy, and model-level evaluation is sufficient to finish the task.
And Claude-3.7-Sonnet is the best agentic model among the three, as we see it has the highest improvements from model-level evaluation to agentic evaluation.

**2. Language coverage:**
We acknowledge that including JavaScript, TypeScript, Go, and Rust would enhance the benchmark's comprehensiveness. 
We will explicitly list expanding to additional programming languages as part of our future work.
We chose to focus initially on Python, C/C++, and Java as they represent the highest number of security vulnerabilities and cover three major programming paradigms.

As a living benchmark, we are committed to continuous improvement.
For example, we've enhanced our mutation strategies including:
- Loop Transformations: While to for loop; Do-while to while loop; Loop unrolling
- Conditional Transformations: If-else to switch statements; Boolean expression simplification
- Method Refactoring: Extract method refactoring; Inline method for simple functions
- Code Style Changes: From procedural to functional style;

- **3. Computational cost of dynamic evaluation:**
Our evaluation suite is designed with flexibility in mind—researchers can choose from multiple evaluation metrics based on their computational constraints. 
As demonstrated in our codebase, we support various metrics including static analysis options. While we advocate for dynamic evaluation due to its superior precision, we provide alternative evaluation methods. 
Here are some initial results with CodeBleu[2]:

| Model             | Python    | Python   | C/C++     | C/C++    | Java      | Java     |
|-------------------|-----------|----------|-----------|----------|-----------|----------|
|                   | unit test | codebleu | unit test | codebleu | unit test | codebleu |
| GPT-4o-2024-08-06 | 53%       | 27%      | 10%       | 18%      | 24%       | 37%      |
| Claude-3.7-Sonnet | 68%       | 24%      | 21%       | 17%      | 46%       | 30%      |
| DeepSeek-R1-0528  | 55%       | 28%      | 13%       | 20%      | 33%       | 42%      |

We need to note here that CodeBLEU is not a perfect metric here because the correct implmentation of the code may be different from the original code, which may lead to lower CodeBLEU scores.

We hope these clarifications address your concerns.

[1]: OpenHands: An Open Platform for {AI} Software Developers as Generalist Agents
[2]: CodeBLEU: a Method for Automatic Evaluation of Code Synthesis