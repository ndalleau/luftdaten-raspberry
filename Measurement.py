class Measurement:
    def __init__(self):
        pm25_values = []
        pm10_values = []
        dusty.workstate = SDS011.WorkStates.Measuring
        try:
            for a in range(8):
                values = dusty.get_values()
                if values is not None:
                    pm10_values.append(values[0])
                    pm25_values.append(values[1])
        finally:
            dusty.workstate = SDS011.WorkStates.Sleeping

        self.pm25_value  = np.mean(pm25_values)
        self.pm10_value  = np.mean(pm10_values)


    def sendInflux(self):
        """Envoi des données vers la base InfluxDB d ATMO"""
        cfg = config['influxdb']

        if not cfg['enabled']:
            return

        data = "feinstaub,node={},site={} SDS_P1={:0.2f},SDS_P2={:0.2f} ".format(
            sensorID,
            cfg['site'],
            self.pm10_value,
            self.pm25_value,
            
        )

        requests.post(cfg['url'],  #Change
            auth=(cfg['username'], cfg['password']),
            data=data,
        )

    def sendLuftdaten(self):
        """Envoi des données vers les API officielles de Luftdaten"""
        if not config['luftdaten']['enabled']:
            return

        self.__pushLuftdaten('https://api-rrd.madavi.de/data.php', 0, {
            "SDS_P1":             self.pm10_value,
            "SDS_P2":             self.pm25_value,

        })
        self.__pushLuftdaten('https://api.luftdaten.info/v1/push-sensor-data/', 1, {
            "P1": self.pm10_value,
            "P2": self.pm25_value,
        })


    def __pushLuftdaten(self, url, pin, values):
        requests.post(url,
            json={
                "software_version": "python-dusty 0.0.1",
                "sensordatavalues": [{"value_type": key, "value": val} for key, val in values.items()],
            },
            headers={
                "X-PIN":    str(pin),
                "X-Sensor": sensorID,
            }
        )

