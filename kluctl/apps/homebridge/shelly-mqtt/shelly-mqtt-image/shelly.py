import logging
from concurrent.futures.thread import ThreadPoolExecutor

import ipcalc
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


def do_request(ip, user, password):
    try:
        status = requests.get('http://%s/status' % ip, timeout=1, auth=HTTPBasicAuth(user, password)).json()
        settings = requests.get('http://%s/settings' % ip, timeout=1, auth=HTTPBasicAuth(user, password)).json()
        return status, settings
    except Exception as e:
        #print(e)
        return e

def scan_shellies(cidr, user, password):
    result = []
    with ThreadPoolExecutor(max_workers=128) as e:
        for ip in ipcalc.Network(cidr):
            f = e.submit(do_request, ip, user, password)
            result.append(f)
    for i in range(len(result)):
        result[i] = result[i].result()
    result = [x for x in result if x is not None and not isinstance(x, Exception)]
    return result

def update_shelly_settings(config, shellies):
    static_ips = config["shellies"]["network"]["ips"]
    ip_to_shelly = {}
    for k, v in static_ips.items():
        if v in ip_to_shelly:
            raise Exception("Duplicate ip %s" % v)
        ip_to_shelly[v] = k

    for status, settings in shellies:
        ip = status["wifi_sta"]['ip']
        hostname = settings["device"]["hostname"]

        updated = False
        auth = HTTPBasicAuth(config["shellies"]["login"]["username"], config["shellies"]["login"]["password"])
        if settings["cloud"]["enabled"]:
            logger.info("%s has cloud enabled" % hostname)
            requests.post("http://%s/settings/cloud/?enabled=0" % ip, auth=auth)
            updated = True
        if not settings["login"]["enabled"]:
            logger.info("%s has login disabled...enabling..." % hostname)
            requests.post("http://%s/settings/login?enabled=1&username=%s&password=%s" % (ip, auth.username, auth.password))
            updated = True
        if not settings["mqtt"]["enable"] or settings["mqtt"]["user"] != config["mqtt"]["username"]:
            logger.info("%s needs mqtt update...updating..." % hostname)
            data = {
                "mqtt_enable": "true",
                "mqtt_server": "%s:%d" % (config["mqtt"]["host"], config["mqtt"]["port"]),
                "mqtt_user": config["mqtt"]["username"],
                "mqtt_pass": config["mqtt"]["password"],
            }
            requests.post("http://%s/settings" % ip, data, auth=auth)
            updated = True
        if hostname in static_ips:
            expected = {
                'enabled': True,
                'ipv4_method': 'static',
                'ip': static_ips[hostname],
                'gw': config["shellies"]["network"]["gw"],
                'mask': config["shellies"]["network"]["mask"],
                'dns': config["shellies"]["network"]["dns"]
            }
            for k in expected.keys():
                if settings["wifi_sta"][k] != expected[k]:
                    logger.info("%s needs static ip config update (old: %s, new: %s)..." % (hostname, str(settings["wifi_sta"]), str(expected)))
                    data = {
                        "ipv4_method": expected["ipv4_method"],
                        "ip": expected["ip"],
                        "netmask": expected["mask"],
                        "gateway": expected["gw"],
                        "dns": expected["dns"],
                    }
                    requests.post("http://%s/settings/sta" % ip, data, auth=auth)
                    updated = True
                    break
        else:
            if settings["wifi_sta"]["ipv4_method"] != "dhcp":
                data = {
                    "ipv4_method": "dhcp",
                }
                requests.post("http://%s/settings/sta" % ip, data, auth=auth)
                updated = True
        # if settings["name"].startswith("switch-") and  settings["name"].find("garage") == -1:
        #     logger.info("%s: %s blub..." % (hostname, settings["name"]))
        #     data = {
        #         "name": "light-%s" % settings["name"].replace("switch-", ""),
        #     }
        #     requests.post("http://%s/settings" % ip, data, auth=auth)
        if updated:
            logger.info("%s (%s) has been updated. Rebooting..." % (hostname, ip))
            requests.post("http://%s/reboot" % ip, auth=auth)
        else:
            logger.info("%s (%s) was up-to-date already" % (hostname, ip))



def update_shellies(config):
    logger.info("Scanning shellies...")
    shellies = scan_shellies(config["shellies"]["network"]["cidr"], config["shellies"]["login"]["username"], config["shellies"]["login"]["password"])
    logger.info("Found %d shellies" % len(shellies))
    for status, settings in shellies:
        logger.info("%s: %s" % (settings["device"]["hostname"], settings["name"]))

    logger.info("Updating shelly settings...")
    update_shelly_settings(config, shellies)
