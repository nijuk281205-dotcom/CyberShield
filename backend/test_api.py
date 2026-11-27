"""Run: python test_api.py   (uses a temporary database)"""
import os
import tempfile
import unittest

from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.client = create_app({"DATABASE_PATH": self.tmp.name, "TESTING": True,
                                  "RATELIMIT_ENABLED": False}).test_client()

    def tearDown(self):
        os.unlink(self.tmp.name)

    def scan(self, kind, value):
        return self.client.post("/api/scan", json={"type": kind, "input": value})

    def test_levels(self):
        self.assertEqual(self.scan("url", "https://www.wikipedia.org").get_json()["risk_level"], "Low")
        self.assertEqual(self.scan("url", "http://192.168.1.5/secure-login/verify-account").get_json()["risk_level"], "High")
        self.assertEqual(self.scan("text", "URGENT! Your SBI account will be suspended. Share OTP now").get_json()["risk_level"], "High")

    def test_validation(self):
        self.assertEqual(self.scan("url", "").status_code, 400)
        self.assertEqual(self.scan("bad", "x").status_code, 400)
        self.assertEqual(self.scan("url", "not a url").status_code, 400)
        self.assertEqual(self.client.post("/api/scan", data="nope").status_code, 400)

    def test_history_stats_delete(self):
        a = self.scan("url", "https://example.com").get_json()
        self.scan("url", "http://paypal.secure-login.xyz/verify")
        h = self.client.get("/api/history").get_json()
        self.assertEqual(h["total"], 2)
        self.assertEqual(self.client.get("/api/history?search=paypal").get_json()["total"], 1)
        self.assertEqual(self.client.get("/api/history?risk=Low").get_json()["total"], 1)
        self.assertEqual(self.client.get("/api/history?search=%25").get_json()["total"], 0)
        s = self.client.get("/api/stats").get_json()
        self.assertEqual(s["total"], 2)
        self.assertEqual(sum(s["by_risk"].values()), 2)
        self.assertEqual(self.client.delete(f"/api/history/{a['id']}").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/history/{a['id']}").status_code, 404)
        self.assertEqual(self.client.get("/api/stats").get_json()["total"], 1)

    def test_sql_injection_is_inert(self):
        self.scan("url", "http://x.com/';DROP-TABLE-scans;--")
        self.assertEqual(self.client.get("/api/history?search=' OR 1=1 --").get_json()["total"], 0)
        self.assertEqual(self.client.get("/api/stats").get_json()["total"], 1)


if __name__ == "__main__":
    unittest.main()
