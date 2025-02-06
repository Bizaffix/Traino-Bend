import openai
import os
import time
from dotenv import load_dotenv

openai.api_base = "https://api.kluster.ai/v1"


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


openai.api_key = "c2d922dc-e340-4fc7-9b80-288bbe18775f" #openai_api_key  # Set your OpenAI API key


def generate_summary_from_gpt(content, prompt=None):
    """
    Summarize large content by chunking it, processing each chunk, and combining the summaries.
    Handles rate limitations with retries and backoff.
    
    Args:
        content (str): The full text to be summarized.
        prompt (str, optional): Custom prompt for GPT. Defaults to a concise summarization prompt.

    Returns:
        final_summary (str): The summarized output for the entire content.
        prompt (str): The prompt used for summarization.
    """
    try:
        # Default prompt if none is provided
        if not prompt:
            prompt = (
                "Summarize the following content in a concise, descriptive, and unique way. "
                "Focus on key points, maintain relevance, and ensure the summary is easy to understand:\n\n"
            )
        
        # Token limits
        max_input_tokens = 4000
        max_response_tokens = 500
        max_final_response_tokens = 3000
        chunk_size = max_input_tokens - len(prompt.split()) - 50  # Adjust for prompt and metadata

        # Split content into chunks
        chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

        # Function to make API calls with retry
        def call_openai_api(messages, max_tokens, retries=5, backoff_factor=2):
            for attempt in range(retries):
                try:
                    return openai.ChatCompletion.create(
                        model="deepseek-ai/DeepSeek-R1",
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=0.5,
                    )
                except openai.error.RateLimitError as e:
                    if attempt < retries - 1:
                        wait_time = 60
                        print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        print("Max retries reached. Rate limit error.")
                        raise e
                except Exception as e:
                    print(f"Error: {e}")
                    raise e

        # Summarize each chunk
        partial_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}...")  # Optional progress tracking
            try:
                response = call_openai_api(
                    messages=[
                        {"role": "system", "content": "You are a professional assistant specializing in summarizing content."},
                        {"role": "user", "content": f"{prompt}{chunk}"},
                    ],
                    max_tokens=max_response_tokens,
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
            final_response = call_openai_api(
                messages=[
                    {"role": "system", "content": "You are a professional assistant specializing in organizing summaries."},
                    {"role": "user", "content": f"{final_prompt}{combined_content}"},
                ],
                max_tokens=max_final_response_tokens,
            )
            final_summary = final_response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Error generating final summary: {e}")
            final_summary = " ".join(partial_summaries)  # Use raw concatenation as fallback

        return final_summary, prompt
    except Exception as e:
        print("Something is wrong with Summary Gen Func", e)



generate_summary_from_gpt("""### Job Title: React and Next.js Developer (Full-Time Remote)  

#### *About the Role*  
We are looking for a talented and experienced React and Next.js Developer to join our team! As a key contributor, you will work on modern web applications, utilizing the latest tools and technologies to deliver high-quality solutions. This is a full-time remote position, giving you the flexibility to work from anywhere while collaborating with a dynamic and passionate team.

---

#### *Key Responsibilities*  
- Develop, maintain, and optimize scalable web applications using *React* and *Next.js*.  
- Implement *Server Actions* for seamless server-side operations.  
- Design and manage databases using *Prisma* or *Drizzle* ORM tools.  
- Build and integrate robust and efficient *APIs*.  
- Create stunning, responsive, and user-friendly UIs using *TailwindCSS*.  
- Write clean, maintainable, and well-documented code following best practices.  
- Collaborate with designers, product managers, and other developers to deliver high-quality solutions.  
- Stay updated with the latest industry trends and technologies to continually improve the development process.  

---

#### *Skills and Qualifications*  
- *Proven experience* in developing applications with *React* and *Next.js*.  
- Solid understanding of *Server Actions* and server-side rendering (SSR).  
- Experience with *Prisma* or *Drizzle* for database management.  
- Strong proficiency in *API development* and integration.  
- Expertise in *TailwindCSS* for building responsive and visually appealing designs.  
- Familiarity with version control systems like *Git* and CI/CD pipelines.  
- Excellent problem-solving skills and a strong attention to detail.  
- Strong communication and collaboration skills to work effectively in a remote team environment.  

---

#### *Preferred Qualifications*  
- Experience with state management libraries like *Redux* or *Zustand*.  
- Knowledge of performance optimization techniques for React and Next.js applications.  
- Familiarity with authentication tools like *NextAuth.js* or *Auth0*.  
- Experience working with cloud platforms like *AWS, **Vercel, or **Firebase*.  
- Understanding of modern build tools like *Webpack* and *Vite*.  
- Experience in A.I applications.
---

#### *What We Offer*  
- *Full-time remote role* with a flexible schedule.  
- Competitive salary based on your skills and experience.  
- Opportunity to work on cutting-edge projects with a talented team.  
- Professional development and learning opportunities.  
- Collaborative and supportive work culture.  

---

If you are a skilled React and Next.js developer who thrives in a remote working environment and loves solving complex problems, we’d love to hear from you!  

📧 *How to Apply:*  
Send your resume to [your email address].  

Join us and help shape the future of web development! 🚀""")
