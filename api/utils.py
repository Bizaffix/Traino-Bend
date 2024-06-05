import logging
import openai
import os 
import chardet
import pdfplumber
openai_api_key =  'sk-proj-9FtVgsRK5a0YMObo5yMhT3BlbkFJYxPy0J1KInGdltTTYtQM'#'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'
os.environ['OPENAI_API_KEY'] = 'sk-proj-9FtVgsRK5a0YMObo5yMhT3BlbkFJYxPy0J1KInGdltTTYtQM'#'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'

logger = logging.getLogger(__name__)

# Summary Generations from gpt
def generate_summary_from_gpt(content):
    # print(openai_api_key)
    # print(os.environ['OPENAI_API_KEY'])
    openai.api_key = openai_api_key
    prompt = f"You are the content creator , Provide me the descriptive, related and concise and everytime unique summary for: \n\n{content[:7500]}"
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
    prompt = f"You are the key-points generator , Provide me the keypoints in bollet-points, related to the and everytime provide me unique keypoints : \n\n{content[:7500]}"
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
    openai.api_key = openai_api_key
    prompt = f"You are the teacher, Provide me the random number quizes with mcqs and each mcq contains the 4 options and also provide me the correct option as well by just labeling A , B ,C Or D for correct answer. Make sure everytime the quizes maybe changed and hard: \n\n{content[:7500]} \n. Please make sure in your response no extra and use less text exists in response neither in start nor in end and question must be as question , question: , options as A:, B:  "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000  # Adjust the max tokens based on the required summary length
    )
    quiz = response.choices[0].message['content'].strip()
    # Extracting individual questions from the generated text
    return quiz


def read_file_content(file):
    file_type = file.name.split('.')[-1].lower()
    if file_type == 'pdf':
        return read_pdf_content(file)
    elif file_type == 'txt':
        return read_text_file_content(file)
    else:
        logger.error("Unsupported file type.")
        return None
        
def read_pdf_content(file):
    try:
        pdf_content = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pdf_content.append(text)
        return "\n".join(pdf_content)
    except Exception as e:
        logger.error(f"Error reading PDF file: {e}")
        return None

def read_text_file_content(file):
    encodings = ['utf-8', 'latin-1']
    content = None

    for encoding in encodings:
        try:
            file.seek(0)  # Reset file pointer to the beginning
            content = file.read().decode(encoding)
            logger.info(f"Successfully decoded with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            logger.warning(f"Failed to decode with encoding: {encoding}")
            continue  # Try next encoding if decoding fails

    if content is None:
        file.seek(0)
        raw_data = file.read()
        detected_encoding = chardet.detect(raw_data)['encoding']
        try:
            content = raw_data.decode(detected_encoding)
            logger.info(f"Successfully decoded with detected encoding: {detected_encoding}")
        except Exception as e:
            logger.error(f"Failed to decode with detected encoding: {detected_encoding}, Error: {e}")

    if content is None:
        logger.error("Unable to decode file content with any encoding")
        
    return content