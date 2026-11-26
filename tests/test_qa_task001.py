"""Independent QA checks for TASK-001 repository registration."""

import json
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

from app import analyzer
from app.server import RegistryServer


OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class Task001QaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = RegistryServer(("127.0.0.1", 0), quiet=True)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.server.store.reset()

    def call(self, method, path, user=None, body=None, raw_body=None):
        data = raw_body if raw_body is not None else (None if body is None else json.dumps(body).encode("utf-8"))
        request = urllib.request.Request(self.base + path, data=data, method=method)
        if user is not None:
            request.add_header("X-User", user)
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with OPENER.open(request, timeout=5) as response:
                return response.status, json.loads(response.read() or b"null")
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read() or b"null")

    def test_ac1_registration_assigns_caller_and_handles_description(self):
        status, described = self.call(
            "POST",
            "/repositories",
            user="chen",
            body={"name": "alerts", "url": "https://example.test/alerts", "description": "Alert service"},
        )
        self.assertEqual(status, 201)
        self.assertEqual(described["owner"], "chen")
        self.assertEqual(described["description"], "Alert service")
        self.assertEqual(
            set(described),
            {"id", "name", "url", "description", "owner", "registered_at", "last_scanned_at"},
        )

        status, defaulted = self.call(
            "POST", "/repositories", user="bob", body={"name": "billing", "url": "https://example.test/billing"}
        )
        self.assertEqual(status, 201)
        self.assertEqual(defaulted["description"], "")

    def test_ac2_owner_can_list_and_read_immediate_analysis_but_other_user_cannot(self):
        status, created = self.call(
            "POST", "/repositories", user="bob", body={"name": "catalog", "url": "https://example.test/catalog"}
        )
        self.assertEqual(status, 201)

        status, repositories = self.call("GET", "/repositories", user="bob")
        self.assertEqual(status, 200)
        self.assertIn(created["id"], [repository["id"] for repository in repositories])
        self.assertEqual(self.call("GET", f"/repositories/{created['id']}", user="bob"), (200, created))
        status, analysis = self.call("GET", f"/repositories/{created['id']}/analysis", user="bob")
        self.assertEqual(status, 200)
        self.assertEqual(analysis["repository_id"], created["id"])
        self.assertEqual(analysis["scanned_at"], created["last_scanned_at"])

        _, alice_repositories = self.call("GET", "/repositories", user="alice")
        self.assertNotIn(created["id"], [repository["id"] for repository in alice_repositories])
        self.assertEqual(self.call("GET", f"/repositories/{created['id']}", user="alice")[0], 403)
        self.assertEqual(self.call("GET", f"/repositories/{created['id']}/analysis", user="alice")[0], 403)

    def test_ac3_wrong_inputs_return_400_without_creating_repository(self):
        initial_repositories = dict(self.server.store.repositories)
        initial_next_id = self.server.store.next_id
        invalid_bodies = [
            None,
            ["not", "an", "object"],
            {},
            {"name": "repo"},
            {"url": "https://example.test/repo"},
            {"name": "   ", "url": "https://example.test/repo"},
            {"name": "repo", "url": "\t"},
            {"name": 1, "url": "https://example.test/repo"},
            {"name": "repo", "url": "https://example.test/repo", "description": False},
        ]
        for body in invalid_bodies:
            with self.subTest(body=body):
                self.assertEqual(self.call("POST", "/repositories", user="alice", body=body)[0], 400)
        self.assertEqual(self.call("POST", "/repositories", user="alice", raw_body=b"{broken")[0], 400)
        self.assertEqual(self.server.store.repositories, initial_repositories)
        self.assertEqual(self.server.store.next_id, initial_next_id)

    def test_ac4_unknown_caller_returns_401_without_creating_repository(self):
        initial_repositories = dict(self.server.store.repositories)
        initial_next_id = self.server.store.next_id
        status, _ = self.call(
            "POST", "/repositories", user="mallory", body={"name": "repo", "url": "https://example.test/repo"}
        )
        self.assertEqual(status, 401)
        self.assertEqual(self.server.store.repositories, initial_repositories)
        self.assertEqual(self.server.store.next_id, initial_next_id)

    def test_ac5_analysis_failure_returns_500_and_rolls_back_registration(self):
        initial_repositories = dict(self.server.store.repositories)
        initial_analyses = dict(self.server.store.analyses)
        initial_next_id = self.server.store.next_id
        with mock.patch.object(analyzer, "analyze", side_effect=RuntimeError("QA simulated analyzer failure")):
            status, _ = self.call(
                "POST", "/repositories", user="alice", body={"name": "repo", "url": "https://example.test/repo"}
            )
        self.assertEqual(status, 500)
        self.assertEqual(self.server.store.repositories, initial_repositories)
        self.assertEqual(self.server.store.analyses, initial_analyses)
        self.assertEqual(self.server.store.next_id, initial_next_id)

    def test_regression_existing_list_and_analysis_still_work(self):
        status, repositories = self.call("GET", "/repositories", user="alice")
        self.assertEqual(status, 200)
        self.assertEqual([repository["id"] for repository in repositories], [1, 2])
        status, analysis = self.call("GET", "/repositories/1/analysis", user="alice")
        self.assertEqual(status, 200)
        self.assertEqual(analysis["repository_id"], 1)


if __name__ == "__main__":
    unittest.main()
