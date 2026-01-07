"""
Main script for math agent training and testing.
Only built-in Python packages are used.
"""
from agent import Agent
from curriculum import Curriculum
from tokens import Node, Group, Assign, Var

def main():
    agent = Agent()
    curriculum = Curriculum(agent)
    print("Starting curriculum...")
    for _ in range(3):
        level = curriculum.advance()
        print(f"Curriculum advanced to level {level}")
        print(f"Agent custom node permission: {agent.can_define_nodes()}")
    # Demo: print a token tree
    tree = Group(Assign('a', 5), Node('Add', [Var('a'), 10]))
    print("Token tree:", tree)
    print("Evaluation result:", agent.evaluate(tree))

if __name__ == "__main__":
    main()
