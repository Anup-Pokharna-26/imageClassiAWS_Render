import google.generativeai as genai
import os
from PIL import Image
import json
import io

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyA2VaaQ_q1zlHbwI7RGa5TTOzFiVVfKX3E"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

def test_basic_gemini():
    """Test basic Gemini API functionality"""
    try:
        response = model.generate_content("Hello! Can you respond with a simple message?")
        print(f"✅ Basic test successful: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {str(e)}")
        return False

def test_json_response():
    """Test Gemini's ability to return JSON"""
    try:
        response = model.generate_content("""
        Please return a simple JSON array like this:
        [{"food": "apple", "confidence": 95}]
        
        Only return the JSON, no other text.
        """)
        print(f"✅ JSON test response: {response.text}")
        
        # Try to parse the JSON
        import re
        json_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
        if json_match:
            json_data = json.loads(json_match.group(0))
            print(f"✅ Successfully parsed JSON: {json_data}")
            return True
        else:
            print("❌ Could not find JSON in response")
            return False
    except Exception as e:
        print(f"❌ JSON test failed: {str(e)}")
        return False

def test_image_analysis():
    """Test image analysis with a simple colored image"""
    try:
        # Create a simple test image
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (200, 200), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), "APPLE", fill='white')
        
        # Save temporarily
        img.save("test_apple.png")
        
        # Test with Gemini
        response = model.generate_content([
            "What food items do you see in this image? Return as JSON: [{'food': 'item_name', 'confidence': number}]",
            img
        ])
        
        print(f"✅ Image analysis response: {response.text}")
        
        # Clean up
        os.remove("test_apple.png")
        return True
    except Exception as e:
        print(f"❌ Image analysis failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Integration...")
    print("=" * 50)
    
    test_basic_gemini()
    print()
    test_json_response()
    print()
    test_image_analysis()
    print()
    print("🔍 Check the outputs above to diagnose the issue!")
