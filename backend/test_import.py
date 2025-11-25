import google.generativeai as genai

# Configure your API key (replace with your actual API key or set as an environment variable)
genai.configure(api_key="") 

print("List of available models:")
for m in genai.list_models():
    print(f"{m.name}")
    # print("-" * 20)