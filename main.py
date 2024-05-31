import os
from datetime import datetime
from dotenv import load_dotenv
from interactions import slash_command, GuildVoice, OptionType, SlashContext, ChannelType, slash_option, Client

class RecorderBot(Client):
    def __init__(self, recording_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_path = recording_path
        self.active_recordings = {}
        
    @slash_command(name="start_meeting", description="Commencer l'enregistrement d'une réunion")
    @slash_option(
        name="channel",
        description="Sélectionnez le canal vocal pour enregistrer",
        required=True,
        opt_type=OptionType.CHANNEL,
        channel_types=[ChannelType.GUILD_VOICE]
    )
    async def start_meeting(self, ctx: SlashContext, channel: GuildVoice):
        await ctx.send("Connexion au canal vocal...")
        await channel.connect()
        await ctx.voice_state.start_recording()
        self.active_recordings[ctx.guild_id] = channel
        await ctx.send("Enregistrement démarré. Utilisez `/stop_meeting` pour arrêter l'enregistrement et déconnecter.")

    @slash_command(name="stop_meeting", description="Arrêter l'enregistrement d'une réunion")
    async def stop_meeting(self, ctx: SlashContext):
        if ctx.guild_id in self.active_recordings:
            channel = self.active_recordings[ctx.guild_id]
            await ctx.send("Déconnexion du canal vocal...")
            await ctx.voice_state.stop_recording()
            await channel.disconnect()
            self.save_audio(ctx)
            del self.active_recordings[ctx.guild_id]
            await ctx.send("Enregistrement arrêté et sauvegardé.")
        else:
            await ctx.send("Je n'enregistre pas dans ce serveur Discord.")

    def save_audio(self, ctx: SlashContext):
        """Enregistrer les données audio pour chaque utilisateur dans l'enregistreur d'état vocal."""
        for user_id, audio_data in ctx.voice_state.recorder.output.items():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"{user_id}_{timestamp}.mp3"
            file_path = os.path.join(self.recording_path, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(audio_data.read())

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    recording_path = os.getenv("RECORDING_PATH", "./recordings/")
    bot = RecorderBot(recording_path)
    bot.start(token)
