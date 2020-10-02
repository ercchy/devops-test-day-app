"""
This script calls weather report and weather control API and changes the temperature for one degree,
if the temperature is higher than 20 degrees.

Note: It changes the temperature only once. Once the temperature was changed we are not able to
change it again. Why? Well it's hard to undo the last 100 years.

To run you will need to `pip install requests`

"""
import logging
import random
import json

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:3000"
RETRIES = 5


class ValidationError(Exception):
    pass


class ErrorWithResponse(Exception):
    def __init__(self, message, response):
        self.message = message
        self.response = response


class APIError(ErrorWithResponse):
    pass


def validate_response(response):
    error_suffix = " response={!r}".format(response)
    if response.status_code in (401, 403):
        raise APIError("operation=auth_error," + error_suffix, response)
    if response.status_code == 404:
        raise APIError("operation=not_found_error," + error_suffix, response)
    if 400 <= response.status_code <= 499:
        raise APIError("operation=client_error," + error_suffix, response)
    if 500 <= response.status_code <= 599:
        raise APIError("operation=server_error," + error_suffix, response)
    return response


def requests_retry_session(retries=RETRIES, backoff_factor=0.3,
                           status_forcelist=(500, 502, 504),
                           session=None):
    # Reference: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    # Documentatin for Retry class: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry

    """
    The method will try hitting the requested url for how much retries we
    define in the constants file.
    Between the retries it will wait for `backoff_factor`, which will exponentially grow
    with the number of retries.

    :param retries: Defined in the constants
    :param backoff_factor: A backoff factor to apply between attempts after the second try
    :param status_forcelist: A set of integer HTTP status codes that we should force a retry on
    :param session: You can pass an alredy alive session
    :return: session
    """

    if not session:
        session = requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def make_request(url, action=None, data=None):
    headers = {
        'Content-Type': 'application/json'
    }

    # Make sure action is written in upper letters
    action = action.upper()

    # raise error if type of request is set wrongly
    if action not in ("GET", "PATCH", "PUT"):
        logger.error(f"The type of request is not valid ({action})")
        raise ValidationError(f"The type of request is not valid ({action})")

    if action == "GET":
        logger.info(f"sending GET request to: {url}")
        # handle possible errors
        try:
            response = requests_retry_session().get(url, headers=headers)
            # response = requests.request("GET", url, headers=headers)
        except Exception as x:
            logger.error('GET request to the api failed: '.format(x.__class__.__name__))
        else:
            logger.info('GET request to the api was successful.')
            return response

    if action == "PATCH":
        logger.info(f"sending {action} request to: {url}")

        # handle possible errors
        try:
            response = requests_retry_session().patch(url, headers=headers, data=data)
            # response = requests.request("PATCH", url, headers=headers, data=data)
        except Exception as x:
            logger.error(f"{action} request to the api failed: {x.__class__.__name__}")
        else:
            logger.info(f"{action} request to the api was successful.")
            return response


def update_temperature(report_id, new_temperature):
    url = f"{BASE_URL}/weather_reports/{report_id}"
    response = None

    descriptions = ["tornados", "floods", ""]

    payload = {
        "weather_report": {
            "temperature": new_temperature,
            "description": random.choice(descriptions)
        }
    }

    try:
        response = make_request(url, action="PATCH", data=json.dumps(payload))
    except Exception as e:
        logger.error(f"Could not get locations: {e}")

    try:
        response = validate_response(response)
    except APIError as e:
        logger.error(f"could not validate response {response.status_code}")

    return json.loads(response.text)


def get_locations():
    # build the URL
    url = f"{BASE_URL}/locations"

    response = None

    try:
        response = make_request(url, action="GET")
    except Exception as e:
        logger.error(f"Could not get locations: {e}")

    response = validate_response(response)
    return json.loads(response.text)


def get_reports_for_location(location):
    # build the URL
    url = f"{BASE_URL}/weather_reports?location={location}"
    response = None

    # get response
    try:
        response = make_request(url, action="GET")
    except Exception as e:
        logger.error(f"Could not get locations: {e}")

    try:
        response = validate_response(response)
    except Exception as v:
        logger.error(f"Status code on retriaval: {v}")
    else:
        return json.loads(response.text)


def get_reports_to_update(reports):
    to_update = []

    # Check the temperature for every hour
    for report in reports:
        current_temp = report["temperature"]
        modification_count = report["modification_count"]

        # change the temperature if degrees more than 20 and if we havent changed it yet
        if current_temp > 20.0 and modification_count == 0:
            # Calculate new temperature
            report["new_temperature"] = current_temp - 1

            # collect all the reports that need to be updated, so we can test
            to_update.append(report)

    return to_update


def update_reports(reports):
    for report in reports:
        update_temperature(report["id"], report["new_temperature"])
    return reports


def get_all_reports(locations):
    reports = []

    for location in locations:
        try:
            report = get_reports_for_location(location["name"])
        except Exception as e:
            logger.error(f"{e}")
        else:
            reports.extend(report)
    return reports


def get_updated_reports(reports):
    updated_reports = []
    for report in reports:
        if report["modification_count"] >= 1:
            updated_reports.append(report)
    return updated_reports


def change_climate():
    """
    Climate change: 
    
    We will retrieve reports for all the locations first
    then we will process them and update them accordingly
    """

    # Get all locations
    try:
        locations = get_locations()
    except Exception as e:
        logger.error("Could not retrieve locations")
    else:
        reports = get_all_reports(locations)

        print(f"We got {len(reports)} reports")

        reports_to_update = get_reports_to_update(reports)
        print(f"We have {len(reports_to_update)} reports to update")

        if reports_to_update:

            print(f"Fixing climate now (aka updating reports) ...")

            update_reports(reports_to_update)

            new_reports = get_all_reports(locations)
            updated_reports = get_updated_reports(new_reports)

            print(f"We updated {len(updated_reports)} reports")


if __name__ == '__main__':
    change_climate()



