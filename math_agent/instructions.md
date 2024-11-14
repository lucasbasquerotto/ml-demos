## Agent Specification

The objective of the agent is to determine if two given expressions, `expression1` and `expression2`, are mathematically equivalent by applying a series of valid transformations. The agent must use known mathematical properties and definitions to transform `expression1` into `expression2`. If the transformation is successful, the agent will have proven that `expression1 = expression2`. If not, and the process reaches a contradiction, it shows that the expressions are not equivalent.

## Environment Specification

The environment is modeled as a Markov Decision Process (MDP), where each element is defined as follows:

#### 1. States
- **State Space $S$**: Each state $S_i$ is a representation of an intermediate form of `expression1` after a series of transformations.
  - **Initial State $S_0$**: The initial state corresponds to `expression1`.
  - **Goal State $S_{target}$**: The goal state is reached when the agent’s current expression matches `expression2`.
  - **Contradictory State**: A special terminal state that indicates the transformations cannot produce an equivalent form of `expression2`.

#### 2. Actions
- **Action Space $A$**: Each action represents a transformation based on mathematical properties or definitions known to the agent.
  - **Examples of Actions**:
    - **Exponentiation**: e.g., $X^2 = X \times X$
    - **Associative Product**: e.g., $(a + b)(c + d) = ac + ad + bc + bd$
    - **Commutative Property of Addition and Multiplication**: e.g., $ a + b = b + a $, $ a \times b = b \times a $
    - **Simplification**: e.g., $ A + A = 2A $
  - Each action, when applied, results in a new state.

#### 3. Transition Function
- **Transition Function $ T(S, A) $**: Determines the resulting state after an action is applied to a given state.
  - **Deterministic Transitions**: Each action leads deterministically to a new state by applying a mathematical rule directly to the expression.
  - **Example**: Applying the associative product action to $ (a + b)(a + b) $ yields $ aa + ab + ba + bb $.

#### 4. Rewards
- **Reward Function $ R $**:
  - **Goal Achievement**: A positive reward for reaching the goal state $ S_{target} $ (proving `expression1 = expression2`).
  - **Intermediate Rewards**: Small positive rewards for transformations that bring the expression closer in structure to `expression2`.
  - **Contradiction Penalty**: A negative reward (penalty) if a transformation leads to a contradiction or state where no further useful transformations are possible.

#### 5. Episode End Conditions
- **Success Condition**: The episode ends successfully if the agent reaches the target expression, showing that `expression1` is equivalent to `expression2`.
- **Failure Condition**: The episode ends in failure if the agent reaches a contradictory state or if no further transformations progress toward the goal.

### Additional Notes
- **Heuristic Guidance**: The environment may employ heuristics to estimate structural similarity to the target expression, guiding the agent’s actions.
- **Exploration**: If multiple transformations apply, the agent may prioritize transformations that reduce the complexity or number of terms in the expression.
- **Cycles**: It may be useful to verify if the agent ends up in the same state as it was in some previous time-step to avoid an infinite loop of actions, or give a negative reward for each time-step with truncation if the objective was not reached after lots of actions.


## Files and Purpose

```
math_agent/
├── main.py
├── README.md
├── requirements.txt
├── config/
│   └── settings.py
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── policy.py
│   └── heuristic.py
├── environment/
│   ├── __init__.py
│   ├── environment.py
│   ├── state.py
│   ├── action.py
│   ├── reward.py
│   └── transition.py
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_environment.py
│   └── test_rewards.py
└── utils/
    ├── __init__.py
    ├── logger.py
    ├── validator.py
    └── expression_parser.py
```

- **`main.py`**
  Entry point. Initializes the environment, creates the agent, and runs the MDP.

- **`README.md`**
  Project documentation including overview, setup, and usage instructions.

- **`requirements.txt`**
  Python dependencies required to run the project.

---

### Configurations

- **`config/settings.py`**
  Global configurations such as MDP settings and agent hyperparameters.

---

### Agent Files

- **`agent/agent.py`**
  Main class implementing the agent’s logic and interactions with the environment.

- **`agent/policy.py`**
  Policy logic that chooses the agent's actions based on state info, possibly using heuristics.

- **`agent/heuristic.py`**
  Provides heuristic functions to assess the similarity of states to the target expression.

---

### Environment Files

- **`environment/environment.py`**
  Main environment class defining the MDP, episode structure, and state transition logic.

- **`environment/state.py`**
  Represents each state as an intermediate form of the expression, with relevant metadata.

- **`environment/action.py`**
  Defines actions, representing transformations like exponentiation and simplification.

- **`environment/reward.py`**
  Defines the reward function, assigning rewards for goals and penalties for contradictions.

- **`environment/transition.py`**
  Implements the transition function, determining state changes based on actions taken.

---

### Testing Suite

- **`tests/` Folder**
  Contains unit tests for the agent, environment, transformations, and reward logic.

---

### Utilities

- **`utils/logger.py`**
  Logging utilities for tracking agent actions, rewards, and states.

- **`utils/validator.py`**
  Contains validation functions for inputs like expressions and transformations.

- **`utils/expression_parser.py`**
  Provides tools to parse and manipulate expressions, critical for transformation application.

This structure is designed to support modular development, easy expansion, and thorough testing, helping ensure the agent can accurately assess mathematical equivalencies.