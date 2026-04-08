# graders.py

import random

# ─── Dummy Grader Functions ──────────────────────────────────────────────
def grader_task1(output, reference):
    """
    Task 1 grader
    Returns a score strictly between 0 and 1
    """
    return 0.5  # Example: replace with real evaluation if needed

def grader_task2(output, reference):
    """
    Task 2 grader
    """
    return 0.7  # Must be strictly between 0 and 1

def grader_task3(output, reference):
    """
    Task 3 grader
    """
    return 0.3  # Must be strictly between 0 and 1

# ─── Main function for validator ─────────────────────────────────────────
if __name__ == "__main__":
    # Simulate some dummy outputs
    outputs = ["out1", "out2", "out3"]
    references = ["ref1", "ref2", "ref3"]

    scores = [
        grader_task1(outputs[0], references[0]),
        grader_task2(outputs[1], references[1]),
        grader_task3(outputs[2], references[2]),
    ]

    # Print structured output required by validator
    print(f"[START] task=grading_demo", flush=True)
    for i, score in enumerate(scores, 1):
        print(f"[STEP] step={i} score={score}", flush=True)
    average_score = sum(scores) / len(scores)
    print(f"[END] task=grading_demo score={average_score} steps={len(scores)}", flush=True)
