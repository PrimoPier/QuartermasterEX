import discord

class confirmView(discord.ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        await interaction.response.edit_message(view=None)
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        await interaction.response.edit_message(view=None)
        self.stop()