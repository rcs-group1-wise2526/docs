# Methodology

I think this study should evaluates whether a Large Language Model (LLM) (i) reproduces human-like psychometric structure and behavior in a source language and (ii) preserves its psychometric structure and behavior across languages. I think we should analyze two research questions (RQs) using two complementary dimensions:

- **Dimension A (Structure): Correlation-Based Fingerprinting + Community Recovery (EGA) + Internal Consistency (Cronbach’s alpha)**  
Do the groups produce similar correlation-based “psychometric fingerprints” and be consistent with the intended factor organization, and do subdomains show comparable internal consistency?
- **Dimension B (Behavior): Response Alignment via 1-Wasserstein Distance**  
Do the groups produce similar item-level Likert response distributions?

**Reference:**

[Fingerprinting LLMs through Survey Item Factor Correlation: A Case Study on Humor Style Questionnaire](https://aclanthology.org/2025.emnlp-main.13/) (Münker, EMNLP 2025)

[Reward Model Perspectives: Whose Opinions Do Reward Models Reward?](https://aclanthology.org/2025.emnlp-main.754/) (Elle, EMNLP 2025)

## Data

### Instrument
- **BFI-2**

### LLM Synthetic Responses (Per Language)
For each language $L \in \{L_{\text{src}}, L_{\text{tgt}}\}$:

### Human Benchmark Data
- Item-level BFI-2 datasets:
  - $H_{\text{src}}$ (humans in source language)

## Research Questions

| Research Question | Comparison | Goal |
|---|---|---|
| **RQ1: Anthropomorphic Validity** | LLM($L_{\text{src}}$) vs Human($H_{\text{src}}$) | Does the LLM reproduce human-like psychometric structural patterns and response behavior? |
| **RQ2: Cross-Lingual Consistency** | LLM($L_{\text{src}}$) vs LLM($L_{\text{tgt}}$) | Does the LLM preserve psychometric structural patterns and response behavior across languages? |

## Dimension A: Structural Similarity via Fingerprinting + EGA + Cronbach’s Alpha

### Core idea
Dimension A evaluates structural similarity by comparing how items relate to each other (and to the intended factor organization) across datasets.

fingerprint approach:

1. Build a correlation-based fingerprint for each dataset.
2. Compare fingerprints between datasets using cosine similarity.
3. Recover latent structure using Exploratory Graph Analysis (EGA) and compare it to the expected theoretical structure.
4. Compute Cronbach’s alpha

to answer:

1. Item–item correlation “fingerprint”: do items relate to each other similarly across datasets?
2. Community recovery (EGA): does the correlation network recover the expected theoretical structure?
3. Internal consistency (Cronbach’s alpha): do each domain(subscale)’s items “hang together” similarly within each dataset?

### Step A1: Compute the item–item correlation matrix
For each dataset $D$ (e.g., LLM-src, LLM-tgt, Human-src), compute a $Q \times Q$ item Pearson correlation matrix:

- Let $Q=60$ items.
- Let $R^{(D)}$ be the correlation matrix where entry $r_{jk}$ is the correlation between item $j$ and item $k$.

### Step A2: Build the “fingerprint vector”
Convert the correlation matrix into a vector representation. Extract the upper triangle (excluding the diagonal):
 
 Let $\tilde{\mathbf{C}}_x = \mathrm{vec}(\mathbf{C}_x)$ denote the vectorized form of the (upper-triangular, excluding the diagonal) item–item correlation matrix:
$$
\tilde{\mathbf{C}}_x = \mathrm{vec}(\mathbf{C}_x) = [c_{1,2}, c_{1,3}, \ldots, c_{1,I}, c_{2,3}, \ldots, c_{I-1,I}]^\top .
$$

This is the dataset’s structural fingerprint.

### Step A3: Compare fingerprints with cosine similarity
We compute fingerprint similarity between two datasets $x_1$ and $x_2$ using cosine similarity: (e.g., LLM-src vs Human-src):

$$
\mathrm{sim}(\tilde{\mathbf{C}}_{x_1}, \tilde{\mathbf{C}}_{x_2})
=
\frac{\sum_{k=1}^{L} \tilde{\mathbf{C}}_{x_1,k}\,\tilde{\mathbf{C}}_{x_2,k}}
{\sqrt{\sum_{k=1}^{L} (\tilde{\mathbf{C}}_{x_1,k})^2}\;\sqrt{\sum_{k=1}^{L} (\tilde{\mathbf{C}}_{x_2,k})^2}} \in [-1,1],
$$
where $L = I(I-1)/2$ is the length of the vectorized upper-triangle (excluding the diagonal).




**Interpretation**
- Values near 1.0: very similar fingerprints structure (high structural alignment).
- Lower values: structural drift (different relationships among items).

### Step A4: Structural recovery via Exploratory Graph Analysis (EGA)
EGA then detects communities (clusters) corresponding to latent constructs.

Evaluation theory:
- Count match: does latent constructs identified in LLM responses align with theoretical constructs in BFI-2?

Cross-dataset comparison:
- Compare clustering solutions across datasets (e.g., latent constructs consistency).

Draw the plot

### Step A5: Reliability via Cronbach’s alpha (internal consistency)
Compute internal consistency per domain by Cronbach’s alpha, providing insight into whether the items consistently measure the same underlying construct.



## Dimension B: Response Alignment (Distributional Consistency)

### Step B1: Build item response distributions
For each item $q$ and dataset $D$:

$$
D^{(D)}(q) = [P(y_q=1), P(y_q=2), P(y_q=3), P(y_q=4), P(y_q=5)].
$$

### Step B2: 1-Wasserstein distance
For two datasets $D_1, D_2$:

$$
W_1(D_1,D_2;q)
=
\sum_{k=1}^{4}
\left|
\sum_{i=1}^{k} D^{(D_1)}(q,i) - \sum_{i=1}^{k} D^{(D_2)}(q,i)
\right|.
$$

### Step B3: Alignment score

$$
A(q) = 1 - \frac{W_1(D_1,D_2;q)}{4}.
$$

Aggregate:
- Global:
  $$
  A_{\text{total}} = \frac{1}{Q}\sum_{q=1}^{Q} A(q).
  $$
- Domain-level: average $A(q)$ within each BFI-2 domain.

## Conclusion Interpretation

- High fingerprint similarity + EGA recovering the expected structure + Cronbach’s alpha supports structural construct alignment.
- High Wasserstein alignment supports behavioral alignment.
