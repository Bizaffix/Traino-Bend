import openai
import os 
openai_api_key =  'sk-proj-9FtVgsRK5a0YMObo5yMhT3BlbkFJYxPy0J1KInGdltTTYtQM'#'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'
os.environ['OPENAI_API_KEY'] = 'sk-proj-9FtVgsRK5a0YMObo5yMhT3BlbkFJYxPy0J1KInGdltTTYtQM'#'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'

# Summary Generations from gpt
def generate_summary_from_gpt(content):
    # print(openai_api_key)
    # print(os.environ['OPENAI_API_KEY'])
    openai.api_key = openai_api_key
    prompt = f"You are the content creator , Provide me the descriptive, related and concise summary for: \n\n{content[:7500]}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000  # Adjust the max tokens based on the required summary length
    )
    summary = response.choices[0].message['content'].strip()
    return summary


# Key-Points Generations from gpt
def generate_keypoints_from_gpt(content):
    openai.api_key = openai_api_key
    prompt = f"You are the key-points generator , Provide me the keypoints in bollet-points, related to the : \n\n{content[:7500]}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000  # Adjust the max tokens based on the required summary length
    )
    summary = response.choices[0].message['content'].strip()
    return summary


# Quizes Generations from gpt
def generate_quizes_from_gpt(content):
    prompt = f"You are the teacher, Provide me the quizes with  mcqs options and also the label of the correct answer for this: \n\n{content[:7500]}"
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000  # Adjust the max tokens based on the required summary length
    )
    summary = response.choices[0].message['content'].strip()
    return summary
