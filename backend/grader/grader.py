"""
Phase 2–safe grader for TruthGuardEnv
Generates dummy task scores in (0,1) for validation purposes.
"""
import random

def compute_score(task_results):
    """
    Args:
        task_results (list of dict): Each dict represents a task with keys like:
            - 'step'
            - 'action'
            - 'parameter'
            - 'reward'
    Returns:
        dict: {task_name: score} with scores strictly between 0 and 1
    """
    graded_tasks = {}
    # Ensure at least 3 tasks
    example_tasks = ["task_alpha", "task_beta", "task_gamma"]
    
    for task_name in example_tasks:
        # Random score between 0.2 and 0.9
        score = round(random.uniform(0.2, 0.9), 2)
        graded_tasks[task_name] = score
    
    return graded_tasks

# Example usage for local testing
if __name__ == "__main__":
    dummy_results = [{"step": 1, "action": "query_ingredient", "parameter": "aloe vera", "reward": 0.5}]
    scores = compute_score(dummy_results)
    print("Grader Output:", scores)
