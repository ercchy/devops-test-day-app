import json
import requests
import logging

logger = logging.getLogger(__name__)

# TODO: add timeout
# TODO: add retry
# TODO: add logging
# TODO: add error handling


def make_get_request(url):

    payload = {}
    headers = {
        'Content-Type': 'application/json'
    }

    logger.info(f"sending GET request to: {url}")
    # handle possible errors
    response = requests.request("GET", url, headers=headers, data=payload)

    return response


def make_patch_request(url, payload):
    payload = payload
    headers = {
        'Content-Type': 'application/json'
    }

    # log this here
    # handle possible errors
    response = requests.request("PATCH", url, headers=headers, data=payload)

    return response


def get_all_reports(location):
    url = f"http://localhost:3000/weather_reports?location={location}"
    # get response
    response = make_get_request(url)

    # make to Python object
    by_hours = json.loads(response.text)

    return by_hours


def process_data(all_reports):
    url = "http://localhost:3000/weather_reports"

    # Check the temperature for evry hour
    for hourly in reports:
        current_temp = hourly["temperature"]

        # 4. change the temperature if degrees more than 20
        if current_temp > 20.0:
            url = f'{url}/{hourly["id"]}'
            payload = {
                "weather_report": {
                    "temperature": current_temp - 1,
                    "description": "tornados"
                }
            }
            make_patch_request(url, payload=payload)

    return reports


if __name__ == '__main__':

    # Steps:
    # 1. get all locations
    locations_url = "http://localhost:3000/locations"
    locations_response = make_get_request(locations_url)
    locations = json.loads(locations_response.text)

    for location in locations:
        # get a report for a location
        reports = get_all_reports(location["name"])

        # fix the temperature
        new_reports = process_data(reports)
        # update the object
        refreshed_reports = get_all_reports(location)

        print(new_reports)




