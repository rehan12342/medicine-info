from flask import Flask, render_template, request, session
import requests
import urllib.parse

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

def get_medicine_info_openfda(medicine_name):
    base_url = "https://api.fda.gov/drug/label.json"
    query_medicine = urllib.parse.quote(f'"{medicine_name}"')
    limit = 3

    def fetch_data(search_field):
        query = f"search={search_field}:{query_medicine}&limit={limit}"
        url = f"{base_url}?{query}"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return None
            data = response.json()
            return data.get("results")
        except:
            return None

    # Try generic_name first
    results = fetch_data("generic_name")

    # If no results, try brand_name
    if not results:
        results = fetch_data("openfda.brand_name")

    if not results:
        return {
            "purpose": "Data not found",
            "dosage": "Data not found",
            "side_effects": "Data not found",
            "precautions": "Data not found",
            "image": f"https://source.unsplash.com/160x160/?{urllib.parse.quote(medicine_name + ' medicine')}"
        }

    for result in results:
        purpose = "; ".join(result.get("indications_and_usage", [])) or "Data not found"
        dosage = "; ".join(result.get("dosage_and_administration", [])) or "Data not found"
        side_effects = "; ".join(result.get("adverse_reactions", [])) or "Data not found"
        precautions = result.get("precautions", []) or \
                      result.get("precautions_and_warnings", []) or \
                      result.get("warnings", []) or ["Data not found"]
        precautions = "; ".join(precautions)

        if any(field != "Data not found" for field in [purpose, dosage, side_effects, precautions]):
            return {
                "purpose": purpose,
                "dosage": dosage,
                "side_effects": side_effects,
                "precautions": precautions,
                "image": f"https://source.unsplash.com/160x160/?{urllib.parse.quote(medicine_name + ' medicine')}"
            }

    # Fallback to first result
    first = results[0]
    return {
        "purpose": purpose,
        "dosage": dosage,
        "side_effects": side_effects,
        "precautions": precautions,
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Tablet_icon.svg/200px-Tablet_icon.svg.png"
    }


@app.route("/", methods=["GET", "POST"])
def index():
    medicine_info = None
    if request.method == "POST":
        medicine_name = request.form.get("medicine_name")
        if medicine_name:
            medicine_info = get_medicine_info_openfda(medicine_name.strip())

            if 'history' not in session:
                session['history'] = []

            if medicine_name not in session['history']:
                session['history'] = [medicine_name] + session['history'][:4]

    return render_template("index.html", medicine_info=medicine_info, history=session.get('history', []))

if __name__ == "__main__":
    app.run(debug=True)