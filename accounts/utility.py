import logging
import random

import requests


def send_otp(phone_number):
    otp = random.randint(100000, 999999)
    message = f"Your OTP is {otp}"
    try:
        url = f"https://2factor.in/API/V1/a2f2dd7d-2b67-11ed-9c12-0200cd936042/SMS/{phone_number}/{otp}/OTP1"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data["Status"] == "Success":
            return otp
        else:
            logging.error(
                f"Failed to send OTP: {data.get('Details', 'No details provided')}"
            )
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending OTP to {phone_number}: {e}")
        return None
