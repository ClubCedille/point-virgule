# Point

Point est un bot Discord conçu pour rejoindre des canaux vocaux, enregistrer de l'audio et l'envoyer a un service de transcription automatique. Il est conçu pour être facile à utiliser et à déployer, et peut être utilisé pour enregistrer des réunions, des appels, des podcasts et plus encore.

## Prérequis

- Python
- Docker (optionnel, pour le déploiement containerisé)

## Utilisation

```sh
git clone https://github.com/yourusername/point.git
cd point
pip install -r requirements.txt
python main.py
```

### Docker

Construire et exécuter l'image Docker:

```sh
docker build -t point .
docker run -d --name point point
```

## Commandes

- `/start_meeting [channel]`: Rejoindre le canal vocal spécifié et commencer l'enregistrement.
- `/stop_meeting`: Arrêter l'enregistrement et sauvegarder le fichier audio.
