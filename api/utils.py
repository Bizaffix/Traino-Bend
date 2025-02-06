import logging
from openai import OpenAI
import chardet
import pdfplumber
import os

logging.basicConfig(filename="app.log", level=logging.INFO)
logger = logging.getLogger(__name__)
from dotenv import load_dotenv

# openai.api_base = "https://api.kluster.ai/v1"


load_dotenv()


client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
)


def generate_summary_from_gpt(content, prompt=None):
    try:
        # Default prompt if none is provided
        if not prompt:
            prompt = (
                "Summarize the following content in a concise, descriptive, and unique way. "
                "Focus on key points, maintain relevance, and ensure the summary is easy to understand:\n\n"
            )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional assistant specializing in summarizing content.",
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
            raise ValueError("Empty response received from API")

        summary = response.choices[0].message.content.strip()

        return summary, prompt
    except Exception as e:
        logger.error(f"Error in generate_summary_from_gpt: {str(e)}")
        logger.error(f"Response type: {type(response)}")
        raise


# def generate_summary_from_gpt(content, prompt=None):
#     """
#     Summarize large content by chunking it, processing each chunk, and combining the summaries.
#     Handles rate limitations with retries and backoff.

#     Args:
#         content (str): The full text to be summarized.
#         prompt (str, optional): Custom prompt for GPT. Defaults to a concise summarization prompt.

#     Returns:
#         final_summary (str): The summarized output for the entire content.
#         prompt (str): The prompt used for summarization.
#     """
#     try:
#         # Default prompt if none is provided
#         if not prompt:
#             prompt = (
#                 "Summarize the following content in a concise, descriptive, and unique way. "
#                 "Focus on key points, maintain relevance, and ensure the summary is easy to understand:\n\n"
#             )

#         # Token limits
#         max_input_tokens = 4000
#         max_response_tokens = 500
#         max_final_response_tokens = 3000
#         chunk_size = max_input_tokens - len(prompt.split()) - 50  # Adjust for prompt and metadata

#         # Split content into chunks
#         chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

#         # Function to make API calls with retry
#         def call_openai_api(messages, max_tokens, retries=5, backoff_factor=2):
#             for attempt in range(retries):
#                 try:
#                     return openai.ChatCompletion.create(
#                         model="gpt-4-turbo",
#                         messages=messages,
#                         max_tokens=max_tokens,
#                         temperature=0.5,
#                     )
#                 except openai.error.RateLimitError as e:
#                     if attempt < retries - 1:
#                         wait_time = 60
#                         print(f"Rate limit hit. Retrying in {wait_time} seconds...")
#                         time.sleep(wait_time)
#                     else:
#                         print("Max retries reached. Rate limit error.")
#                         raise e
#                 except Exception as e:
#                     print(f"Error: {e}")
#                     raise e

#         # Summarize each chunk
#         partial_summaries = []
#         for i, chunk in enumerate(chunks):
#             print(f"Processing chunk {i + 1}/{len(chunks)}...")  # Optional progress tracking
#             try:
#                 response = call_openai_api(
#                     messages=[
#                         {"role": "system", "content": "You are a professional assistant specializing in summarizing content."},
#                         {"role": "user", "content": f"{prompt}{chunk}"},
#                     ],
#                     max_tokens=max_response_tokens,
#                 )
#                 summary = response["choices"][0]["message"]["content"].strip()
#                 partial_summaries.append(summary)
#             except Exception as e:
#                 print(f"Error processing chunk {i + 1}: {e}")
#                 partial_summaries.append("")  # Add an empty string for failed chunks

#         # Combine partial summaries into a final summary
#         combined_content = " ".join(partial_summaries)
#         final_prompt = (
#             "Combine the following summaries into a final cohesive and concise summary, avoiding repetition:\n\n"
#         )
#         try:
#             final_response = call_openai_api(
#                 messages=[
#                     {"role": "system", "content": "You are a professional assistant specializing in organizing summaries."},
#                     {"role": "user", "content": f"{final_prompt}{combined_content}"},
#                 ],
#                 max_tokens=max_final_response_tokens,
#             )
#             final_summary = final_response["choices"][0]["message"]["content"].strip()
#         except Exception as e:
#             print(f"Error generating final summary: {e}")
#             final_summary = " ".join(partial_summaries)  # Use raw concatenation as fallback

#         return final_summary, prompt
#     except Exception as e:
#         print("Something is wrong with Summary Gen Func", e)


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
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional assistant specializing in generating key points.",
                },
                {"role": "user", "content": f"{prompt}{content}"},
            ],
            stream=False,
            temperature=0.5,
        )
        final_keypoints = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating key points: {e}")
        raise

    return final_keypoints, prompt


def generate_quizes_from_gpt(content, max_questions=10, min_questions=5):
    """
    Generate quizzes in the form of multiple-choice questions from large content by chunking it
    and processing each chunk. Combines quizzes if the content is too large.

    Args:
        content (str): The full text to process for quiz generation.
        max_questions (int): Maximum number of questions per quiz. Default is 10.
        min_questions (int): Minimum number of questions per quiz. Default is 5.

    Returns:
        final_quiz (str): The generated quiz following the required format.
        prompt (str): The prompt used for quiz generation.
    """
    # Refined prompt for quiz generation

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
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional quiz generator.",
                },
                {"role": "user", "content": f"{prompt}{content}"},
            ],
            stream=False,
            temperature=0.5,
        )
        final_quiz = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating quizes: {e}")
        raise

    return final_quiz, prompt


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
