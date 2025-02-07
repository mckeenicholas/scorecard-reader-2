from dotenv import load_dotenv
import google.generativeai as genai
import base64
import cv2
import os
import re
import json

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")


def format_response_json(response):
    start_trimmed = re.sub("```json", "", response.strip())
    end_trimmed = re.sub("```", "", start_trimmed)

    print(end_trimmed.strip())

    return json.loads(end_trimmed.strip())


def convert_to_centiseconds(time):
    if time is None:
        return 0

    if time == "DNF":
        return -1

    try:
        if ":" in time:
            # Split the input into minutes and seconds.milliseconds
            minutes, seconds_milliseconds = time.split(":")
            # Convert minutes to seconds
            time_in_seconds = int(minutes) * 60 + float(seconds_milliseconds)
        else:
            time_in_seconds = float(time)

        # Convert to centiseconds (truncate after the 2nd decimal)
        centiseconds = int(time_in_seconds * 100)
    except:
        return 0

    return centiseconds


def scan_image(images):
    # Convert images to base64
    image_parts = []
    for image in images:
        success, encoded_image = cv2.imencode(".png", image)
        if not success:
            raise ValueError("Failed to encode image")

        base64_image = base64.b64encode(encoded_image).decode("utf-8")
        image_parts.append({"mime_type": "image/png", "data": base64_image})

    # Create the prompt
    prompt = "Could you tell me what is written down for each result in this image? Each one conains either a time, or 'DNF' Respond in JSON only in the form [{ 1: string, 2: string, ...}], respond with 'null' for unreadable times"

    print("sent to model")

    # Generate content with both images and prompt
    response = model.generate_content(contents=[*image_parts, prompt])

    response_text = format_response_json(response.text)

    formatted_responses = []

    for average in response_text:
        results = {}
        for idx, time in average.items():
            results[idx] = convert_to_centiseconds(time)

        formatted_responses.append(results)

    return formatted_responses
