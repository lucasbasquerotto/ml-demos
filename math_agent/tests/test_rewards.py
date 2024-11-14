import unittest
from environment.state import State
from environment.reward import Reward

class TestReward(unittest.TestCase):
    def setUp(self):
        self.reward = Reward()
        self.current_state = State("x + 1")
        self.target_state = State("1 + x")

    def test_goal_achievement_reward(self):
        next_state = State("1 + x")
        reward = self.reward.calculate(self.current_state, next_state, self.target_state)
        self.assertEqual(reward, 100)

    def test_contradiction_reward(self):
        next_state = State("False")
        reward = self.reward.calculate(self.current_state, next_state, self.target_state)
        self.assertEqual(reward, 100)

    def test_intermediate_reward(self):
        next_state = State("x + 1")
        reward = self.reward.calculate(self.current_state, next_state, self.target_state)
        self.assertEqual(reward, -10)

if __name__ == "__main__":
    unittest.main()
