## **Proposal: Assessing the Political Alignment of Thought of Explicitly Biased LLMs**

### *Determining whether LLMs trained towards providing explicitly biased responses will be more internally consistent in their held beliefs*

---

### **1. Background and Motivation**
The paper "Political Bias in LLMs: Unaligned Moral Values in Agent-centric Simulations," (2025) posits that LLMs, even when given in-context content to try to align them towards a specific political or moral framework, are generally ineffective at maintaining internal belief consistency that aligns with human respondents. A natural extension of this observation, however, is the question of whether an LLM made to be explicitly biased towards a particular political or moral framework will hold greater internal belief consistency and produce outputs that closely align with a respective human group.
---

### **2. Research Question(s)**

**RQ:** Do explicitly biased LLMs maintain greater internal belief consistency as measured by consistent alignment with respective human groups? 

---

### **3. Methodology**
The most basic framework of this proposal would be an extension of Simon Münker's original paper focused on explicitly biased LLMs and assessing whether they present increased alignment with human respondents. Since we are updating the experiment, we can also assess other commonly used models such as the latest GPT or Claude versions to provide points of comparison. While I was unable to find any explicitly-crafted left-leaning LLMs (though there are a great many papers that observe evidently left-leaning tendencies in common LLMs like GPT), I would suggest that we can conduct this experiment focusing on the two prominent right-wing focused LLMs, X's Grok and Gab's Arya models. 

We have the option of using the same human respondent survey data as the original paper which would provide a direct means of comparison. That being said, given that the dataset was collected in 2011, it is possible that the right-wing moral frameworks possessed by the modern LLMs we seek to test are different than those of over a decade ago. For this reason, I would suggest using a human response dataset created more recently, focused on American frameworks (since both primary models to be tested are American), and centered on political beliefs. 

The core workflow as I envision it would consist of the following:

1. **Gather a Reference Dataset of Human Responses to Political/Moral Framework Questions**
    - Any human response dataset should have respondents organized by their self-declared political affiliation so that we may assess alignment of our models both in terms of strong alignment with conservative human responses and strong unalignment with liberal human responses.
    - We also have the option of testing on several datasets. 
2. **Question the Selection of Models Along the Same Guidelines as the Human Respondents Using Simple Prompting**
3. **Compare LLM Response Alignment with Human Respondents**

---

### **4. References**

Political Bias in LLMs: Unaligned Moral Values in Agent-centric Simulations (2025) - Simon Münker