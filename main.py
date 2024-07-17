import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from interactions import slash_command, GuildVoice, OptionType, SlashContext, ChannelType, slash_option, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecorderBot(Client):
    def __init__(self, recording_path: str, api_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_path = recording_path
        self.point_url = api_url
        self.active_recordings = {}

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
        await ctx.send("Enregistrement démarré.")
        self.active_recordings[ctx.guild_id] = voice_state
        await ctx.send("Utilisez `/stop_meeting` pour arrêter l'enregistrement et déconnecter.")
        logger.info(f"Enregistrement démarré dans la guilde: {ctx.guild_id}")


    @slash_command(name="stop_meeting", description="Arrêter l'enregistrement d'une réunion")
    async def stop_meeting(self, ctx: SlashContext):
        if ctx.guild_id in self.active_recordings:
            channel = self.active_recordings[ctx.guild_id]
            await ctx.send("Déconnexion du canal vocal...")
            await ctx.voice_state.stop_recording()
            await channel.disconnect()
            file_path = self.save_audio(ctx)
            del self.active_recordings[ctx.guild_id]
            await ctx.send("Enregistrement arrêté. Envoi du fichier audio pour transcription...")

            logger.info(f"Enregistrement arrêté dans la guilde: {ctx.guild_id}")
            
            transcript = self.get_transcript(file_path)
            if transcript:
                await ctx.send(f"Transcription:\n{transcript}")
                logger.info(f"Transcription réussie: {transcript[:100]}")
            else:
                await ctx.send("Erreur lors de la transcription de l'audio.")
                logger.error(f"Erreur lors de la transcription de l'audio pour la guilde {ctx.guild_id}")
            
            self.delete_audio(file_path)
        else:
            await ctx.send("Je n'enregistre pas dans ce serveur Discord.")
            logger.error(f"Enregistrement non trouvé pour la guilde {ctx.guild_id}")

    def save_audio(self, ctx: SlashContext):
        for user_id, audio_data in ctx.voice_state.recorder.output.items():
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
                response = requests.post(self.api_url, files={'file': audio_file}, headers={'Content-Type': 'audio/mp3'})
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
    api_url = os.getenv("TRANSCRIPTION_API_URL", "http://127.0.0.1:5000/transcript")
    bot = RecorderBot(recording_path, api_url)
    logger.info(f"{bot.user.name} démarré.")
    bot.start(token)
