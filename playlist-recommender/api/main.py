from flask import Flask, request, jsonify, render_template_string
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

# HTML template string for Web UI
HOME_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Song Recommendation System</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        textarea {
            width: 100%;
            height: 120px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            margin-bottom: 15px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
        }
        button:hover {
            background-color: #2980b9;
        }
        #results {
            margin-top: 20px;
            padding: 15px;
            border-top: 1px solid #eee;
        }
        .recommended-songs {
            list-style-type: none;
            padding: 0;
        }
        .recommended-songs li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #7f8c8d;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .error {
            color: #e74c3c;
            padding: 10px;
            background-color: #fadbd8;
            border-radius: 4px;
            margin-top: 15px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Song Recommendation System</h1>
        
        <div>
            <label for="songs">Enter songs you like (one song per line):</label>
            <textarea id="songs" placeholder="Lady Gaga - Bad Romance&#10;The Weeknd - Blinding Lights&#10;Dua Lipa - Don't Start Now"></textarea>
            
            <button id="recommend-btn">Get Recommendations</button>
            
            <div class="loading" id="loading">Processing...</div>
            <div class="error" id="error"></div>
            
            <div id="results" style="display:none;">
                <h3>Recommended Songs:</h3>
                <ul class="recommended-songs" id="recommendations"></ul>
                <p><small>Model Version: <span id="model-version">{{ version }}</span></small></p>
            </div>
        </div>
        
        <div class="footer">
            <p>Using Rule-Based Collaborative Filtering | Model Date: {{ model_date }}</p>
        </div>
    </div>
    
    <script>
        document.getElementById('recommend-btn').addEventListener('click', function() {
            const songsText = document.getElementById('songs').value;
            if (!songsText.trim()) {
                showError('Please enter at least one song');
                return;
            }
            
            // Get list of input songs
            const songsList = songsText.split('\\n')
                .map(song => song.trim())
                .filter(song => song.length > 0);
            
            if (songsList.length === 0) {
                showError('Please enter at least one valid song');
                return;
            }
            
            // Show loading state
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            
            // Call API to get recommendations
            fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ songs: songsList })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network error, please try again later');
                }
                return response.json();
            })
            .then(data => {
                // Hide loading state
                document.getElementById('loading').style.display = 'none';
                
                // Show recommendation results
                const recommendationsList = document.getElementById('recommendations');
                recommendationsList.innerHTML = '';
                
                if (data.songs && data.songs.length > 0) {
                    data.songs.forEach(song => {
                        const li = document.createElement('li');
                        li.textContent = song;
                        recommendationsList.appendChild(li);
                    });
                } else {
                    const li = document.createElement('li');
                    li.textContent = 'No matching recommendations found';
                    recommendationsList.appendChild(li);
                }
                
                // Update model version
                document.getElementById('model-version').textContent = data.version;
                
                // Show results area
                document.getElementById('results').style.display = 'block';
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                showError(error.message);
            });
        });
        
        function showError(message) {
            const errorElement = document.getElementById('error');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_PAGE, version=MODEL_VERSION, model_date=MODEL_DATE)

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

