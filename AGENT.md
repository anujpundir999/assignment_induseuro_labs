# AGENT.md — ShopAssist LLM Optimization Plan & Execution Tracker

## 1. Executive Summary & Objective

**Mission:** Complete both questions in the **ShopAssist LLM Optimization Assignment** to minimize token consumption and billing points while preserving 100% resolution accuracy and schema compatibility.

**Branch:** `solution`  
**Status:** **Completed & Verified** (All tests green, all targets beaten with >45% safety margin)

### The Billing Equation
$$\text{Total Points} = (\text{Uncached Input Tokens} \times 3) + (\text{Cached Input Tokens} \times 0.3) + (\text{Output Tokens} \times 15)$$

---

## 2. Deliverables Checklist

- [x] Create and checkout dedicated working branch (`solution`).
- [x] Configure offline dependency runtime and local tiktoken cache.
- [x] **Question 1 (`question1/agent.py`):**
  - [x] Eliminate verbose prompt keywords to prevent output inflation.
  - [x] Remove dynamic UUID prefix (`uuid.uuid4()`) to enable prompt prefix caching.
  - [x] Optimize input prompt structure with static system prefix $\ge 1024$ tokens.
  - [x] Pass target: **1,275 avg points / ticket** (Target: $\le \mathbf{3000}$, -57.5% below target).
  - [x] Ensure full accuracy on public tickets (`T-1001` - `T-1004`) + holdout (`T-1091`).
  - [x] Document per-call token & points breakdown for sample ticket (T-1001: 1,397 points).
- [x] **Question 2 (`question2/agent.py`):**
  - [x] Eliminate help center context bloat across pipeline nodes.
  - [x] Strip verbose triggers from all nodes.
  - [x] Streamline 4-node pipeline flow: deterministic RAG retrieval + cached compose node + schema audit.
  - [x] Pass target: **1,326 avg points / ticket** (Target: $\le \mathbf{2500}$, -47.0% below target).
  - [x] Ensure full accuracy on public tickets (`T-1001` - `T-1004`).
  - [x] Document points breakdown for physical fulfillment path (T-1004: 1,262 points) and denial path (T-1002: 1,310 points).
- [x] **Project Documentation & Submission:**
  - [x] Author comprehensive `SUBMISSION.md` covering architecture, benchmarks, mathematical proofs, and trade-offs.
  - [x] Provide complete demo video walkthrough script.

---

## 3. Results Summary

| Question | Baseline Cost | Target Limit | Achieved Cost | Savings | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Q1 (Single Call)** | 8,886 pts/ticket | $\le 3,000$ pts/ticket | **1,275 pts/ticket** | **-85.6%** | **PASSED** |
| **Q2 (Pipeline)** | 73,153 pts/ticket | $\le 2,500$ pts/ticket | **1,326 pts/ticket** | **-98.2%** | **PASSED** |

---

## 4. Verification Commands

```bash
# Run test suite
TIKTOKEN_CACHE_DIR=$(pwd)/.tiktoken_cache .venv/bin/pytest -v

# Run Question 1 runner
TIKTOKEN_CACHE_DIR=$(pwd)/.tiktoken_cache .venv/bin/python3 question1/run.py

# Run Question 2 runner
TIKTOKEN_CACHE_DIR=$(pwd)/.tiktoken_cache .venv/bin/python3 question2/run.py
```
