from flask import Flask, render_template, request, jsonify, Response
import sqlite3, os, csv, io
from datetime import datetime

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "sales.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, order_date TEXT NOT NULL, customer TEXT NOT NULL, product TEXT NOT NULL, category TEXT NOT NULL, region TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0), unit_price REAL NOT NULL CHECK(unit_price >= 0), unit_cost REAL NOT NULL CHECK(unit_cost >= 0), payment_method TEXT NOT NULL)")
        if conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0:
            rows = [
                ("2026-01-05","Aarav Sharma","Laptop Pro","Electronics","South",2,65000,51000,"UPI"),
                ("2026-01-09","Diya Reddy","Wireless Mouse","Accessories","South",5,900,420,"Card"),
                ("2026-01-15","Kabir Patel","Office Chair","Furniture","West",3,8500,5600,"Bank Transfer"),
                ("2026-02-02","Ananya Rao","Monitor 27-inch","Electronics","South",4,18000,13500,"Card"),
                ("2026-02-12","Ishaan Mehta","Desk Lamp","Home & Office","North",6,1200,650,"UPI"),
                ("2026-02-21","Meera Nair","Laptop Pro","Electronics","South",1,65000,51000,"Bank Transfer"),
                ("2026-03-04","Arjun Singh","Keyboard Mechanical","Accessories","North",4,3200,1900,"Card"),
                ("2026-03-11","Sara Khan","Office Chair","Furniture","East",2,8500,5600,"UPI"),
                ("2026-03-23","Vivaan Das","Monitor 27-inch","Electronics","East",3,18000,13500,"Card"),
                ("2026-04-06","Ira Joshi","Desk Lamp","Home & Office","West",8,1200,650,"UPI"),
                ("2026-04-14","Reyansh Gupta","Laptop Pro","Electronics","North",2,65000,51000,"Card"),
                ("2026-04-25","Aditi Iyer","Wireless Mouse","Accessories","South",10,900,420,"UPI"),
                ("2026-05-03","Krishna Roy","Office Chair","Furniture","West",5,8500,5600,"Bank Transfer"),
                ("2026-05-17","Myra Kapoor","Monitor 27-inch","Electronics","North",2,18000,13500,"Card"),
                ("2026-06-08","Dev Malhotra","Keyboard Mechanical","Accessories","East",7,3200,1900,"UPI"),
                ("2026-06-19","Kiara Bose","Laptop Pro","Electronics","South",1,65000,51000,"Card"),
                ("2026-07-07","Advik Verma","Desk Lamp","Home & Office","North",9,1200,650,"UPI"),
                ("2026-07-18","Navya Menon","Wireless Mouse","Accessories","West",12,900,420,"Card"),
                ("2026-08-02","Atharv Pillai","Monitor 27-inch","Electronics","East",2,18000,13500,"Bank Transfer"),
                ("2026-08-13","Saanvi Shah","Office Chair","Furniture","South",4,8500,5600,"UPI")
            ]
            conn.executemany("INSERT INTO sales (order_date,customer,product,category,region,quantity,unit_price,unit_cost,payment_method) VALUES (?,?,?,?,?,?,?,?,?)", rows)

def sale_dict(row):
    d = dict(row)
    d["revenue"] = round(d["quantity"] * d["unit_price"], 2)
    d["profit"] = round(d["quantity"] * (d["unit_price"] - d["unit_cost"]), 2)
    return d

@app.route("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "SalesPulse"})

@app.get("/api/sales")
def get_sales():
    sql = "SELECT * FROM sales WHERE 1=1"
    args = []
    search = request.args.get("search", "").strip()
    for key, clause in [("category", "category = ?"), ("region", "region = ?")]:
        value = request.args.get(key, "").strip()
        if value:
            sql += " AND " + clause
            args.append(value)
    if search:
        sql += " AND (customer LIKE ? OR product LIKE ? OR CAST(id AS TEXT) LIKE ?)"
        args.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    start, end = request.args.get("start", ""), request.args.get("end", "")
    if start:
        sql += " AND order_date >= ?"; args.append(start)
    if end:
        sql += " AND order_date <= ?"; args.append(end)
    sql += " ORDER BY order_date DESC, id DESC"
    with get_db() as conn:
        rows = conn.execute(sql, args).fetchall()
    return jsonify([sale_dict(r) for r in rows])

@app.get("/api/dashboard")
def dashboard():
    where, args = " WHERE 1=1", []
    start, end = request.args.get("start", ""), request.args.get("end", "")
    if start:
        where += " AND order_date >= ?"; args.append(start)
    if end:
        where += " AND order_date <= ?"; args.append(end)
    with get_db() as conn:
        summary = conn.execute("SELECT COUNT(*) orders, COALESCE(SUM(quantity),0) units, COALESCE(SUM(quantity*unit_price),0) revenue, COALESCE(SUM(quantity*unit_cost),0) cost FROM sales" + where, args).fetchone()
        monthly = conn.execute("SELECT substr(order_date,1,7) month, ROUND(SUM(quantity*unit_price),2) revenue, ROUND(SUM(quantity*(unit_price-unit_cost)),2) profit FROM sales" + where + " GROUP BY substr(order_date,1,7) ORDER BY month", args).fetchall()
        categories = conn.execute("SELECT category, ROUND(SUM(quantity*unit_price),2) revenue FROM sales" + where + " GROUP BY category ORDER BY revenue DESC", args).fetchall()
        regions = conn.execute("SELECT region, ROUND(SUM(quantity*unit_price),2) revenue FROM sales" + where + " GROUP BY region ORDER BY revenue DESC", args).fetchall()
        products = conn.execute("SELECT product, SUM(quantity) units, ROUND(SUM(quantity*unit_price),2) revenue FROM sales" + where + " GROUP BY product ORDER BY revenue DESC LIMIT 5", args).fetchall()
    revenue, cost, orders = float(summary["revenue"]), float(summary["cost"]), int(summary["orders"])
    return jsonify({"summary":{"orders":orders,"units":int(summary["units"]),"revenue":round(revenue,2),"profit":round(revenue-cost,2),"average_order_value":round(revenue/orders,2) if orders else 0,"profit_margin":round((revenue-cost)/revenue*100,2) if revenue else 0},"monthly":[dict(x) for x in monthly],"categories":[dict(x) for x in categories],"regions":[dict(x) for x in regions],"top_products":[dict(x) for x in products]})

def validate(data):
    required = ["order_date","customer","product","category","region","quantity","unit_price","unit_cost","payment_method"]
    if any(data.get(k) is None or str(data.get(k)).strip() == "" for k in required):
        return "All fields are required."
    try:
        datetime.strptime(str(data["order_date"]), "%Y-%m-%d")
        qty, price, cost = int(data["quantity"]), float(data["unit_price"]), float(data["unit_cost"])
        if qty <= 0 or price < 0 or cost < 0:
            return "Quantity must be positive; price and cost cannot be negative."
    except (ValueError, TypeError):
        return "Enter a valid date, whole-number quantity, price and cost."
    if len(str(data["customer"]).strip()) > 100 or len(str(data["product"]).strip()) > 100:
        return "Customer and product names must be 100 characters or fewer."
    return None

@app.post("/api/sales")
def create_sale():
    data = request.get_json(silent=True) or {}
    error = validate(data)
    if error: return jsonify({"error":error}), 400
    with get_db() as conn:
        cur = conn.execute("INSERT INTO sales (order_date,customer,product,category,region,quantity,unit_price,unit_cost,payment_method) VALUES (?,?,?,?,?,?,?,?,?)", (data["order_date"],data["customer"].strip(),data["product"].strip(),data["category"],data["region"],int(data["quantity"]),float(data["unit_price"]),float(data["unit_cost"]),data["payment_method"]))
        row = conn.execute("SELECT * FROM sales WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(sale_dict(row)), 201

@app.put("/api/sales/<int:sale_id>")
def update_sale(sale_id):
    data = request.get_json(silent=True) or {}
    error = validate(data)
    if error: return jsonify({"error":error}), 400
    with get_db() as conn:
        if not conn.execute("SELECT id FROM sales WHERE id=?", (sale_id,)).fetchone():
            return jsonify({"error":"Sale not found."}), 404
        conn.execute("UPDATE sales SET order_date=?,customer=?,product=?,category=?,region=?,quantity=?,unit_price=?,unit_cost=?,payment_method=? WHERE id=?", (data["order_date"],data["customer"].strip(),data["product"].strip(),data["category"],data["region"],int(data["quantity"]),float(data["unit_price"]),float(data["unit_cost"]),data["payment_method"],sale_id))
        row = conn.execute("SELECT * FROM sales WHERE id=?", (sale_id,)).fetchone()
    return jsonify(sale_dict(row))

@app.delete("/api/sales/<int:sale_id>")
def delete_sale(sale_id):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        if cur.rowcount == 0: return jsonify({"error":"Sale not found."}), 404
    return jsonify({"message":"Sale deleted successfully."})

@app.get("/api/export")
def export_csv():
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Order ID","Date","Customer","Product","Category","Region","Quantity","Unit Price","Unit Cost","Revenue","Profit","Payment Method"])
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM sales ORDER BY order_date DESC, id DESC").fetchall()
    for row in rows:
        d = sale_dict(row)
        writer.writerow([d["id"],d["order_date"],d["customer"],d["product"],d["category"],d["region"],d["quantity"],d["unit_price"],d["unit_cost"],d["revenue"],d["profit"],d["payment_method"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=sales-report.csv"})

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
