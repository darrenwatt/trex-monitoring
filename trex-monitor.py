import requests, pprint, time, logging
from influxdb import InfluxDBClient

influxclient = InfluxDBClient('192.168.0.3', 8086, 'root', 'root', 'darrenInflux')
url = "http://192.168.0.20:4067/summary"
writedata = True # True/False
loop_timer = 60 # seconds

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG, # INFO / DEBUG
    datefmt='%Y-%m-%d %H:%M:%S')


def get_stats():
    try:
        logging.info("Getting stats from host ...")
        resp = requests.get(url).json()
        logging.debug(resp)
    except requests.exceptions.RequestException as e:
            logging.info('Failed to get stats from host.')
            print(e)
            return False
    return resp


def build_payload(data):
    efficiency = data['gpus'][0]['efficiency'].split("k")[0]
    try:
        efficiency= int(efficiency)
    except ValueError as v:
        logging.info('No efficiency value reported.')
        efficiency = 0
    payload = {
        "measurement": "trex-stats-whitebox",
        "fields": {
            "driver": data['driver'],
            "version": data['version'],
            "hashrate": data['hashrate'],
            "hashrate_day": data['hashrate_day'],
            "hashrate_hour": data['hashrate_hour'],
            "efficiency": efficiency,
            "fan_speed": data['gpus'][0]['fan_speed'],
            "power": data['gpus'][0]['power'],
            "temperature": data['gpus'][0]['temperature']
        }
    }
    return payload


def write_db(mydict):
    if writedata:
        try:
            logging.info("Writing to influxdb ...")
            influxclient.write_points([mydict])
        except ConnectionError as e:
            logging.info("Unable to write data to influxdb.")
            print(e)


def main():
    while True:
        data = get_stats()
        if data != False:
            payload = build_payload(data)
            logging.debug(payload)
            write_db(payload)
        time.sleep(loop_timer)


main()
