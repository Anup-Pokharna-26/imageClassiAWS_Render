import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyA2VaaQ_q1zlHbwI7RGa5TTOzFiVVfKX3E"
genai.configure(api_key=GEMINI_API_KEY)

print("Available Gemini models:")
print("=" * 40)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ {m.name}")
            print(f"   Description: {m.description}")
            print(f"   Supports: {m.supported_generation_methods}")
            print()
except Exception as e:
    print(f"Error listing models: {e}")
