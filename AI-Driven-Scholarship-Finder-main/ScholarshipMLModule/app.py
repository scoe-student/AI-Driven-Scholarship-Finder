from flask import Flask, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

df = joblib.load("scholarship_rules.pkl")
df.columns = df.columns.str.strip()
scholarships = df

print("COLUMNS:", scholarships.columns.tolist())

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        gpa = float(data.get("gpa", 0))
        income = int(data.get("income", 9999999))
        category = data.get("category", "").lower()
        gender = data.get("gender", "").lower()
        region = data.get("region", "").lower()

        def is_eligible(row):
            gpa_required = row.get("GPA Required", "")
            income_limit = row.get("Family Income (LPA)", "")
            cat = str(row.get("Category Eligibility", "")).strip().lower()
            elig = str(row.get("Gender Eligibility", "")).strip().lower()

            if isinstance(gpa_required, str) and ">" in gpa_required:
                try:
                    if not gpa > float(gpa_required.replace(">", "").strip()): return False
                except: return False
            elif isinstance(gpa_required, str) and ">=" in gpa_required:
                try:
                    if not gpa >= float(gpa_required.replace(">=", "").strip()): return False
                except: return False
            elif isinstance(gpa_required, str) and gpa_required.replace(".", "").isdigit():
                try:
                    if not gpa >= float(gpa_required): return False
                except: return False

            if isinstance(income_limit, str) and "<" in income_limit:
                try:
                    if not income < int(income_limit.replace("<", "").replace("=", "").strip()): return False
                except: return False
            elif isinstance(income_limit, str) and "<=" in income_limit:
                try:
                    if not income <= int(income_limit.replace("<=", "").strip()): return False
                except: return False

            if cat != "all" and cat != category: return False
            if elig != "all" and elig != gender: return False

            if "j & k" in str(row.get("Scholarship Name", "")).lower():
                if "j&k" not in region and "jammu" not in region: return False

            return True

        matches = scholarships[scholarships.apply(is_eligible, axis=1)]
        return jsonify({"eligible_scholarships": matches.to_dict(orient="records")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
