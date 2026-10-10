import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the .env file
load_dotenv()

# Initialize the Groq client (ensure GROQ_API_KEY is in your .env file)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_hotel_summary(hotel_data):
    """
    Takes a dictionary of hotel data and generates a personalized
    summary email body using Groq's blazing-fast inference.
    """
    prompt = f"""
    You are an AI account manager at FUNNOW. 
    Write a short, professional email to the owner of {hotel_data["brandname"]}. 
    
    Last week's performance data:
    - Revenue: ${hotel_data["revenue"]}
    - Bookings (Orders): {hotel_data["Order"]}
    - System Assessment: {hotel_data["performance_status"]}
    
    Instructions:
    1. Write exactly 3 to 4 sentences summarizing this performance.
    2. Do not include a subject line or email headers (just the body).
    3. If their status is 'Needs Improvement', politely suggest they run a flash promotion on FUNNOW to boost visibility.
    4. If their status is 'Performing Well', congratulate them and encourage them to keep their weekend inventory open.
    5. Sign off as "FUNNOW Account Management Team".
    """

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional account manager for a hotel booking platform.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating summary for {hotel_data['brandname']}: {e}")
        return "Error generating AI summary."


# Quick test block
if __name__ == "__main__":
    mock_data = {
        "brandname": "Riverside Hotel",
        "revenue": 150000,
        "Order": 30,
        "performance_status": "Needs Improvement",
    }
    print(generate_hotel_summary(mock_data))
