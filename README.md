# luftdaten-raspberry
luftdaten 

Ce script python permet d'utiliser un raspberry pi 3 à la place d'un microcontrolleur NodemCU ESP8266 pour acquérir les données d'un capteur de particules SDS011 et envoyer les résultats des mesures vers le site Luftdaten.info et une base de données InfluxDB.
En effet, dans certains cas, il n'est pas possible d'avoir le wifi. L'utilisation d'un raspberry permet alors de s'affranchir des contraintes du wifi lorsque celui ci n'est pas disponible. Toutefois pour accéder à internet et notamment au site Luftdaten, il est possible de brancher le raspberry en ethernet.
L'utilisation du Raspebbery permet aussi le stockage des données dans une base InfluxDB (déployée sur le raspberry) ou dans un fichier CSV (à venir). 

# luftdaten
Le site luftdaten.info (https://luftdaten.info/) est issu d'un projet issu de l'OK Lab de Stuttgart qui permet la réalisation d'une station de mesures de la pollution atmopshérique par les particules (PM10 et PM2.5). Ce site participe à la mise en place d'un observatoire citoyen de la qualité de l'air.

# Capteurs supportés:
  Capteur de mesures des particules SDS011 (Constructeur: nova fitness): recommandé par le site luftdaten.info
  Le capteur SDS011 est branché sur un des ports USB du Raspberry Pi 3 en utilisant le module FTDI fourni par le constructeur du capteur.
  
  Plantower PMSXXXX (à venir)
  
# Dépendances
  sudo apt install python3-numpy python3-requests python3-yaml python3-serial
  
# Configuration
Il faut modifier le fichier config.yml pour activer les API (Envoi des données vers le site Luftdaten et/ou InfluxDB)

# Lancement
python3 main.py 

Il est possible de compléter avec des paramètres différent de celui du fichier de configuration lors du lancement du script
python3 main.py --device ttyUSB0 --site site_mesures --sample 60

--device ttyUSB0 correspond au numéro du port USB sur lequel est branché le SDS011

--site site_mesure correspond au site de mesures (cette information remonte dans la base InfluxDB)

--sample correspond à la durée entre deux mesures


