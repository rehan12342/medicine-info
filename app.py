from flask import Flask, render_template, request, session, jsonify
import requests
import urllib.parse
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Load local 200 medicines dataset
with open("data/medicines_dataset.json") as f:
    medicine_data = json.load(f)

# Load health quotes
with open("data/quotes.json") as f:
    health_quotes = json.load(f)

# FDA API
def get_medicine_info_openfda(medicine_name):
    base_url = "https://api.fda.gov/drug/label.json"
    query_medicine = urllib.parse.quote(f'"{medicine_name}"')
    limit = 3

    def fetch_data(search_field):
        url = f"{base_url}?search={search_field}:{query_medicine}&limit={limit}"
        try:
            res = requests.get(url)
            if res.status_code != 200:
                return None
            return res.json().get("results")
        except:
            return None

    results = fetch_data("generic_name") or fetch_data("openfda.brand_name")
    if not results:
        return {
            "purpose": "Data not found",
            "dosage": "Data not found",
            "side_effects": "Data not found",
            "precautions": "Data not found",
            "image": f"https://source.unsplash.com/160x160/?{urllib.parse.quote(medicine_name + ' medicine')}"
        }

    result = results[0]
    return {
        "purpose": "; ".join(result.get("indications_and_usage", []) or ["Data not found"]),
        "dosage": "; ".join(result.get("dosage_and_administration", []) or ["Data not found"]),
        "side_effects": "; ".join(result.get("adverse_reactions", []) or ["Data not found"]),
        "precautions": "; ".join(result.get("precautions", []) or result.get("warnings", []) or ["Data not found"]),
        "image": f"https://source.unsplash.com/160x160/?{urllib.parse.quote(medicine_name + ' medicine')}"
    }

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    medicine_info = None
    if request.method == "POST":
        name = request.form.get("medicine_name", "").strip()
        if name:
            medicine_info = get_medicine_info_openfda(name)
            session.setdefault("history", [])
            if name not in session["history"]:
                session["history"] = [name] + session["history"][:4]
    return render_template("search.html", medicine_info=medicine_info, history=session.get("history", []))

@app.route("/info")
def info():
    return render_template("info.html", medicines=medicine_data)

@app.route("/quotes")
def quotes():
    return render_template("quotes.html", quotes=health_quotes)

if __name__ == "__main__":
    app.run(debug=True)
