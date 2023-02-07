import json
import logging
import re

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

def on_connect(client, config, flags, rc):
    logger.info("Connected with result code " + str(rc))

    client.subscribe("#")

def on_message(client, userdata, msg):
    try:
        on_message2(client, userdata, msg)
    except Exception as e:
        logger.exception("exception in on_message", exc_info=e)

def on_message2(client, config, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf8')

    base_pattern = re.compile(r"(\w*)/(\w*)-(\w*)/(.*)")
    m = base_pattern.match(topic)
    if not m:
        return

    logger.info("message: %s: %s" % (topic, payload))

    type = m.group(2)
    name = "%s-%s" % (m.group(2), m.group(3))
    name2 = "%s/%s" % (m.group(1), name)
    path = m.group(4)

    if type in ["shellydimmer", "shellydimmer2"]:
        m = re.match(r"^(light/[0-9]*)/status$", path)
        if m:
            j = json.loads(payload)
            client.publish("%s/%s/_brightness" % (name2, m.group(1)), j["brightness"])
        m = re.match(r"^(light/[0-9]*)/_brightness/set$", path)
        if m:
            j = json.dumps({"brightness": int(payload)})
            client.publish("%s/%s/set" % (name2, m.group(1)), j)
    elif type == "shellybutton1":
        m = re.match(r"^input_event/[0-9]*$", path)
        if m:
            j = json.loads(payload)
            event = j["event"]
            client.publish("%s/%s/_press" % (name2, path), event)
    elif type == "shellyht":
        m = re.match(r"^sensor/humidity$", path)
        if m:
            v = int(float(payload))
            client.publish("%s/sensor/_humidity" % name2, str(v))
        # m = re.match(r"^sensor/temperature$", path)
        # if m:
        #     v = int(float(payload))
        #     client.publish("%s/sensor/_temperatur" % name, str(v))
    elif type == "shellydw2":
        m = re.match(r"^sensor/state$", path)
        if m:
            if payload == "open":
                v = "on"
            else:
                v = "off"
            client.publish("%s/sensor/_state" % name2, str(v))

def start_mqtt(config):
    client = mqtt.Client()
    client.user_data_set(config)
    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set(config["mqtt"]["username"], config["mqtt"]["password"])
    client.connect(config["mqtt"]["host"], config["mqtt"]["port"], 60)

    client.loop_forever()
