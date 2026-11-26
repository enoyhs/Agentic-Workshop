import unittest
from unittest import mock

from app import analyzer, service
from app.store import Store


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def test_list_shows_only_my_repositories(self):
        names = [repo["name"] for repo in service.list_repositories(self.store, "alice")]
        self.assertEqual(names, ["payments-api", "web-portal"])

    def test_unknown_user_is_rejected(self):
        with self.assertRaises(service.Unauthorized):
            service.list_repositories(self.store, "mallory")

    def test_cannot_open_someone_elses_repository(self):
        with self.assertRaises(service.Forbidden):
            service.get_repository(self.store, "bob", 1)

    def test_missing_repository(self):
        with self.assertRaises(service.NotFound):
            service.get_repository(self.store, "alice", 999)

    def test_scan_updates_time_and_analysis(self):
        before = service.get_repository(self.store, "alice", 1)["last_scanned_at"]
        analysis = service.scan_repository(self.store, "alice", 1)
        after = service.get_repository(self.store, "alice", 1)["last_scanned_at"]
        self.assertNotEqual(before, after)
        self.assertEqual(analysis["scanned_at"], after)

    def test_register_failure_in_analysis_leaves_store_untouched(self):
        repositories, analyses, next_id = dict(self.store.repositories), dict(self.store.analyses), self.store.next_id
        with mock.patch.object(analyzer, "analyze", side_effect=RuntimeError("analyzer down")):
            with self.assertRaises(RuntimeError):
                service.register_repository(self.store, "alice", {"name": "x", "url": "https://example.com/x"})
        self.assertEqual(self.store.repositories, repositories)
        self.assertEqual(self.store.analyses, analyses)
        self.assertEqual(self.store.next_id, next_id)
        names = [repo["name"] for repo in service.list_repositories(self.store, "alice")]
        self.assertNotIn("x", names)

    def test_register_assigns_next_id(self):
        repo = service.register_repository(self.store, "chen", {"name": "x", "url": "https://example.com/x"})
        self.assertEqual(repo["id"], 5)
        self.assertEqual(self.store.next_id, 6)

    def test_analysis_is_stable_for_the_same_url(self):
        repo = self.store.repositories[1]
        first = analyzer.analyze(repo, "2026-01-01T00:00:00Z")
        second = analyzer.analyze(repo, "2026-01-01T00:00:00Z")
        self.assertEqual(first, second)
        self.assertEqual(sum(first["languages"].values()), 100)


if __name__ == "__main__":
    unittest.main()
