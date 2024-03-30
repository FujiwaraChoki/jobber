import json


def get_chrome_config() -> dict:
    """
    Returns a dictionary with the chrome settings in them.

    :return: A dictionary with the chrome settings in them
    """
    return json.load(open("config.json"))["chrome"]


def get_indeed_settings() -> dict:
    """
    Returns a dictionary of the Indeed settings, such as the job and place query.

    :return: A dictionary with the Indeed settings
    """
    return json.load(open("config.json"))["indeed"]

def get_smtp_settings() -> dict:
    """
    Returns a dictionary of the SMTP settings, such as the email and password.

    :return: A dictionary with the SMTP settings
    """
    return json.load(open("config.json"))["smtp"]
