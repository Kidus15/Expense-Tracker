from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import csv, os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # allow cross-origin during dev
CSV_PATH = os.path.join("data", "expenses.csv")
os.makedirs("data", exist_ok=True)
HEADERS = ["date", "amount", "category", "note"]

# initialize CSV file if not exists
def init_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)


# read all expenses from CSV
def read_expenses():
    init_csv()
    rows = []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try: r["amount"] = float(r["amount"]) # try to convert amount to float
            except: r["amount"] = 0.0 # default to 0.0 if conversion fails
            rows.append(r)
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows

# add a new expense to CSV
def add_expense(date_str, amount, category, note):
    init_csv()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([date_str, amount, category, note])

@app.get("/api/expenses") # app route for GET /api/expenses
# List all expenses as JSON
def api_list():
    data = read_expenses()
    total = round(sum(e["amount"] for e in data), 2)
    return jsonify({"expenses": data, "total": total})

@app.post("/api/expenses")
# Add a new expense via JSON payload
def api_add():
    payload = request.get_json(force=True) or {}
    date_str = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
    try: amt = round(float(payload.get("amount", 0)), 2)
    except: amt = 0.0
    category = (payload.get("category") or "Other").strip()
    note = (payload.get("note") or "").strip()
    add_expense(date_str, amt, category, note)
    return jsonify({"ok": True}), 201


if __name__ == "__main__":
    app.run(debug=True)
