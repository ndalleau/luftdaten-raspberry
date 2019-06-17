#!/usr/bin/env python3

import sys
import os
import yaml

# Import-Pfade setzen
sys.path.append(os.path.join(sys.path[0],"sds011"))  #Ajout module SDS011 au gestionnaire
#sys.path.append(os.path.join(sys.path[0],"bme280"))

import time
import datetime as datetime
import pytz
from datetime import timedelta
import json
import requests
import numpy as np
from sds011 import SDS011
#from Adafruit_BME280 import *

import argparse

#Parseur ####################################
#Le parseur définit les paramètres à compléter lors du lancement du script
#Dans le cas de ce script il s'agit du numéro ttyUSB sur lequel le SDS011 est branché, par défaut 0
description = """description"""
parseur = argparse.ArgumentParser(description=description)
parseur.add_argument('-d','--device',dest='device',default=0 ,help='numero device dans /dev', type=int)
parseur.add_argument('-s','--site',dest='site',default='site_test',help='site de mesures',type=str)
args=parseur.parse_args()
#############################################

# Lecture fichier de configuration ##########
with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)
    print("Fichier de configuration :")
    print(config)
    print("\n")
##############################################
    
# Logging
import logging

#Objet SDS01 #################################
#i=0 #Numero du SDS011 dans le repertoire /dev
i = args.device
port = "ttyUSB"+str(i)
print("Port: ",port)
print("Site: ",args.site)
if port in os.listdir("/dev"):
    print("Création objet capteur SDS011 sur port "+port)
    dusty = SDS011("/dev/"+port)
else:
    print("Pas de capteur sur port "+port)
    sys.exit()

# Now we have some details about it
print("SDS011 initialized: device_id={} firmware={}".format(dusty.device_id,dusty.firmware))

# Set dutycyle to nocycle (permanent)
dusty.dutycycle = 0
##############################################

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

# extracts serial from cpuinfo ################################
#Extraire le numéro du Raspberry pour envoyer avec les données
def getSerial():
    """Fonction pour récupérer le numéro de série du raspberry"""
    with open('/proc/cpuinfo','r') as f:
        for line in f:
            if line[0:6]=='Serial':
                return(line[10:26])
    raise Exception('CPU serial not found')
###############################################################
    
def run():
    m = Measurement()
    
    print(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
    print('pm2.5     = {:f} '.format(m.pm25_value))
    print('pm10      = {:f} '.format(m.pm10_value))
    print('\n')

    print("*** Envoi des données ***")
    if config['influxdb']['enabled'] == True:
        print("{0}{1}".format("Send to InfluxDB: ",config['influxdb']['url']))
        m.sendInflux()
    if config['luftdaten']['enabled'] == True:
        print("Send to Luftdaten : ")
        m.sendLuftdaten()
    print("-------------------------")


sensorID  = config['luftdaten'].get('sensor') or ("raspi-" + getSerial())
starttime = time.time()

#Gestion du répertoire ####################
print("Repertoire en cours: ",os.getcwd())
print("\n")
###########################################


#Visualisation de la configuration ########
print("*** Configuration ***")
print("Site de mesure: {0}".format(config['influxdb']['site']))
print("Frequence echantillonnage en secondes: {0}".format(config['acquisition']['sample']))
print(config['luftdaten'].get('sensor'))
print("Lecture du numero de serie raspi-" + getSerial())
print("{0} {1}".format('Sensor Id: ',sensorID))
print("*********************")
############################################

#Corps du programme

tz=pytz.timezone('Europe/Paris')
deb=datetime.datetime.now()  #Date de début execution du script
debText=deb.strftime('%Y-%m-%d %H:%M:%S')
print("Debut execution du script: "+debText)

while True:
    print('\n')
    print("running ...")
    run()
    time.sleep(config['acquisition']['sample']- ((time.time() - starttime) % config['acquisition']['sample']))

print("Stopped")

