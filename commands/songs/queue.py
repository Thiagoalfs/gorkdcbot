import discord
from discord.ui import Button, View
from commands.songs.vcplay import song_queues

class QueueView(View):
    def __init__(self, guild_id, pages, current_page=0):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.pages = pages
        self.current_page = current_page

    def create_embed(self):
        songs = self.pages[self.current_page]
        description = ""
        for i, song in enumerate(songs):
            index = (self.current_page * 5) + i + 1
            description += f"`{index}.` {song['title']}\n"

        embed = discord.Embed(title="📜 Fila de Músicas", description=description, color=discord.Color.blue())
        embed.set_footer(text=f"Página {self.current_page + 1} de {len(self.pages)}")
        return embed

    @discord.ui.button(label="⬅️ Voltar", style=discord.ButtonStyle.gray)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Próximo ➡️", style=discord.ButtonStyle.gray)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.create_embed(), view=self)
        else:
            await interaction.response.defer()

def setup_queue_command(bot):
    @bot.command(name="queue", aliases=["q", "fila"])
    async def queue(ctx):
        state = song_queues.get(ctx.guild.id)
        
        if not state or not state['queue']:
            if state and state['current']:
                return await ctx.send("A fila tá vazia.")
            return await ctx.send("A fila tá mais vazia que meu bolso ze.")

        queue_list = state['queue']
        pages = [queue_list[i:i + 5] for i in range(0, len(queue_list), 5)]
        
        current_msg = f"🎶 **Tocando agora:** {state['current']['title']}\n\n" if state['current'] else ""
        
        view = QueueView(ctx.guild.id, pages)
        embed = view.create_embed()
        embed.description = current_msg + embed.description

        if len(pages) <= 1:
            view.clear_items()
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=embed, view=view)
