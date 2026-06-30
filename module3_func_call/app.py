import json
import os

from dotenv import load_dotenv
from groq import (
    Groq,
    APIConnectionError,
    APIStatusError,
    RateLimitError,
)

from tools import available_functions, tools


# Load environment variables
load_dotenv()

# Create the Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def create_chat_completion(messages):
    """
    Sends a chat completion request to the Groq API.
    """

    try:
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
        )

    except RateLimitError:
        raise Exception("Rate limit exceeded. Please try again later.")

    except APIConnectionError:
        raise Exception("Unable to connect to the AI service.")

    except APIStatusError as e:
        raise Exception(f"API Error ({e.status_code}): {e}")


def run_assistant(user_prompt: str):
    """
    Sends the user's prompt to the LLM, executes any requested tool,
    and returns the final response.
    """

    try:
        messages = [
            {
                "role": "user",
                "content": user_prompt,
            }
        ]

        # First API call
        response = create_chat_completion(messages)

        # If no tool is required, return the normal response
        if not response.choices[0].message.tool_calls:
            return response.choices[0].message.content

        # Extract tool information
        tool_call = response.choices[0].message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        # Execute the requested tool
        function_to_call = available_functions[function_name]
        result = function_to_call(**arguments)

        # Continue the conversation
        messages.append(response.choices[0].message)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
        )

        # Second API call
        final_response = create_chat_completion(messages)

        return final_response.choices[0].message.content

    except json.JSONDecodeError:
        return "Error: Invalid tool arguments received from the model."

    except KeyError:
        return f"Error: Unknown tool '{function_name}'."

    except TypeError as e:
        return f"Error: Invalid arguments for tool '{function_name}'. {e}"

    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    user_prompt = "How many leave days does Rahul have left?"

    response = run_assistant(user_prompt)

    print("\nFinal Response:")
    print(response)