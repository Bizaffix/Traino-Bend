


from openai import OpenAI

client = OpenAI(
  api_key="c2d922dc-e340-4fc7-9b80-288bbe18775f",
  base_url="https://api.kluster.ai/v1"
)
# openai.api_key = openai_api_key  # Set your OpenAI API key

def generate_summary_from_gpt(content, prompt=None):
    """
    Summarize large content by chunking it, processing each chunk, and combining the summaries.
    Args:
        content (str): The full text to be summarized.
        prompt (str, optional): Custom prompt for GPT. Defaults to a concise summarization prompt.

    Returns:
        final_summary (str): The summarized output for the entire content.
        prompt (str): The prompt used for summarization.
    """
    # Default prompt if none is provided
    try:
        if not prompt:
            prompt = (
                "Summarize the following content in a concise, descriptive, and unique way. "
                "Focus on key points, maintain relevance, and ensure the summary is easy to understand:\n\n"
            )
        
        # Token limit for input per request (leave room for response tokens)
        max_input_tokens = 4000
        max_response_tokens = 500
        max_final_response_tokens = 3000
        chunk_size = max_input_tokens - len(prompt.split()) - 50  # Adjust for prompt and metadata

        # Split content into chunks
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

        # Summarize each chunk
        partial_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}...")  # Optional progress tracking
            try:
                response = client.ChatCompletion.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional assistant specializing in summarizing content."},
                        {"role": "user", "content": f"{prompt}{chunk}"},
                    ],
                    max_tokens=max_response_tokens,
                    temperature=0.5,  # Adjust temperature for balanced creativity
                )
                summary = response["choices"][0]["message"]["content"].strip()
                partial_summaries.append(summary)
            except Exception as e:
                print(f"Error processing chunk {i + 1}: {e}")
                partial_summaries.append("")  # Add an empty string for failed chunks

        # Combine partial summaries into a final summary
        combined_content = " ".join(partial_summaries)
        final_prompt = (
            "Combine the following summaries into a final cohesive and concise summary, avoiding repetition:\n\n"
        )
        try:
            final_response = client.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional assistant specializing in organizing summaries."},
                    {"role": "user", "content": f"{final_prompt}{combined_content}"},
                ],
                max_tokens=max_final_response_tokens,
                temperature=0.5,
            )
            final_summary = final_response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error generating final summary: {e}")
            final_summary = " ".join(partial_summaries)  # Use raw concatenation as fallback

        return final_summary, prompt
    except Exception as e:
        print("Something is wrong with Summary Gen Func",e)
