from flask import Flask, render_template, request, redirect, redirect, url_for
import csv, os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Path for storing CSV data
CSV_PATH = os.path.join("data", "expenses.csv")

# Ensure the "data" folder exists
os.makedirs("data", exist_ok=True)

#Column headers for CSV
HEADERS = ["date", "amount", "category", "note"]


# Initialize CSV file if it doesn't exist
def init_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode='w', newline='') as f:
            writer = csv,writer(f)
            writer.writerow(HEADERS)

#Read all expenses from CSV file
def read_expenses():
    init_csv() # make sure file exists
    rows = []
    with open(CSV_PATH, "r", newlinwe='', encoding = "utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Convert amount safely to float
            try:
                r["amount"] = float(r["amount"])
            except ValueError:
                r["amount"] = 0.0
            rows.append(r)

    # Sort by date descending
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows


# Add a new expense entry to the CSV file

def add_expense(date_str, amount, category, note):
    init_csv()  # make sure file exists
    with open(CSV_PATH, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date_str, amount, category, note])

# Main route (home page) - shows expenses and form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
    # Get data from form inputs
        date_str = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")
        amount = request.form.get("amount", "").strip()# Remove leading/trailing spaces
        category = request.form.get("category", "").strip() or "Other"
        note = request.form.get("note", "").strip()

        # Validate and parse amount
        try:
            amt = round(float(amount), 2)
        except:
            amt = 0.0

        # Normalize date format (YYYY-MM-DD)
        try:
            date_str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            date_str = datetime.now().strftime("%Y-%m-%d")

        add_expense(date_str, amt, category, note)

        return redirect(url_for("index"))

    # If GET request, load all the expenses

    expenses = read_expenses()
    total = round(sum(e["amount"] for e in expenses), 2)

    # Render the template with expenses and total
    return render_template("index.html", expenses=expenses, total=total)

# Run the app - in debug mode (auto reload on code changes)
if __name__ == "__main__":
    app.run(debug=True)


    





















