We thank the reviewer for the insightful feedback. Please see below for our response.

# Main weaknesses

## 1. Mutation issues

First, we would like to clarify that our mutation strategy does not only modify the function names and variable names. Our mutation strategies also include:
- Loop Transformations: While to for loop; Do-while to while loop; Loop unrolling
- Conditional Transformations: If-else to switch statements; Boolean expression simplification
- Method Refactoring: Extract method refactoring; Inline method for simple functions
- Code Style Changes: From procedural to functional style

Here, we show an example with basic mutations (renaming) and Code Style Changes
```java
    // other context...
    public boolean isStringNotEmpty(String myString) throws Throwable {
        boolean isGreaterThanZero = false;
        if ((myString != null) & (myString.length() > 0)) {
            IO.writeLine("The string length is greater than 0");
            isGreaterThanZero = true;
        }
        return isGreaterThanZero;
    }
```

```java
    // other context...
    public boolean validateString(String myString) throws Throwable {
        return Optional.ofNullable(myString)
            .filter(s -> s.length() > 0)
            .map(s -> {
                try {
                    IO.writeLine("The string length is greater than 0");
                } catch (Exception e) {}
                return true;
            })
            .orElse(false);
    }
```

Second, our mutation is mainly applied to Python, where we generate 9 mutations from one seed. This is because python does not have real-world codebases as seeds and we manually write the seeds. For C/C++ and Java, we obtain enough seeds from the real-world codebase and only generate 1–2 variants per seed. As such, the impact of the mutation is constrained in our benchmark. 

Third, we conducted a **similarity filter** to remove too similar data samples. Below, we report the similarity of the original and the mutated data under two metrics: our selected editing distance and the  embedding similarities  based on OpenAI text-embedding model:

| Language | Ave. embedding Distance | Ave. editing distance |
|----------|-------------------------|-----------------------|
| Python   | 0.61                    | 0.517                 | 
| C/C++    | 0.52                    | 0.379                 | 
| Java     | 0.54                    | 0.408                 | 


## 2. Potential Memorization 
Our mutations can mitigate the issue of memorization as it has changed the prompts and code. In addition, the pool performance of the SOTA models show that the benchmark is still challenging. We will make our benchmark as a live one where we continuously include new repos to combat memorization.    

## 3. Python sample collection and real-world mapping
Sorry for the confusion. **Our Python samples are based on real CVEs**.  While we manually craft the code examples, each is grounded in top severe vulnerabilities as shown in Table 1 in the paper. . 

We chose manually creating seeds for Python because there is no existing Python dataset with comprehensive CWE coverage mapped to real-world codebases (similar to Arvo for C/C++ or Juliet for Java).

## 4. Function-level benchmark

We would like to clarify that our benchmark, especially for C/C++ and Java are repository-level. For vulnerability detection and patch generation, the users need to identify the vulnerable function from the given repo and patch them. Given the poor performance of SOTA models and agents, we provide additional contexts retrieved from the repo. On average, our full context contains:
- 1,831 tokens (avg across ARVO and Juliet datasets)
- Information spanning 4.7 files on average (6.1 files specifically in ARVO)
However, users can choose not to use our provided context and extract their own context using their agents.  

## 5. Potential data contamination and memorization 

Our mutations can mitigate the issue of memorization as it has changed the prompts and code. In addition, the pool performance of the SOTA models shows that the benchmark is still challenging.  We will make our benchmark as a live one where we continuously include new repos to combat memorization. In addition, we conduct the following analysis to show that our dataset has not been largely contaminated yet. 

We use Min-K[1] (top k=20) to detect potential training data contamination. As we do not have access to the logits of commercial models, we use Qwen2.5-32B (released December 2024) as a proxy.

| Dataset Source     | Min-K% Prob |
|--------------------|-------------|
| Arvo (Original)    | 19%         |
| Arvo (Mutated)     | 11%         |
| Juliet (Original)  | 57%         |
| Juliet (Mutated)   | 31%         |

The results show that our mutation can largely reduce the memorization concerns. Note that if the score is around or lager than 70%, the corresponding data is deemed as part of the training data [1]. In our case, the scores are all lower than this threshold.

We also evaluate models with knowledge cutoffs before and after August 2024 using our C/C++ data on secure code generation:

| Model             | Original | Mutated |
|-------------------|----------|---------|
| GPT-4o-2024-08-06 | 17%      | 9%      |
| GPT-4o-2024-11-20 | 16%      | 13%     |

The results demonstrate no significant performance advantage for models with more recent training data, suggesting that memorization does not substantially influence our evaluation outcomes. 

## 6. Failure case analysis 

We provide an example analysis here:

```c
// information that indicates this assertion
      static constexpr int32 motionOffset[7] = {-4, -2, -2, 0, 0, 2, 4};
      static constexpr int32 motionDoAverage[7] = {0, 0, 1, 0, 1, 0, 0};

      int32 slideOffset = motionOffset[motion];
      int32 doAverage = motionDoAverage[motion];

      for (uint32 i = 0; i < 16; i++) {
        ushort16* refpixel;

        if ((row + i) & 0x1) 
        {
          // Red or blue pixels use same color two lines up
          refpixel = img_up2 + i + slideOffset;

          if (col == 0 && img_up2 > refpixel)
            ThrowRDE("Bad motion %u at the beginning of the row", motion);
// assertion that LLM missed
          if (col + 16 == width &&
            ((refpixel >= img_up2 + 16) ||
             (doAverage && (refpixel + 2 >= img_up2 + 16))))
              ThrowRDE("Bad motion %u at the end of the row", motion);
// information that indicates this assertion
 else {
          // Green pixel N uses Green pixel N from row above
          // (top left or top right)
          refpixel = img_up + i + slideOffset + (((i % 2) != 0) ? -1 : 1);

          if (col == 0 && img_up > refpixel)
            ThrowRDE("Bad motion %u at the beginning of the row", motion);
        }

        // In some cases we use as reference interpolation of this pixel and
        // the next
        if (doAverage)
          img[i] = (*refpixel + *(refpixel + 2) + 1) >> 1;
        else
          img[i] = *refpixel;
      }
    }
        img += 16;
        img_up += 16;
        img_up2 += 16;
    }
```
In this code, the slideOffset comes from `motionOffset[motion]` which can be:
Positive values: 2, 4
At the end of the row, positive offsets can push refpixel beyond valid boundaries.
This can happen in two scenarios:
(1) `img_up2` points to the start of the reference row (2 rows above)
img_up2 + 16 points to the end of the current 16-pixel block in the reference row
refpixel is calculated as: `img_up2 + i + slideOffset`
If `refpixel >= img_up2 + 16`, it means we're trying to access pixels beyond the current block
This would be accessing unprocessed or invalid memory locations
(2) When doAverage is true, the code performs interpolation: `(*refpixel + *(refpixel + 2) + 1) >> 1`
This requires accessing both `refpixel` and `refpixel + 2`
If `refpixel + 2 >= img_up2 + 16`, the second pixel for averaging would be outside the valid block

The minimal fix for this issue is:
```
          if (
              ((refpixel >= width) ||
               (doAverage && (refpixel + 2 >= width))))
```
In models' response, all LLMs miss one of the conditions in the if statement, which is `refpixel + 2 >= img_up2 + 16`.
Besides, we also have some other observations below:
1. LLMs struggle with comprehensive analysis of complex code, especially when it involves multiple complex branches.
2. LLMs also hallucinate incorrect context, especially in vulnerability detection tasks, where they may reason with critical incorrect information and lead to incorrect conclusions.

## 7.Metrics beyond success rate

The unit test rate is the most accurate reflection of whether secure coding and patch generation tasks are completed. 
If phased indicators are needed, the metrics we can consider include BLEU, CodeBLEU, LLM Judge. 
Our evaluation suite is designed with flexibility in mind—researchers can choose from multiple evaluation metrics based on their computational constraints.
We provide some CodeBLEU results below.

| Model             | Python    | Python   | C/C++     | C/C++    | Java      | Java     |
|-------------------|-----------|----------|-----------|----------|-----------|----------|
|                   | unit test | codebleu | unit test | codebleu | unit test | codebleu |
| GPT-4o-2024-08-06 | 53%       | 27%      | 10%       | 18%      | 24%       | 37%      |
| Claude-3.7-Sonnet | 68%       | 24%      | 21%       | 17%      | 46%       | 30%      |
| DeepSeek-R1-0528  | 55%       | 28%      | 13%       | 20%      | 33%       | 42%      |

## 8. Levenshtein threshold

We select the 0.8 threshold based on empirical analysis. Specifically, we manually analyzed 20 samples to determine an appropriate threshold.

## 9. LLM dependency for evaluation and Figure 4 clarity

We acknowledge the dependency on LLMs for evaluation. To mitigate potential bias, we conduct experiments on other LLMs including DeepSeek-R1 and Gemini-2.5-pro, beyond the Claude and OpenAI results shown in the paper. 
We achieve an average 0.87 security relevance score, which is much higher than the 0.54 in CyberSecEval.

Regarding Figure 4's clarity, we agree the radar chart could be improved. We will provide a table format with exact values and confidence intervals in the revision.

## 10. On specific prompts and prompt engineering

Prompt word: we try different prompt words in Appendix J.1: default prompt, Auto CoT, Manual CoT.
Average Length: default prompt: 92 tokens, Auto CoT: 101 tokens, Manual CoT: 147 tokens.
We do not adjust prompts across languages.

## 11. Using other models for task description rewriting

We experiment with multiple models for task description generation. Our latest results use O3-mini, and we are continuously updating our dataset.
The task description is indeed more accurate in human inspection (Claude-3.7-Sonnet achieves 4.2% more in C/C++ Secure Coding), and we plan to continuously update our benchmark with the improved data.

[1] Detecting Pretraining Data from Large Language Models
