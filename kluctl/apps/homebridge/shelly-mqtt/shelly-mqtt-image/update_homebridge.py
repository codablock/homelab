import logging

import requests

logger = logging.getLogger(__name__)


def login_homebridge(config):
    token = requests.post("%s/api/auth/login" % config["homebridge"]["url"],
                          json={"username": config["homebridge"]["username"], "password": config["homebridge"]["password"]})
    token.raise_for_status()
    token = token.json()["access_token"]
    headers = {"Authorization": "Bearer %s" % token}
    return headers

def load_homebridge_config(config):
    headers = login_homebridge(config)
    config = requests.get('%s/api/config-editor' % config["homebridge"]["url"], headers=headers)
    config.raise_for_status()
    config = config.json()
    return config

def save_homebridge_config(config, homebridge_config):
    headers = login_homebridge(config)
    requests.post("%s/api/config-editor" % config["homebridge"]["url"], headers=headers, json=homebridge_config)
    requests.put("%s/api/server/restart" % config["homebridge"]["url"], headers=headers)

def build_light(x):
    type = "lightbulb"
    dimmable = "dimmable" in x and x["dimmable"]
    if dimmable:
        type = "lightbulb-Dimmable"
    a = {
        "type": type,
        "name": x["name"],
        "topics": {
            "getOn": "%s" % x["switchTopic"],
            "setOn": "%s/command" % x["switchTopic"],
        },
        "onValue": "on",
        "offValue": "off",
        "accessory": "mqttthing",
    }
    if dimmable:
        a["topics"]["getBrightness"] = "%s/_brightness" % x["switchTopic"]
        a["topics"]["setBrightness"] = "%s/_brightness/set" % x["switchTopic"]
    return a

def build_switch(x):
    a = {
        "type": "switch",
        "name": x["name"],
        "topics": {
            "getOn": "%s" % x["switchTopic"],
            "setOn": "%s/command" % x["switchTopic"],
        },
        "onValue": "on",
        "offValue": "off",
        "accessory": "mqttthing",
    }
    return a

def build_fan(x):
    a = {
        "type": "fan",
        "name": x["name"],
        "topics": {
            "getOn": "%s" % x["switchTopic"],
            "setOn": "%s/command" % x["switchTopic"],
        },
        "onValue": "on",
        "offValue": "off",
        "accessory": "mqttthing",
    }
    return a

def build_humidity_sensor(x):
    a = {
        "type": "humiditySensor",
        "name": x["name"],
        "topics": {
            "getCurrentRelativeHumidity": "%s/_humidity" % x["sensorTopic"],
        },
        "history": True,
        "accessory": "mqttthing",
    }
    return a

def build_temperature_sensor(x):
    a = {
        "type": "temperatureSensor",
        "name": x["name"],
        "topics": {
            "getCurrentTemperature": "%s/temperature" % x["sensorTopic"],
        },
        "history": True,
        "accessory": "mqttthing",
    }
    return a

def build_contact_sensor(x):
    a = {
        "type": "contactSensor",
        "name": x["name"],
        "topics": {
            "getContactSensorState": "%s/_state" % x["sensorTopic"],
        },
        "onValue": "on",
        "offValue": "off",
        "history": True,
        "accessory": "mqttthing",
    }
    return a

def update_homebridge_accessories(config):
    logger.info("Updating homebridge accessories...")

    homebridge_config = load_homebridge_config(config)

    need_update = [False]

    accessories = homebridge_config['accessories']
    accessories_by_name = {}
    for a in accessories:
        accessories_by_name[a['name']] = a

    generated_accessories = {}

    def process(a, postfix=None):
        name = a["name"]
        if postfix is not None:
            name = "%s #%s" % (name, postfix)
            a["name"] = name
        if name in generated_accessories:
            raise Exception("Accessory with name %s is duplicated" % name)

        a["url"] = "mqtt://%s:%d" % (config["mqtt"]["host"], config["mqtt"]["port"])
        a["username"] = config["mqtt"]["username"]
        a["password"] = config["mqtt"]["password"]

        generated_accessories[name] = a
        if name not in accessories_by_name:
            accessories.append(a)
            accessories_by_name[a['name']] = a
            need_update[0] = True
            logger.info("Adding accessory: %s" % name)
            #logger.info(json.dumps(a, indent=2))
        elif a != accessories_by_name[name]:
            for i in range(len(accessories)):
                if accessories[i] is accessories_by_name[name]:
                    accessories[i] = a
                    accessories_by_name[name] = a
                    need_update[0] = True
                    logger.info("Updating accessory: %s" % name)
                    #logger.info(json.dumps(a, indent=2))

    def get_accs(type):
        if type not in config["accessories"]:
            return []
        return config["accessories"][type]

    for x in get_accs("lights"):
        process(build_light(x))
    for x in get_accs("switches"):
        process(build_switch(x))
    for x in get_accs("fans"):
        process(build_fan(x))
    for x in get_accs("temperatureSensors"):
        process(build_temperature_sensor(x))
    for x in get_accs("humiditySensors"):
        process(build_humidity_sensor(x))
    for x in get_accs("temperatureAndHumiditySensors"):
        process(build_temperature_sensor(x), "T")
        process(build_humidity_sensor(x), "H")
    for x in get_accs("contactSensors"):
        process(build_contact_sensor(x))

    for a in accessories:
        if a["name"] not in generated_accessories:
            topic = "unknown"
            if len(a["topics"]) != 0:
                topic = next(iter(a["topics"].values()))
            logger.info("%s not online. First topic: %s" % (a["name"], topic))

    if need_update[0]:
        save_homebridge_config(config, homebridge_config)
