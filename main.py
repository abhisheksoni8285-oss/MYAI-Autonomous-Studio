import os
import subprocess
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Environment variables लोड करें
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
  raise ValueError("❌ Error: GEMINI_API_KEY .env फाइल में नहीं मिली!")

client = genai.Client(api_key=API_KEY)


def ask_gemini_safe(prompt, previous_code="", error_message=""):
  """503 और हाई डिमांड से निपटने के लिए मजबूत रीट्राय लॉजिक"""
  full_prompt = (
      "You are an expert autonomous Python coding agent. "
      "Write clean, non-interactive, executable Python code (do NOT use input() as it causes timeouts) based on this request: "
      f"{prompt}\n"
      "IMPORTANT: Output ONLY pure Python code. Do not include markdown ticks like ```python or ```."
  )

  if previous_code and error_message:
    full_prompt += f"\nPrevious Code:\n{previous_code}\nError:\n{error_message}\nFix it and ensure it runs automatically without user input."

  model_name = "gemini-3.8-flash"
  max_retries = 4
  delay = 3

  for attempt in range(1, max_retries + 1):
    try:
      print(f"📡 Connecting to Gemini API [{model_name}] (Attempt {attempt})...")
      response = client.models.generate_content(
          model=model_name,
          contents=full_prompt,
      )

      code = response.text.strip()
      if code.startswith("```python"):
        code = code[9:]
      if code.startswith("```"):
        code = code[3:]
      if code.endswith("```"):
        code = code[:-3]

      return code.strip()

    except Exception as e:
      print(f"⚠️ Server/API Error: {e}. Retrying in {delay} seconds...")
      time.sleep(delay)
      delay *= 2  # Exponential backoff

  raise RuntimeError(
      "❌ Failed to get response from Gemini API after multiple retries."
  )


def run_code(filename="generated_script.py"):
  """कोड को रन करना (टर्मिनल को हैंग होने से बचाने के लिए 5 सेकंड का टाइमआउट)"""
  try:
    result = subprocess.run(
        ["python3", filename], capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
      return True, result.stdout
    else:
      return False, result.stderr
  except subprocess.TimeoutExpired:
    return (
        False,
        "Script timed out (possibly waiting for input or running infinitely).",
    )
  except Exception as e:
    return False, str(e)


def run_autonomous_agent(user_prompt):
  """मुख्य एजेंट लूप"""
  print(f"\n🤖 [MYAI Agent] Task Received: '{user_prompt}'\n")

  file_name = "generated_script.py"
  current_code = ""
  error_msg = ""

  for attempt in range(1, 4):
    print(f"🔄 Execution Attempt {attempt}/3...")
    try:
      current_code = ask_gemini_safe(user_prompt, current_code, error_msg)
    except Exception as err:
      print(err)
      return

    with open(file_name, "w", encoding="utf-8") as f:
      f.write(current_code)

    print("⚡ Running Generated Code...")
    success, output = run_code(file_name)

    if success:
      print("\n✅ Task Successfully Completed!")
      print("----------------- Output -----------------")
      print(output if output.strip() else "Code executed successfully.")
      print("------------------------------------------")
      break
    else:
      print(f"❌ Execution Error:")
      print(f"--> {output.strip()}")
      error_msg = output
      print("🔧 Self-correcting & Retrying...\n")


if __name__ == "__main__":
  prompt = input("Enter what program you want the AI to write and execute: ")
  if prompt.strip():
    run_autonomous_agent(prompt)
  else:
    run_autonomous_agent(
        "Write a Python script to calculate Fibonacci numbers up to 10 terms"
        " and print them."
    )