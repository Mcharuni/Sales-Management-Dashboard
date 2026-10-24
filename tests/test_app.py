import os, tempfile, unittest
import app as sales_app

class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(delete=False)
        self.temp.close()
        self.old_path = sales_app.DB_PATH
        sales_app.DB_PATH = self.temp.name
        sales_app.init_db()
        self.client = sales_app.app.test_client()
    def tearDown(self):
        sales_app.DB_PATH = self.old_path
        try: os.unlink(self.temp.name)
        except OSError: pass
    def test_home(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"SalesPulse", r.data)
    def test_health(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
    def test_dashboard(self):
        data = self.client.get("/api/dashboard").get_json()
        self.assertGreater(data["summary"]["orders"], 0)
    def test_create_and_delete(self):
        payload = {"order_date":"2026-09-01","customer":"Test Customer","product":"Test Product","category":"Other","region":"Central","quantity":2,"unit_price":100,"unit_cost":40,"payment_method":"UPI"}
        r = self.client.post("/api/sales", json=payload)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["profit"], 120)
        self.assertEqual(self.client.delete("/api/sales/"+str(r.get_json()["id"])).status_code, 200)
    def test_invalid_quantity(self):
        payload = {"order_date":"2026-09-01","customer":"Test","product":"Thing","category":"Other","region":"Central","quantity":0,"unit_price":10,"unit_cost":2,"payment_method":"UPI"}
        self.assertEqual(self.client.post("/api/sales", json=payload).status_code, 400)
    def test_export(self):
        self.assertIn("text/csv", self.client.get("/api/export").content_type)

if __name__ == "__main__":
    unittest.main()
