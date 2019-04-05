# luftdaten-raspberry
luftdaten 

Un script python pour utiliser un raspberry pi (à la place d'un microcontrolleur NodemCU ESP8266) pour acquérir les données d'un capteur de particules SDS011 et envoyer les résultats vers le site Luftdaten.info et une base de données InfluxDB.

Le site luftdaten.info (https://luftdaten.info/) est issu d'un projet issu de l'OK Lab de Stuttgart qui permet la réalisation d'une station de mesures de la pollution atmopshérique par les particules. Ce site participe à la mise en place d'un observatoire citoyen de la qualité de l'air.

# Capteurs supportés:
  SDS011 (nov fitness): recommandé pr le site luftdaten.info
  
  Plantower (à venir)
  
# Dépendances
  apt install python3-numpy python3-requests python3-yaml python3-serial
  
#Configuration
Modifier le fichier config.yml



