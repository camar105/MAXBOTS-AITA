# nanoGPT Report

## Objective

This phase implements a compact character-level GPT model inspired by the nanoGPT teaching workflow. The goal was to understand transformer training behavior on a small public text corpus and compare a few architecture choices under a CPU-friendly training budget.

## Model Architecture

The implementation in `model.py` follows the standard small-GPT pattern:

- token embeddings
- learned positional embeddings
- masked multi-head self-attention
- feedforward network inside each transformer block
- residual connections and layer normalization
- final linear language-model head

This is a character-level model, so the network predicts the next character in the Tiny Shakespeare text.

## Training Setup

- Dataset: Tiny Shakespeare
- Tokenization: character-level vocabulary built from the dataset text
- Split: 90% train / 10% validation
- Optimizer: AdamW
- Device used: CPU
- Evaluation cadence: every 50 training iterations
- Validation estimate: average over 20 mini-batches each time

### Configurations used

| Config | Batch Size | Context | Layers | Heads | Embed | LR | Dropout |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 32 | 64 | 2 | 2 | 64 | 0.003 | 0.1 |
| `wider` | 32 | 64 | 2 | 4 | 96 | 0.003 | 0.1 |
| `deeper_context` | 24 | 96 | 3 | 4 | 96 | 0.003 | 0.1 |

## Experiment Set

Three configurations were defined in `configs/experiments.json` and trained successfully:

1. `baseline`
2. `wider`
3. `deeper_context`

Each configuration varied one or more of these factors:

- embedding size
- number of attention heads
- number of transformer blocks
- context length

## Results

| Config | Params | Best Val Loss | Runtime (s) | Main Change |
| --- | ---: | ---: | ---: | --- |
| `baseline` | 112,193 | 2.2770 | 7.13 | 2 layers, 2 heads, 64-dim embed |
| `wider` | 241,985 | 2.2269 | 12.11 | wider embedding and 4 heads |
| `deeper_context` | 356,609 | 2.3273 | 22.17 | more layers plus longer context |

### Loss Trend Summary

- `baseline`: validation loss improved from `4.1604` to `2.2770`
- `wider`: validation loss improved from `4.2022` to `2.2269`
- `deeper_context`: validation loss improved from `4.1992` to `2.3273`

The best validation loss came from the `wider` model.

## Qualitative Samples

### `baseline`

The generated text shows recognizable Shakespeare-style dialogue markers and names, but still contains many broken words:

> DUSAULAR:
> Thale, wil-s hart ar, my tintheeree; by.

### `wider`

The `wider` run shows slightly stronger structure and line transitions, even though the text is still noisy:

> LTUCIO, whof at leay:
> Shour; toukenk yas nod I lefte'tal, fo thand,

### `deeper_context`

The deeper + longer-context run still generates Shakespeare-like fragments, but under this short training budget it produced less stable text than `wider`:

> cavr ches Tin no nk myousent, f histhouw kngerong,
> And ound orad dotnd; aghak, this ourouand je lodenot heelft k:

## Analysis And Reflection

### What changed across experiments?

- Increasing width from `baseline` to `wider` improved validation loss noticeably.
- Increasing both depth and context length further did not help under the same short training budget.
- Runtime increased sharply as parameter count and context length increased.

### What did this teach us?

1. More capacity is not automatically better if the training budget stays fixed.
2. A moderate increase in width helped more than a deeper, slower model in this setup.
3. Validation loss and qualitative samples both matter when judging a language model.

### Overfitting and underfitting

- No severe overfitting appeared in these runs because train and validation loss both decreased together.
- The models were still underfit at the end of 250 iterations because the curves were still trending downward.
- The deeper model likely needed either more optimization steps or a different learning budget to benefit from its larger capacity.

### Training stability

- All three runs trained stably on CPU without loss spikes or divergence.
- Keeping dropout fixed at `0.1` and using short evaluation intervals made it easy to compare architectures under the same budget.

### Best configuration

`wider` was the strongest tradeoff in this experiment set because it achieved the best validation loss while still keeping runtime manageable on CPU.

## How This Informs The MVP

This phase reinforced two practical lessons for the product build:

- lightweight, well-scoped configurations are easier to train and evaluate reliably
- evaluation should combine both measurable metrics and direct output inspection

Those lessons shaped the MVP approach by favoring a practical, testable system over a larger but harder-to-verify one.
