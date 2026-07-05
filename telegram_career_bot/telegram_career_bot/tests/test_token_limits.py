import tempfile
import unittest
from pathlib import Path

from db import database as db


class TokenLimitTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.tmpdir.name) / "test-bot.db"
        db.init_db()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_limit_blocks_service_after_threshold(self):
        user = db.create_user("user-1", username="Ada")
        self.assertEqual(user.get("token_limit"), 100)

        db.update_user("user-1", token_limit=2)

        allowed, updated = db.consume_tokens("user-1")
        self.assertTrue(allowed)
        self.assertEqual(updated.get("tokens_used"), 1)

        allowed, updated = db.consume_tokens("user-1")
        self.assertTrue(allowed)
        self.assertEqual(updated.get("tokens_used"), 2)

        allowed, updated = db.consume_tokens("user-1")
        self.assertFalse(allowed)
        self.assertEqual(updated.get("status"), "limit_reached")


if __name__ == "__main__":
    unittest.main()
