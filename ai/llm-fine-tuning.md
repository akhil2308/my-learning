# LLM Fine-Tuning Process

## 1\. Core Concepts: Before We Start

### Base Model vs. Instruct Model

  * **Base Model:** Think of this as a super-powerful "autocomplete." It is trained on raw internet text. If you ask it "What is the capital of France?", it might reply with "and what is the capital of Germany?" because it thinks it is completing a list.
  * **Instruct Model:** This is a base model that has already been fine-tuned to follow instructions. It understands how to chat and answer questions.

### The Tokenizer

The model understands numbers, not words. The tokenizer is the translator that converts your text into a specific format and then into numbers.

-----

## 2\. Data Preparation Pipeline

### A. Download & Split

1.  **Download:** Get your dataset.
2.  **Split:** Divide the data into two sets:
      * **Training Set:** Used to teach the model (usually 80-90%).
      * **Testing/Validation Set:** Used to check if the model is actually learning (usually 10-20%).

### B. Standard Chat Format

We must organize the raw text into a structured conversation format (JSON) so the model knows who is speaking.

```json
[
  {
    "role": "system",
    "content": "You are a helpful coding assistant."
  },
  {
    "role": "user",
    "content": "How do I print in Python?"
  },
  {
    "role": "assistant",
    "content": "You use the print() function."
  }
]
```

-----

## 3\. Tokenization Process

### A. Applying the Chat Template

Before converting to numbers, the tokenizer applies a specific **Chat Template**. This adds special characters (like `<|im_start|>` or `<s>`) required by the specific model (e.g., Llama 3 vs. Mistral) to separate the User from the Assistant.

### B. Numeric Conversion

Once the template is applied, the text is converted into **Numeric Tokens** (integers) that the model can process mathematically.

-----

## 4\. Efficient Processing: Batching & Padding

### Batch Size

We cannot feed the whole dataset at once or the GPU will run out of memory (OOM).

  * **Solution:** We use **Batches** (small groups of examples processed together).

### Padding

A batch must be a perfect rectangle matrix, meaning every sentence in the batch must have the **same length**.

  * **The Problem:** Real data has different sentence lengths.
  * **The Solution:** We add "dummy" tokens (Padding) to the shorter sentences to equal the length of the longest sentence.
  * **Left Padding:** We typically add these dummy tokens to the **left side** (the start) of the sequence. This ensures the actual meaningful data is at the end, which is better for the model when generating responses.

<!-- end list -->

```text
[PAD] [PAD] [PAD] [Hello] [World]  <-- Left Padding
[I] [am] [learning] [AI] [today]   <-- Full Length
```

-----

## 5\. LoRA (Low-Rank Adaptation)

Full fine-tuning updates *every* weight in the model, which is extremely expensive and slow.

  * **How LoRA works:** It freezes the main model weights and only trains tiny adapter layers on top of them.
  * **Benefit:** drastically reduces memory usage and allows you to fine-tune huge models on consumer hardware (like a single GPU).

-----
