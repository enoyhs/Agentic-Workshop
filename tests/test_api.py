import json
import threading
import unittest
import urllib.error
import urllib.request

from app.server import RegistryServer

# Ignore any system proxy: these requests go to a server on this machine.
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class ApiTests(unittest.TestCase):
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

    def call(self, method, path, user=None, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(self.base + path, data=data, method=method)
        if user:
            request.add_header("X-User", user)
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with OPENER.open(request, timeout=5) as response:
                return response.status, json.loads(response.read() or b"null")
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read() or b"null")

    def test_health(self):
        self.assertEqual(self.call("GET", "/health"), (200, {"status": "ok"}))

    def test_list_defaults_to_alice(self):
        status, repos = self.call("GET", "/repositories")
        self.assertEqual(status, 200)
        self.assertEqual([repo["owner"] for repo in repos], ["alice", "alice"])

    def test_list_for_another_user(self):
        status, repos = self.call("GET", "/repositories", user="bob")
        self.assertEqual(status, 200)
        self.assertEqual([repo["name"] for repo in repos], ["data-pipeline"])

    def test_unknown_user(self):
        status, _ = self.call("GET", "/repositories", user="mallory")
        self.assertEqual(status, 401)

    def test_other_users_repository_is_forbidden(self):
        status, _ = self.call("GET", "/repositories/3", user="alice")
        self.assertEqual(status, 403)

    def test_missing_repository(self):
        status, _ = self.call("GET", "/repositories/999")
        self.assertEqual(status, 404)

    def test_analysis_and_scan(self):
        status, analysis = self.call("GET", "/repositories/1/analysis")
        self.assertEqual(status, 200)
        self.assertEqual(analysis["repository_id"], 1)

        status, rescanned = self.call("POST", "/repositories/1/scan")
        self.assertEqual(status, 200)
        self.assertNotEqual(rescanned["scanned_at"], analysis["scanned_at"])

    def test_register_then_list_detail_and_analysis(self):
        body = {"name": "new-service", "url": "https://github.com/example-org/new-service", "description": "New"}
        status, repo = self.call("POST", "/repositories", user="bob", body=body)
        self.assertEqual(status, 201)
        self.assertEqual(repo["owner"], "bob")
        self.assertEqual(repo["description"], "New")
        self.assertEqual(repo["registered_at"], repo["last_scanned_at"])

        status, repos = self.call("GET", "/repositories", user="bob")
        self.assertIn(repo["id"], [r["id"] for r in repos])
        self.assertEqual(self.call("GET", f"/repositories/{repo['id']}", user="bob"), (200, repo))

        status, analysis = self.call("GET", f"/repositories/{repo['id']}/analysis", user="bob")
        self.assertEqual(status, 200)
        self.assertEqual(analysis["repository_id"], repo["id"])
        self.assertEqual(analysis["scanned_at"], repo["last_scanned_at"])

    def test_registered_repository_is_hidden_from_other_users(self):
        _, repo = self.call("POST", "/repositories", user="bob", body={"name": "x", "url": "https://example.com/x"})
        _, alice_repos = self.call("GET", "/repositories", user="alice")
        self.assertNotIn(repo["id"], [r["id"] for r in alice_repos])
        self.assertEqual(self.call("GET", f"/repositories/{repo['id']}", user="alice")[0], 403)
        self.assertEqual(self.call("GET", f"/repositories/{repo['id']}/analysis", user="alice")[0], 403)

    def test_register_description_defaults_to_empty(self):
        status, repo = self.call("POST", "/repositories", body={"name": "x", "url": "https://example.com/x"})
        self.assertEqual(status, 201)
        self.assertEqual(repo["description"], "")
        self.assertEqual(repo["owner"], "alice")

    def test_register_rejects_invalid_bodies(self):
        bad_bodies = [
            None,
            ["name", "url"],
            {"url": "https://example.com/x"},
            {"name": "x"},
            {"name": "   ", "url": "https://example.com/x"},
            {"name": "x", "url": ""},
            {"name": 5, "url": "https://example.com/x"},
            {"name": "x", "url": "https://example.com/x", "description": 7},
        ]
        for body in bad_bodies:
            with self.subTest(body=body):
                status, _ = self.call("POST", "/repositories", body=body)
                self.assertEqual(status, 400)
        self.assertEqual(len(self.call("GET", "/repositories")[1]), 2)

    def test_register_rejects_malformed_json(self):
        request = urllib.request.Request(self.base + "/repositories", data=b"{not json", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as caught:
            OPENER.open(request, timeout=5)
        self.assertEqual(caught.exception.code, 400)
        self.assertEqual(len(self.server.store.repositories), 4)

    def test_register_unknown_user(self):
        status, _ = self.call("POST", "/repositories", user="mallory", body={"name": "x", "url": "https://example.com/x"})
        self.assertEqual(status, 401)
        self.assertEqual(len(self.server.store.repositories), 4)

    def test_unknown_endpoint(self):
        status, _ = self.call("GET", "/nope")
        self.assertEqual(status, 404)

    def test_wrong_method(self):
        status, _ = self.call("PUT", "/health")
        self.assertEqual(status, 405)

    def test_invalid_json_body(self):
        request = urllib.request.Request(
            self.base + "/repositories/1/scan", data=b"{not json", method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as caught:
            OPENER.open(request, timeout=5)
        self.assertEqual(caught.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
