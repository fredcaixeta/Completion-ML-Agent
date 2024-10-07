import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv

import json

import completion

import openai
import re

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a chave da API da OpenAI do arquivo .env
openai.api_key = os.getenv('OPENAI_API_KEY')


try:
    ANNOUNCE_CHANNEL_ID = int(os.getenv('ANNOUNCE_CHANNEL_ID'))
    BACKGROUNDS_CHANNEL_ID = int(os.getenv('BACKGROUNDS_CHANNEL_ID'))
    BUILDS_CHANNEL_ID = int(os.getenv('BUILDS_CHANNEL_ID'))
    MAIN_GUILD_ID = int(os.getenv('MAIN_GUILD_ID'))
    
except TypeError:
    raise ValueError("One or more environment variables are missing or not set correctly.")

class ConfirmButton(View):
    def __init__(self, user, embed, target_channel, moderation_channel, bot, title_type, files):
        super().__init__(timeout=60) 
        self.user = user
        self.embed = embed
        self.target_channel = target_channel
        self.moderation_channel = moderation_channel
        self.bot = bot
        self.title_type = title_type
        self.files = files

    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode confirmar isso.", ephemeral=True)
            return

        await interaction.response.send_message("A sua publicação foi confirmada e publicada!", ephemeral=True)
        await self.target_channel.send(embed=self.embed)
        
        if self.files:
            await self.target_channel.send(files=[await file.to_file() for file in self.files])

        await self.moderation_channel.send(f"{self.user.display_name} ({self.user.id}) postou um {self.title_type}.")
        
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("Você não pode cancelar essa mensagem.", ephemeral=True)
            return
        
        await interaction.response.send_message("Sua publicação foi cancelada.", ephemeral=True)
        self.stop()

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.announce, guild=discord.Object(id=MAIN_GUILD_ID))
        self.bot.tree.add_command(self.airfoilai, guild=discord.Object(id=MAIN_GUILD_ID))
        #self.bot.tree.add_command(self.build, guild=discord.Object(id=MAIN_GUILD_ID))

    @app_commands.command(name="anuncio", description="Envia um anúncio RP no #anuncios-roleplay")
    async def announce(self, interaction: discord.Interaction):
        await interaction.response.send_message("Olhe seu privado para continuarmos o anuncio.", ephemeral=True)
        await self.send_dm(interaction.user, ANNOUNCE_CHANNEL_ID, "anúncio", "o anúncio", "anúncio", "seu anúncio")

    @app_commands.command(name="airfoilai", description="Utilizando RAG & Chat Completion!")
    async def airfoilai(self, interaction: discord.Interaction):
        await interaction.response.send_message("Olhe seu privado para continuarmos com Chat Completion...", ephemeral=True)
        await self.send_dm(interaction.user, BACKGROUNDS_CHANNEL_ID, "airfoilai", "a história do seu personagem", "personagem", "seu background")

    async def send_dm(self, user: discord.User, channel_id: int, title_type: str, description_prompt: str, title_prompt: str, success_message: str):
        def check(m):
            return m.author == user and isinstance(m.channel, discord.DMChannel)
        
        try:
            restart = True
            while restart == True:
                dm_channel = await user.create_dm()

                await dm_channel.send(f"*GenAI*: Como gostaria de prever o ruído do seu aerofólio? Exemplo:\n\nPrever o ruído com base em parâmetros específicos - Frequency em *Hz* (ex: 3000), Suction Thickness em *m* (ex: 1.8), Chord Length em *m* (ex: 0.28), Angle of Attack em *deg* (ex: 53), Free Stream Velocity em *m/s* (ex: 0.002).")
                question = await self.bot.wait_for('message', check=check)                                                                                                  
                question = question.content

                resposta_ai = completion.start_Completion(question)
                resposta_ai = re.search(r'{.*?}', resposta_ai, re.DOTALL).group(0)
                print(resposta_ai)
                # Converte a string JSON para um dicionário Python
                try:
                    resposta_ai = json.loads(resposta_ai)  # Isso vai transformar a string em um dicionário
                    print(resposta_ai)
                    #await dm_channel.send(f"Debug GenAI: {resposta_ai}")
                except json.JSONDecodeError as e:
                    print(f"Erro ao converter JSON: {e}")
                
                try:
                    frequency = float(resposta_ai.get("Frequency"))
                    suction_thickness = float(resposta_ai.get("Suction Thickness"))
                    chord_length = float(resposta_ai.get("Chord Length"))
                    angle_of_attack = float(resposta_ai.get("Angle of Attack"))
                    free_stream_velocity = float(resposta_ai.get("Free Stream Velocity"))
                except Exception:
                    frequency = float(resposta_ai.get("Frequency"))
                    suction_thickness = float(resposta_ai.get("Suction_Thickness"))
                    chord_length = float(resposta_ai.get("Chord_Length"))
                    angle_of_attack = float(resposta_ai.get("Angle_of_Attack"))
                    free_stream_velocity = float(resposta_ai.get("Free_Stream_Velocity"))

                import prever_ruido_aerofolio
                
                result = prever_ruido_aerofolio.prever_ruido(frequency, suction_thickness, chord_length, angle_of_attack, free_stream_velocity)
                await dm_channel.send(f"\n\n*GenAI*: Predição do Modelo: Ruído estimado de {result} dB.\n\n")
                
                import agente_expert_aeroespacial
                question = f"Para os parâmetros do aerofólio {resposta_ai}, tem-se um ruído estimado de {result} dB."
                
                agent_ai = agente_expert_aeroespacial.start_Completion(question)
                await dm_channel.send(f"\n\n*AI Agente Engenheiro Aeroespacial*:\n\n{agent_ai}\n")
                
                await dm_channel.send(f"\n\n*GenAI*: Deseja ter análises de outro aerofólio? Yes / No")
                restart_confirm = await self.bot.wait_for('message', check=check)
                
                if restart_confirm == "No":
                    restart = False
                        
                
        except Exception as e:
            await dm_channel.send(f"Ocorreu um erro: {e}")

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))