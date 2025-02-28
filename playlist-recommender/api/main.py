from flask import Flask, request, jsonify
import pickle
import os
from datetime import datetime

def get_recommendations(input_songs, rules, top_n=5):
    # Convert input list to a set for subset testing
    input_set = set(input_songs)
    recommendations = set()
    # Iterate over each rule row in the DataFrame
    for _, rule in rules.iterrows():
        # The antecedents in the rule are stored as a frozenset
        if rule['antecedents'].issubset(input_set):
            recommendations.update(rule['consequents'])
    # Return up to top_n recommendations
    return list(recommendations)[:top_n]


app = Flask(__name__)

# Set environment variables or use defaults
MODEL_PATH = os.getenv("MODEL_PATH", "/model/model.pickle")
MODEL_VERSION = os.getenv("MODEL_VERSION", "0.1")

def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

# Load the model at startup
app.model = load_model()
MODEL_DATE = datetime.now().isoformat()

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json(force=True)
    user_songs = data.get("songs", [])
    
    # Generate recommendations using the function defined earlier
    recommendations = get_recommendations(user_songs, app.model)
    
    return jsonify({
        "songs": recommendations,
        "version": MODEL_VERSION,
        "model_date": MODEL_DATE
    })

@app.route('/api/debug', methods=['GET'])
def debug_model():
    # Get sample of the model
    sample_rules = []
    try:
        for i, (_, rule) in enumerate(app.model.iterrows()):
            if i >= 5:  # Just sample 5 rules
                break
            sample_rules.append({
                "antecedents": list(rule['antecedents']),
                "consequents": list(rule['consequents']),
                "confidence": float(rule['confidence'])
            })
    except Exception as e:
        return jsonify({"error": str(e)})
        
    return jsonify({
        "rules_count": len(app.model),
        "sample_rules": sample_rules,
        "version": MODEL_VERSION
    })

if __name__ == '__main__':
    # Ensure Flask listens on all interfaces
    app.run(host='0.0.0.0', port=5000)

