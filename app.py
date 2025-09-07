from flask import Flask, render_template, request, redirect, url_for
import csv, os
from datetime import datetime

app = Flask(__name__)

CSV_PATH = os.path.join("data", "expenses.csv")
os.makedirs("data", exist_ok=True)

HEADERS = ["date", "amount", "category", "note"]

def init_csv():
    # create file with header OR fix an empty file
    need_header = not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0
    if need_header:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)

def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return datetime.min  # push bad/missing dates to the bottom

def read_expenses():
    init_csv()
    rows = []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # If header is wrong, bail out gracefully
        if reader.fieldnames != HEADERS:
            # Optionally: rebuild file or just return empty until user fixes it
            return []
        for r in reader:
            try:
                r["amount"] = float((r.get("amount") or 0))
            except ValueError:
                r["amount"] = 0.0
            rows.append(r)
    rows.sort(key=lambda r: _parse_date(r.get("date", "")), reverse=True)
    return rows


def add_expense(date_str, amount, category, note):
    init_csv()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date_str, amount, category, note])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        date_str = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")
        amount_raw = (request.form.get("amount") or "").strip()
        category = (request.form.get("category") or "").strip() or "Other"
        note = (request.form.get("note") or "").strip()

        try:
            amt = round(float(amount_raw), 2)
        except (TypeError, ValueError):
            amt = 0.0

        try:
            date_str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            date_str = datetime.now().strftime("%Y-%m-%d")

        add_expense(date_str, amt, category, note)
        return redirect(url_for("index"))

    expenses = read_expenses()
    total = round(sum(e["amount"] for e in expenses), 2)
    return render_template("index.html", expenses=expenses, total=total)

if __name__ == "__main__":
    app.run(debug=True)
