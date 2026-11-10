import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1488262125708116198
CATEGORIA_TICKET_ID = 1488541441373241364
RUOLO_STAFF_ID = 1498676038937481246
MAPPA_EH_URL = "INSERISCI_QUI_LINK_MAPPA"

VILLE = {
    "A1": {"nome": "Villa A1 - Vinewood Hills", "prezzo": "€30.000", "emoji": "🏡", "zona": "Lusso - Vinewood Hills"},
    "A2": {"nome": "Villa A2 - Vinewood Hills", "prezzo": "€35.000", "emoji": "🏡", "zona": "Lusso - Vinewood Hills"},
    "A3": {"nome": "Villa A3 - Rockford Hills", "prezzo": "€40.000", "emoji": "🏠", "zona": "Lusso - Rockford Hills"},
    "A4": {"nome": "Villa A4 - Vespucci Beach", "prezzo": "€45.000", "emoji": "🏖️", "zona": "Lusso - Vespucci Beach"},
    "B1": {"nome": "Casa B1 - Mirror Park", "prezzo": "€15.000", "emoji": "🏠", "zona": "Città - Mirror Park"},
    "B2": {"nome": "Casa B2 - Sandy Shores", "prezzo": "€10.000", "emoji": "🏜️", "zona": "Città - Sandy Shores"},
    "C1": {"nome": "Villa C1 - Paleto Bay", "prezzo": "€20.000", "emoji": "🌲", "zona": "Paleto Bay"},
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class InfoVillaModal(discord.ui.Modal, title="Info Aggiuntive - Facoltativo"):
    uso = discord.ui.TextInput(label="Uso della villa / casa", placeholder="Es: Abitazione, Base gang, Azienda...", required=False, max_length=100)
    note = discord.ui.TextInput(label="Note aggiuntive", placeholder="Es: Ho già i soldi, voglio visitarla...", required=False, style=discord.TextStyle.paragraph, max_length=500)

    def __init__(self, villa_key: str):
        super().__init__()
        self.villa_key = villa_key

    async def on_submit(self, interaction: discord.Interaction):
        try:
            villa = VILLE[self.villa_key]
            guild = interaction.guild
            user = interaction.user
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            }
            staff_role = guild.get_role(RUOLO_STAFF_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            categoria = guild.get_channel(CATEGORIA_TICKET_ID)
            channel = await guild.create_text_channel(
                name=f"villa-{self.villa_key.lower()}-{user.name}",
                category=categoria if categoria else None,
                overwrites=overwrites,
                topic=f"Ticket Villa {self.villa_key} | {user.id}"
            )
            uso_text = self.uso.value if self.uso.value else "Non specificato"
            note_text = self.note.value if self.note.value else "Nessuna"
            embed = discord.Embed(
                title=f"🏡 Richiesta Acquisto - {villa['nome']}",
                description=f"Nuova richiesta da {user.mention}",
                color=discord.Color.gold()
            )
            embed.add_field(name="📍 Villa / Casa Selezionata", value=f"**{self.villa_key}** - {villa['nome']}", inline=False)
            embed.add_field(name="🗺️ Zona", value=villa['zona'], inline=True)
            embed.add_field(name="💰 Prezzo", value=villa['prezzo'], inline=True)
            embed.add_field(name="👤 Richiedente", value=f"{user.mention} (`{user.id}`)", inline=False)
            embed.add_field(name="🎯 Uso Previsto", value=uso_text, inline=False)
            embed.add_field(name="📝 Note Aggiuntive", value=note_text, inline=False)
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text="Sistema Ville EH - Eclissi RP")
            ping = f"<@&{RUOLO_STAFF_ID}>" if staff_role else ""
            await channel.send(content=f"{user.mention} {ping}", embed=embed, view=ChiudiTicketView())
            await interaction.response.send_message(f"✅ Ticket aperto! Vai su {channel.mention}", ephemeral=True)
        except Exception as e:
            print(f"Errore modal: {e}")
            try:
                await interaction.response.send_message(f"Errore apertura ticket: {e}", ephemeral=True)
            except:
                pass

class ChiudiTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="chiudi_ticket_villa")
    async def chiudi(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket in chiusura tra 5 secondi...", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class VillaSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for key, data in VILLE.items():
            options.append(discord.SelectOption(
                label=f"{key} - {data['nome']}",
                description=f"Prezzo: {data['prezzo']} | {data['zona']}",
                emoji=data['emoji'],
                value=key
            ))
        super().__init__(placeholder="Seleziona una villa / casa...", min_values=1, max_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InfoVillaModal(self.values[0]))

class VillaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VillaSelect())

# --- QUESTO E' IL COMANDO GIUSTO ---
@bot.tree.command(name="ticket_pannel", description="Apri il pannello per comprare una villa / casa")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def ticket_pannel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🗺️ MAPPA VILLE & CASE - EH",
        description=(
            "**Benvenuto nel sistema acquisto ville!**\n\n"
            "Guarda la mappa, seleziona dal menù qui sotto la villa che vuoi e ti si aprirà un ticket in automatico.\n\n"
            "**🏡 ZONE:**\n"
            "🟡 **A1 - A4** -> Lusso / Vinewood / Vespucci\n"
            "🔵 **B1 - B2** -> Città / Sandy Shores\n"
            "🟢 **C1** -> Paleto Bay\n\n"
            "**💰 LISTINO:**\n"
            "A1 - €30.000 | A2 - €35.000 | A3 - €40.000 | A4 - €45.000\n"
            "B1 - €15.000 | B2 - €10.000 | C1 - €20.000\n\n"
            "*Le informazioni sull'uso sono facoltative.*"
        ),
        color=discord.Color.blue()
    )
    # Se il link mappa è valido lo mostra, se no non crasha
    if MAPPA_EH_URL.startswith("http"):
        embed.set_image(url=MAPPA_EH_URL)
    embed.set_footer(text="Sistema Ville EH - Seleziona una villa per aprire il ticket")
    await interaction.response.send_message(embed=embed, view=VillaView(), ephemeral=True)

@bot.event
async def on_ready():
    print(f"Bot online come {bot.user}")
    try:
        # Cancella i vecchi comandi e sincronizza solo il nuovo
        bot.tree.clear_commands(guild=discord.Object(id=GUILD_ID))
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Sincronizzati {len(synced)} comandi: {[c.name for c in synced]}")
    except Exception as e:
        print(e)

bot.run(TOKEN)