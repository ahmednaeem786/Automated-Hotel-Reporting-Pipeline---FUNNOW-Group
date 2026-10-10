import os

import groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

client = (
    groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
    if os.getenv("GROQ_API_KEY")
    else None
)


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM client is not configured."""


class LLMInputError(ValueError):
    """Raised when hotel data is missing fields needed for the prompt."""


class LLMResponseError(RuntimeError):
    """Raised when the provider returns an unusable response."""


def generate_hotel_summary(hotel_data):
    """
    Takes a dictionary of hotel data and generates a personalized
    summary email body using Groq's blazing-fast inference.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise LLMConfigurationError(
            "GROQ_API_KEY is missing. Add it to the environment or .env file."
        )

    required_fields = {"brandname", "revenue", "Order", "performance_status"}
    missing_fields = required_fields.difference(hotel_data)
    if missing_fields:
        raise LLMInputError(
            "Hotel data is missing required fields: "
            f"{', '.join(sorted(missing_fields))}"
        )

    hotel_name = hotel_data["brandname"]
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
        if not response.choices or not response.choices[0].message.content:
            raise LLMResponseError("The LLM returned an empty summary.")
        return response.choices[0].message.content.strip()

    except groq.AuthenticationError as error:
        print(f"[LLM AUTHENTICATION ERROR] {hotel_name}: check GROQ_API_KEY ({error})")
    except groq.RateLimitError as error:
        print(f"[LLM RATE LIMIT] {hotel_name}: retry later ({error})")
    except (groq.APIConnectionError, groq.APITimeoutError) as error:
        print(f"[LLM CONNECTION ERROR] {hotel_name}: provider unavailable ({error})")
    except (groq.BadRequestError, groq.APIStatusError) as error:
        print(f"[LLM API ERROR] {hotel_name}: request was rejected ({error})")
    except groq.GroqError as error:
        print(f"[LLM PROVIDER ERROR] {hotel_name}: {error}")
    except LLMResponseError as error:
        print(f"[LLM RESPONSE ERROR] {hotel_name}: {error}")
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
        print(f"[LLM DATA ERROR] {hotel_name}: invalid hotel data ({error})")

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
