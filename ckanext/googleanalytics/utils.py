import json
import logging

import requests
from six.moves.urllib.parse import urlencode
from ckanext.googleanalytics import config


log = logging.getLogger(__name__)

EVENT_API = "CKAN API Request"
EVENT_DOWNLOAD = "CKAN Resource Download Request"


def send_event(data):
    if isinstance(data, MeasurementProtocolData):
        if data["event"] == EVENT_API:
            return _mp_api_handler({
                "action": data["object"],
                "payload": data["payload"],
            })

        if data["event"] == EVENT_DOWNLOAD:
            return _mp_download_handler({"payload": {
                "resource_id": data["id"],
            }})

        log.warning("Only API and Download events supported by Measurement Protocol at the moment")
        return

    return _ga_handler(data)


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, _):
        return None


def _mp_api_handler(data_dict):
    log.debug(
        "Sending API event to Google Analytics using the Measurement Protocol: %s",
        data_dict
    )
    _mp_event({
        "name": data_dict["action"],
        "params": data_dict["payload"]
    })


def _mp_download_handler(data_dict):
    log.debug(
        "Sending Downlaod event to Google Analytics using the Measurement Protocol: %s",
        data_dict
    )
    _mp_event({
        "name": "file_download",
        "params": data_dict["payload"],
    })


def _mp_event(event):
    resp = requests.post(
        "https://www.google-analytics.com/mp/collect",
        params={
            "api_secret": config.measurement_protocol_client_secret(),
            "measurement_id": config.measurement_id()
        },
        data=json.dumps({
            "client_id": config.measurement_protocol_client_id(),
            "non_personalized_ads": False,
            "events": [event]
        }, cls=SafeJSONEncoder)
    )

    if resp.status_code >= 300:
        log.error("Cannot post event: %s", resp)


def _ga_handler(data_dict):
    data = urlencode(data_dict)
    log.debug("Sending API event to Google Analytics: %s", data)

    requests.post(
        "http://www.google-analytics.com/collect",
        data,
        timeout=10,
    )


class UniversalAnalyticsData(dict):
    pass


class MeasurementProtocolData(dict):
    pass
