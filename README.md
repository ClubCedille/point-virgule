# point-virgule

point-virgule est un bot Discord conçu pour rejoindre des canaux vocaux, enregistrer de
l'audio et l'envoyer a un service de transcription automatique.

Séquence de fonctionnement:

```mermaid
sequenceDiagram
    participant User
    participant Discord
    participant Point-Virgule
    participant Point
    participant Virgule

    User->>Discord: User starts voice channel
    User->>Discord: /start_meeting channel_id
    Discord->>Point-Virgule: Joins voice channel
    Point-Virgule->>Discord: Recording started
    Discord->>User: acknowledgment of recording started
    User->>Discord: /stop_meeting
    Discord->>Point-Virgule: Recording stopped
    Point-Virgule->>Discord: Leave voice channel
    Point-Virgule->>Point: Send audio data
    Point->>Point-Virgule: Send back transcription
    Point-Virgule->>Virgule: Send transcription
    Virgule->>Point-Virgule: Sends back summary
    Point-Virgule->>Discord: Send summary
    Discord->>User: Send summary
```

## Prérequis

- Python
- Docker (optionnel, pour le déploiement containerisé)

## Utilisation

```sh
git clone https://github.com/yourusername/point-virgule.git
cd point-virgule
pip install -r requirements.txt
python main.py
```

### Docker

Construire et exécuter l'image Docker:

```sh
docker build -t point-virgule .
docker run -d --name point-virgule point-virgule
```

## Commandes

- `/start_meeting [channel]`: Rejoindre le canal vocal spécifié et commencer
  l'enregistrement.
- `/stop_meeting`: Arrêter l'enregistrement et sauvegarder le fichier audio.
