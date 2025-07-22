import os
from dotenv import load_dotenv
load_dotenv()
try:
    import google.generativeai as genai
except ImportError:
    print("google-generativeai package not installed. Run 'pip install google-generativeai'.")
    exit(1)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

long_input = (
    "My name is John Doe. I worked as a software engineer at Google from 2020 to 2022, "
    "where I led a team and improved system performance by 40%. I also interned at Facebook in 2019. "
    "I graduated from MIT in 2020 with a degree in Computer Science. My skills include Python, JavaScript, and machine learning. "
    "I speak English and Spanish. I enjoy hiking and photography."
)
prompt = f'''
You are an expert resume writer specializing in the JSON Resume format. Your task is to extract and fill as many fields as possible in the full JSON Resume structure from the user's input below. If a field is not present, leave it empty. Be as complete as possible.

USER INPUT:
"{long_input}"

Return ONLY a valid JSON object for the entire resume (no explanations, no markdown, no extra text).
'''

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    print("Gemini API response:", response.text)
except Exception as e:
    print("Gemini API call failed:", e) 