from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
import os
import json
import re
from PIL import Image
import io

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyA2VaaQ_q1zlHbwI7RGa5TTOzFiVVfKX3E')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test-gemini", methods=["GET"])
def test_gemini():
    """Test endpoint to verify Gemini API is working"""
    try:
        response = model.generate_content("Hello, can you respond with a simple JSON array like this: [{'test': 'success'}]")
        return jsonify({
            "status": "success", 
            "response": response.text,
            "api_key_configured": bool(GEMINI_API_KEY)
        })
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e),
            "api_key_configured": bool(GEMINI_API_KEY)
        }), 500

@app.route("/classify", methods=["POST"])
def classify():
    try:
        file = request.files["image"]
        if not file:
            return jsonify({"error": "No image file provided"}), 400
        
        # Read and process the image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Create a prompt for food identification with confidence
        prompt = """
        Look at this image and identify any food items you can see. 
        For each food item, provide the food name and a confidence score from 0-100.
        
        Return your answer as a JSON array like this:
        [{"food": "pizza", "confidence": 95}, {"food": "salad", "confidence": 80}]
        
        If you see food items, always return the JSON array. If no food is visible, return: []
        
        Examples of good responses:
        - [{"food": "burger", "confidence": 90}]
        - [{"food": "apple", "confidence": 95}, {"food": "orange", "confidence": 88}]
        - []
        """
        
        # Generate content using Gemini
        response = model.generate_content([prompt, image])
        
        if not response or not response.text:
            return jsonify({"error": "No response from Gemini API"}), 500
        
        print(f"DEBUG - Raw Gemini response: {response.text}")  # Debug line
            
        # Parse the JSON response
        try:
            # Clean the response text and extract JSON
            response_text = response.text.strip()
            print(f"DEBUG - Cleaned response: {response_text}")  # Debug line
            
            # Try to extract JSON array using regex (handle multiline JSON)
            json_match = re.search(r'\[\s*\{[^\]]*\}\s*\]', response_text, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
            
            if json_match:
                response_text = json_match.group(0)
                print(f"DEBUG - Extracted JSON: {response_text}")  # Debug line
            else:
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
            # Parse JSON
            food_results = json.loads(response_text.strip())
            
            # Validate the format
            if not isinstance(food_results, list):
                raise ValueError("Response is not a list")
                
            # Validate each item in the list
            validated_results = []
            for item in food_results:
                if isinstance(item, dict) and "food" in item and "confidence" in item:
                    # Ensure confidence is a number and within 0-100 range
                    confidence = max(0, min(100, float(item["confidence"])))
                    validated_results.append({
                        "food": str(item["food"]),
                        "confidence": round(confidence, 1)
                    })
                    
            return jsonify({"labels": validated_results})
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: try to extract food items from natural language response
            try:
                fallback_prompt = f"""
                The previous response was: {response.text}
                
                Convert this to the required JSON format:
                [
                    {{"food": "food_name", "confidence": confidence_percentage}}
                ]
                
                Only return the JSON array, no additional text.
                """
                
                fallback_response = model.generate_content(fallback_prompt)
                fallback_text = fallback_response.text.strip()
                
                # Clean and parse fallback response
                if fallback_text.startswith('```json'):
                    fallback_text = fallback_text[7:]
                if fallback_text.startswith('```'):
                    fallback_text = fallback_text[3:]
                if fallback_text.endswith('```'):
                    fallback_text = fallback_text[:-3]
                    
                food_results = json.loads(fallback_text.strip())
                
                validated_results = []
                for item in food_results:
                    if isinstance(item, dict) and "food" in item and "confidence" in item:
                        confidence = max(0, min(100, float(item["confidence"])))
                        validated_results.append({
                            "food": str(item["food"]),
                            "confidence": round(confidence, 1)
                        })
                        
                return jsonify({"labels": validated_results})
                
            except Exception:
                # Final fallback: return error with raw response
                return jsonify({
                    "error": "Could not parse Gemini response", 
                    "raw_response": response.text,
                    "labels": []
                }), 500
        
    except Exception as e:
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
