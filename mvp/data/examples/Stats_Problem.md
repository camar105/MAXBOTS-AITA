#  Homework Walkthrough
## 1. Problem Classification
- **Topic:** Statistics
- **Problem Type:** One-sample hypothesis test for a population mean
- **Difficulty Level:** Medium

---

## 2. Given Information
- Sample size: \( n = 25 \)
- Sample mean: \( \bar{x} = 52 \)
- Population standard deviation: \( \sigma = 10 \)
- Claimed population mean: \( \mu_0 = 48 \)
- Significance level: \( \alpha = 0.05 \)

---

## 3. What is Being Solved
Determine whether there is enough evidence to conclude that the true population mean is different from 48.

---

## 4. Strategy Selection
Because the population standard deviation is known, this is a **one-sample z-test for the mean**.

We will:
1. State the null and alternative hypotheses
2. Compute the test statistic
3. Find the p-value
4. Compare the p-value to the significance level
5. Make a conclusion in context

---

## 5. Step-by-Step Solution

### Step 1: State the Hypotheses
- Null hypothesis: \( H_0 : \mu = 48 \)
- Alternative hypothesis: \( H_a : \mu \ne 48 \)

This is a **two-tailed test** because we are checking whether the mean is different from 48, not specifically greater or less.

---

### Step 2: Write the Test Statistic Formula
For a one-sample z-test:

\[
z = \frac{\bar{x} - \mu_0}{\sigma / \sqrt{n}}
\]

---

### Step 3: Substitute the Given Values
\[
z = \frac{52 - 48}{10 / \sqrt{25}}
\]

\[
z = \frac{4}{10 / 5}
\]

\[
z = \frac{4}{2} = 2.00
\]

---

### Step 4: Find the p-value
Since this is a two-tailed test:

\[
p = 2P(Z > 2.00)
\]

From the standard normal table:

\[
P(Z > 2.00) = 0.0228
\]

So:

\[
p = 2(0.0228) = 0.0456
\]

---

### Step 5: Decision
- \( p = 0.0456 \)
- \( \alpha = 0.05 \)

Since:

\[
p < \alpha
\]

we **reject the null hypothesis**.

---

## 6. Final Answer
There is sufficient evidence at the 5% significance level to conclude that the true population mean is different from 48.

---

## 7. Interpretation of Results
The sample provides enough statistical evidence to suggest that the population mean is not equal to the claimed value of 48. Since the sample mean is 52, the data suggests the true mean may be higher, but the formal conclusion of this test is only that it is different.

---

## 8. Quick Check
- Correct test used? ✔ One-sample z-test  
- Two-tailed setup correct? ✔  
- Arithmetic correct? ✔  
- p-value compared to alpha correctly? ✔  

---

## 9. Common Mistakes
- Using a t-test when the population standard deviation is known
- Forgetting that “different from” means a two-tailed test
- Comparing the test statistic directly to alpha instead of using a p-value or critical value
- Writing the conclusion without referencing the original context

---

## 10. Key Insight (Exam Tip)
Always decide the test type first by checking whether \( \sigma \) is known and whether the claim is about “equal to,” “greater than,” or “less than.” That determines the formula and whether the test is one-tailed or two-tailed.
