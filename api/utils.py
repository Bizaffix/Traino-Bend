import logging
from openai import OpenAI
import chardet
import pdfplumber
import os
from google import genai


logging.basicConfig(filename="app.log", level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv

# openai.api_base = "https://api.kluster.ai/v1"


load_dotenv()


def call_model(prompt, content, model, system_mssg):
    if model == "deepseek-chat":
        client = genai.Client(api_key="AIzaSyDz_MvESKjQtYKoeUHJISfhpWFqHQdODCg")
    else:
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com"
        )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_mssg,
                },
                {"role": "user", "content": f"{prompt}{content}"},
            ],
            stream=False,
            temperature=0.5,
        )

        # Add debug logging
        logger.info(f"API Response: {response}")

        # Check if response is None or empty
        if not response:
            raise ValueError(f"Empty response received from {model} API")

        summary = response.text.strip()

        return summary, prompt
    except Exception as e:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"You are a professional assistant specializing in summarizing content. \n\n Summarize the following content in a concise, descriptive, and unique way. {content}",
            )

            # Add debug logging
            logger.info(f"API Response: {response}")

            # Check if response is None or empty
            if not response:
                raise ValueError(f"Empty response received from {model} API")

            summary = response.text.strip()

            return summary, prompt

        except Exception as e:
            logger.error(f"Error in calling {model} with prompt:{prompt} :\n {str(e)}")
            logger.error(f"Response type: {type(response)}")
            raise


def generate_summary_from_gpt(content, prompt=None):
    # Default prompt if none is provided
    if not prompt:
        prompt = (
            "Summarize the following content in a concise, descriptive, and unique way. "
            "Focus on key points, maintain relevance, and ensure the summary is easy to understand:\n\n"
        )

    try:
        return call_model(
            prompt,
            content,
            "deepseek-chat",
            "You are a professional assistant specializing in summarizing content.",
        )
    except Exception as e:
        print("Error with Generating Summary ", e)
        raise


def generate_keypoints_from_gpt(content, prompt=None):
    """
    Generate key points from large content by chunking it, processing each chunk,
    and combining the key points into a final cohesive list.

    Args:
        content (str): The full text to process for key points.
        prompt (str, optional): Custom prompt for GPT. Defaults to a detailed prompt.

    Returns:
        final_keypoints (str): The generated key points as bullet points.
        prompt (str): The prompt used for key point generation.
    """
    # Default prompt if none is provided
    if not prompt:
        prompt = (
            "Extract key points from the following content. Present them as bullet points "
            "that are concise, relevant, and unique. Focus on capturing critical ideas, "
            "actionable insights, and important highlights. Avoid repetition and ensure clarity:\n\n"
        )

    try:
        return call_model(
            prompt,
            content,
            "deepseek-chat",
            "You are a professional assistant specializing in generating key points.",
        )
    except Exception as e:
        print("Error with Generating Summary ", e)
        raise


def generate_quizes_from_gpt(content, max_questions=10, min_questions=5):

    prompt = (
        f"You are a teacher creating quizzes. Provide a quiz with a maximum of {max_questions} "
        f"questions and a minimum of {min_questions} questions, each containing 4 options as MCQs. "
        "Indicate the correct option by labeling it A, B, C, or D and answer as 'Correct Answer'. "
        "Ensure the quizzes are unique, challenging, and directly derived from the content. "
        "Strictly follow this format:\n\n"
        "Question: [Write the question here]\n"
        "A: [Option A]\n"
        "B: [Option B]\n"
        "C: [Option C]\n"
        "D: [Option D]\n"
        "Correct Answer: [Correct option (A, B, C, or D)]\n\n"
        "No extra text, no new lines between the 'Question:' and the question text. "
        "Generate the quiz only from the following content:\n\n"
    )

    try:
        return call_model(
            prompt,
            content,
            "deepseek-chat",
            "You are a professional quiz generator.",
        )
    except Exception as e:
        print("Error with Generating Summary ", e)
        raise


def read_file_content(file):
    file_type = file.name.split(".")[-1].lower()
    if file_type == "pdf":
        return read_pdf_content(file)
    elif file_type == "txt":
        return read_text_file_content(file)
    else:
        logger.error("Unsupported file type.")
        return None


def read_pdf_content(file):
    try:
        max_pages = 100
        pdf_content = []
        with pdfplumber.open(file) as pdf:
            for i, page in enumerate(pdf.pages):
                # print(i)
                if i >= max_pages:
                    break
                text = page.extract_text()
                if text:
                    pdf_content.append(text)
        return "\n".join(pdf_content)
    except Exception as e:
        logger.error(f"Error reading PDF file: {e}")
        return None


# pushing


def read_text_file_content(file):
    encodings = ["utf-8", "latin-1"]
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
        detected_encoding = chardet.detect(raw_data)["encoding"]
        try:
            content = raw_data.decode(detected_encoding)
            logger.info(
                f"Successfully decoded with detected encoding: {detected_encoding}"
            )
        except Exception as e:
            logger.error(
                f"Failed to decode with detected encoding: {detected_encoding}, Error: {e}"
            )

    if content is None:
        logger.error("Unable to decode file content with any encoding")

    return content
