import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from interactions import slash_command, GuildVoice, OptionType, SlashContext, ChannelType, slash_option, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Point-Virgule")

class RecorderBot(Client):
    def __init__(self, recording_path: str, point_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_path = recording_path
        self.point_url = point_url
        self.active_recordings = {}
        self.recording_states = {}

    @slash_command(name="start_meeting", description="Commencer l'enregistrement d'une réunion")
    @slash_option(
        name="channel",
        description="Choisir le canal vocal dans lequel enregistrer la réunion",
        required=True,
        opt_type=OptionType.CHANNEL,
        channel_types=[ChannelType.GUILD_VOICE]
    )
    async def start_meeting(self, ctx: SlashContext, channel: GuildVoice):
        await ctx.send("Connexion au canal vocal...")
        voice_state = await channel.connect()
        await voice_state.start_recording()
        self.active_recordings[ctx.guild_id] = voice_state
        self.recording_states[ctx.guild_id] = True
        await ctx.send("Enregistrement démarré. Utilisez `/stop_meeting` pour arrêter l'enregistrement et déconnecter.")
        logger.info(f"Enregistrement démarré dans la guilde: {ctx.guild_id}")

    @slash_command(name="stop_meeting", description="Arrêter l'enregistrement d'une réunion")
    async def stop_meeting(self, ctx: SlashContext):
        if ctx.guild_id in self.active_recordings and self.recording_states.get(ctx.guild_id, False):
            voice_state = self.active_recordings[ctx.guild_id]
            await ctx.send("Déconnexion du canal vocal...")
            await voice_state.stop_recording()
            await voice_state.disconnect()
            file_path = self.save_audio(ctx, voice_state)
            del self.active_recordings[ctx.guild_id]
            self.recording_states[ctx.guild_id] = False
            await ctx.send("Enregistrement arrêté. Envoi du fichier audio pour transcription...")

            logger.info(f"Enregistrement arrêté dans la guilde: {ctx.guild_id}")

            transcript = self.get_transcript(file_path)
            if transcript:
                await ctx.send(f"Transcription:\n{transcript}")
                logger.info(f"Transcription réussie: {transcript[:100]}")
                self.delete_audio(file_path)
            else:
                await ctx.send("Erreur lors de la transcription de l'audio.")
                logger.error(f"Erreur lors de la transcription de l'audio pour la guilde {ctx.guild_id}")
        else:
            await ctx.send("Je n'enregistre pas dans ce serveur Discord.")
            logger.error(f"Enregistrement non trouvé pour la guilde {ctx.guild_id}")

    def save_audio(self, ctx: SlashContext, voice_state):
        for user_id, audio_data in voice_state.recorder.output.items():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"{user_id}_{timestamp}.mp3"
            file_path = os.path.join(self.recording_path, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(audio_data.read())
            return file_path

    def get_transcript(self, file_path):
        try:
            with open(file_path, 'rb') as audio_file:
                response = requests.post(self.point_url, files={'file': audio_file}, headers={'Content-Type': 'audio/mp3'})
                if response.status_code == 200:
                    logger.info(f"L'appel de l'API de transcription a réussi pour le fichier {file_path}")
                    return response.text
                logger.error(f"L'appel de l'API de transcription a échoué pour le fichier {file_path} avec le code d'état {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Une erreur s'est produite lors de l'appel de l'API de transcription pour le fichier {file_path}: {e}")
            return None

    def delete_audio(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    recording_path = os.getenv("RECORDING_PATH", "./recordings/")
    point_url = os.getenv("TRANSCRIPTION_API_URL", "http://localhost:5000/transcript")
    bot = RecorderBot(recording_path, point_url)
    logger.info("démarrage du bot Discord...")
    bot.start(token)
