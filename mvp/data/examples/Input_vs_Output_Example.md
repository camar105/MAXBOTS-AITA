## Central Limit Theorem (Textbook Input Example)

Suppose eight of you roll one fair die ten times, seven of you roll two fair dice ten times, nine of you roll five fair dice ten times, and 11 of you roll ten fair dice ten times.

Each time a person rolls more than one die, they calculate the sample mean of the faces showing. For example, one person might roll five fair dice and get 2, 2, 3, 4, 6 on one roll.

The mean is (2 + 2 + 3 + 4 + 6) / 5 = 3.4. The 3.4 is one mean when five fair dice are rolled. This same person would roll the five dice nine more times and calculate nine more means for a total of ten means.

Your instructor will pass out the dice to several people. Roll your dice ten times. For each roll, record the faces, and find the mean. Round to the nearest 0.5.

Your instructor (and possibly you) will produce one graph (it might be a histogram) for one die, one graph for two dice, one graph for five dice, and one graph for ten dice. Since the "mean" when you roll one die is just the face on the die, what distribution do these means appear to be representing?

Draw the graph for the means using two dice. Do the sample means show any kind of pattern?

Draw the graph for the means using five dice. Do you see any pattern emerging?

Finally, draw the graph for the means using ten dice. Do you see any pattern to the graph? What can you conclude as you increase the number of dice?

As the number of dice rolled increases from one to two to five to ten, the following is happening:

1. The mean of the sample means remains approximately the same.
2. The spread of the sample means (the standard deviation of the sample means) gets smaller.
3. The graph appears steeper and thinner.

You have just demonstrated the central limit theorem (CLT).

The central limit theorem tells you that as you increase the number of dice, the sample means tend toward a normal distribution (the sampling distribution).




# OUTPUT Example
# 📘 Lecture Summary

## 1. Topic Overview
- **Course / Lecture Title:** Applied Statistics (MAE 301)
- **Main Topic:** Central Limit Theorem (CLT)
- **Subtopics Covered:**
  - Sample mean
  - Sampling distribution
  - Effect of sample size
  - Distribution of dice outcomes

---

## 2. Key Concepts
- Sample mean: average of outcomes from multiple trials  
- Sampling distribution: distribution of sample means  
- Central Limit Theorem: sample means tend toward a normal distribution as sample size increases  
- Variability reduction: spread decreases as sample size increases  

---

## 3. Simplified Explanation
When you roll dice multiple times and compute the average (mean) of each roll, those averages start forming a pattern. Even though individual dice rolls are random, the distribution of the averages becomes more predictable as the number of dice increases. Eventually, the distribution of these averages looks like a normal (bell-shaped) curve.

---

## 4. Important Formulas
| Formula | Meaning | When to Use |
|--------|--------|------------|
| \(\bar{x} = \frac{1}{n} \sum x_i\) | Sample mean | Average of dice rolls |
| \(\mu_{\bar{x}} = \mu\) | Mean of sample means | Always equals population mean |
| \(\sigma_{\bar{x}} = \frac{\sigma}{\sqrt{n}}\) | Standard error | Spread of sample means |

---

## 5. Step-by-Step Logic
1. Roll dice multiple times  
2. Compute the mean for each roll  
3. Repeat to get multiple sample means  
4. Plot the distribution of these means  
5. Observe how the shape changes as sample size increases  

---

## 6. Example Application
**Problem Type:** Sampling distribution  

**Given:**
- Rolling 5 dice
- Example roll: 2, 2, 3, 4, 6  

**Find:** Sample mean  

**Approach:**
1. Add values: 2 + 2 + 3 + 4 + 6 = 17  
2. Divide by number of dice (5)  

**Final Answer:**
\[
\bar{x} = 17 / 5 = 3.4
\]

---

## 7. Observed Patterns (From Experiment)
As the number of dice increases:
- The mean stays approximately the same  
- The spread (standard deviation) decreases  
- The graph becomes narrower and more bell-shaped  

---

## 8. Common Mistakes / Pitfalls
- Confusing individual outcomes with sample means  
- Assuming the original data must be normal  
- Forgetting that variability decreases with larger sample size  

---

## 9. Key Takeaways
- Sample means become normally distributed as sample size increases  
- The mean remains constant, but variability decreases  
- This behavior demonstrates the Central Limit Theorem  
