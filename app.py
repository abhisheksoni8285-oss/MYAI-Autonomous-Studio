import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai

# .env से API Key लोड करें
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
client = genai.Client(api_key=API_KEY)

# जेनरेटेड ऐप को सेव करने की जगह
OUTPUT_FILE = "static/preview.html"


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
  data = request.json
  prompt = data.get("prompt", "")

  if not prompt:
    return jsonify({"success": False, "error": "Prompt is empty!"})

  full_prompt = (
      "You are an expert full-stack web developer and autonomous coding agent. "
      "Create a single, fully functional, beautifully styled responsive HTML page "
      "incorporating HTML, CSS (Tailwind or modern internal CSS), and JavaScript based on this request: "
      f"{prompt}\n"
      "IMPORTANT: Output ONLY pure HTML code containing all styles and scripts. "
      "Do not wrap the output in markdown block ticks like ```html or ```."
  )

  try:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=full_prompt,
    )

    code = response.text.strip()
    # Markdown हटाने का लॉजिक
    if code.startswith("```html"):
      code = code[7:]
    if code.startswith("```"):
      code = code[3:]
    if code.endswith("```"):
      code = code[:-3]

    # static फोल्डर सुनिश्चित करें
    os.makedirs("static", exist_ok=True)

    # फ़ाइल सेव करें ताकि दाईं तरफ लाइव प्रीव्यू दिखे
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
      f.write(code.strip())

    return jsonify({"success": True, "preview_url": "/static/preview.html"})

  except Exception as e:
    return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
  print("🚀 Starting Web UI Agent Server...")
  app.run(debug=True, port=5000)