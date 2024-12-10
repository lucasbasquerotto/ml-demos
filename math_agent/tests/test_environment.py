import unittest
from environment.environment import Environment
from environment.action import Action
from utils.types import Expression

class TestEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = Environment("x + 1", "1 + x")

    def test_initial_state(self):
        self.assertEqual(str(self.env.initial_state.expression), "x + 1")

    def test_step(self):
        action = Action(Expression("x + 1"), Expression("1 + x"))
        next_state, reward, terminated, truncated = self.env.step(action)
        self.assertEqual(str(next_state.expression), "1 + x")
        self.assertEqual(reward, 100)
        self.assertTrue(terminated)
        self.assertFalse(truncated)

    def test_reset(self):
        self.env.reset()
        self.assertEqual(str(self.env.current_state.expression), "x + 1")

if __name__ == "__main__":
    unittest.main()
