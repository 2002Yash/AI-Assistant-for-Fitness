
from dotenv import load_dotenv
import requests
from typing import Optional
import json
import os

load_dotenv()

BASE_API_URL = "http://127.0.0.1:7860" # Or your Langflow API URL
ASK_AI_FLOW_ID = "" 
MACRO_FLOW_ID = ""
APPLICATION_TOKEN = os.getenv("LANGFLOW_TOKEN")

def dict_to_string(obj, level=0):
    strings = []
    indent = "  " * level
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                nested_string = dict_to_string(value, level + 1)
                strings.append(f"{indent}{key}: {nested_string}")
            else:
                strings.append(f"{indent}{key}: {value}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            nested_string = dict_to_string(item, level + 1)
            strings.append(f"{indent}Item {idx + 1}: {nested_string}")
    else:
        strings.append(f"{indent}{obj}")

    return ", ".join(strings)


def ask_ai(profile, question):
    TWEAKS = {
        "TextInput-ArZs2": { 
            "input_value": question
        },
        "TextInput-Y6n6S": {
            "input_value": dict_to_string(profile)
        },
    }
    result = run_flow(flow_id=ASK_AI_FLOW_ID, message=question, tweaks=TWEAKS, application_token=APPLICATION_TOKEN)
    return result


def get_macros(profile, goals):
    TWEAKS = {
        "TextInput-QYrvG": { 
            "input_value": ", ".join(goals)
        },
        "TextInput-lhxcK": {
            "input_value": dict_to_string(profile)
        }
    }
    api_response_text = run_flow(flow_id=MACRO_FLOW_ID, message="", tweaks=TWEAKS, application_token=APPLICATION_TOKEN)
    return json.loads(api_response_text)


def run_flow(flow_id: str,
  message: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  application_token: Optional[str] = None) -> str:
    api_url = f"{BASE_API_URL}/api/v1/run/{flow_id}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}
    
    response = requests.post(api_url, json=payload, headers=headers)
    response_json = response.json()
    
    # THE FINAL FIX IS HERE:
    # We loop through the final outputs and take the first one with actual text.
    try:
        final_outputs = response_json["outputs"][0]["outputs"]
        for output in final_outputs:
            # Check for both possible structures, "message" or "text" keys
            if "message" in output["results"]:
                result_text = output["results"]["message"]["data"]["text"]
                if result_text:
                    return result_text
            elif "text" in output["results"]:
                result_text = output["results"]["text"]["data"]["text"]
                if result_text:
                    return result_text
        return "Error: The workflow ran, but all final outputs were empty."

    except (KeyError, IndexError) as e:
        print(f"Error parsing response: {e}")
        return "Error: Could not parse the output from the workflow."
