from typing import Final

import discord
import os
import main
import embeds # Error embeds file
import buttons # Embed confirmation buttons
import mysql.connector
import aiomysql
import aiohttp
import re
from discord.ext import commands, pages
from discord import Intents
from discord.commands import Option
from dotenv import load_dotenv
load_dotenv()

GUILDS: Final[str] = os.getenv('DISCORD_GUILDS')
ROVER_API: Final[str] = os.getenv('ROVER_API')
intents: Intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

class commandList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="ping",
        description="A simple ping command.",
        guild_ids=[GUILDS]
    )
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(title="Pong! 🏓", description=(f"Latency: `{latency}ms`!"), color=discord.Color.from_rgb(255,0,0))
        await ctx.respond(embed=embed, ephemeral=False)

    @discord.slash_command(
        name="help",
        description="Brings up a list of all possible commands.",
        guild_ids=[GUILDS]
    )
    async def help(self, ctx):
        embed = embeds.embed_help()
        await ctx.respond(embed=embed, ephemeral=False)

    @discord.slash_command(
        name="verify",
        description="Verify yourself with the database.",
        guild_ids=[GUILDS]
    )
    async def verify(self, ctx):
        discord_id = ctx.author.id
        # print(discord_id)
        rover_url = f"https://registry.rover.link/api/guilds/{GUILDS}/discord-to-roblox/{discord_id}"
        headers = {"Authorization": f"Bearer {ROVER_API}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(rover_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print("API Response:", data)
                    roblox_username = data.get('cachedUsername')

                    if roblox_username:
                        conn = await aiomysql.connect(**main.uscmc_db)
                        async with conn.cursor() as cursor:
                            # Check if user exists
                                await cursor.execute(
                                    "SELECT COUNT(*) FROM members WHERE discord_id = %s",
                                    (discord_id,)
                                )
                                count = await cursor.fetchone()

                                if count[0] == 0:
                                    # Insert new user
                                    await cursor.execute(
                                        "SELECT MAX(member_id) FROM members"
                                    )
                                    max_member_id = await cursor.fetchone()
                                    new_member_id = (max_member_id[0] or 0) + 1

                                    await cursor.execute(
                                        "INSERT INTO members (member_id, discord_id, roblox_username) VALUES (%s, %s, %s)",
                                        (new_member_id, discord_id, roblox_username)
                                    )
                                    print(f"Inserted new user: {discord_id} with username: {roblox_username}")
                                    embed = discord.Embed(title="✅ Success!", color=discord.Color.from_rgb(0,255,0), description="User verified: "
                                                                                                                                 f"`{roblox_username}`")
                                    await ctx.respond(embed=embed, ephemeral=False)
                                else:
                                    # Update existing user
                                    await cursor.execute(
                                        "UPDATE members SET roblox_username = %s WHERE discord_id = %s",
                                        (roblox_username, discord_id)
                                    )
                                    print(f"Updated existing user: {discord_id} with new username: {roblox_username}")
                                    embed = discord.Embed(title="✅ Success!", color=discord.Color.from_rgb(0, 255, 0), description="User verified: "
                                                                                                                                   f"`{roblox_username}`")
                                    await ctx.respond(embed=embed, ephemeral=False)

                                await conn.commit()
                    else:
                        embed = embeds.embed_rousererror()
                        await ctx.respond(emebed=embed, ephemeral=False)
                else:
                    error_message = f"Failed to verify account, HTTP status: {response.status}"
                    print(error_message)
                    embed = embeds.embed_rovererror()
                    await ctx.respond(embed=embed, ephemeral=False)

    @discord.slash_command(
        name="award-data",
        description="Add or remove awards from the database.",
        guild_ids=[GUILDS]
    )
    async def award(self, ctx,
                    action: Option(str, "Choose an action", choices=["add", "remove", "view"]),
                    name: Option(str, "The name of the award being added/removed.", required=False),
                    description: Option(str, "The description of the award being added.", required=False),
                    id: Option(int, "The ID of the award being removed.", required=False)
                    ):
        # Required role ID's
        role_perms = ["Test HIGHCOMM"]
        author = ctx.author
        has_role = any(role.name in role_perms for role in author.roles)

        try:
            if action in ["add", "remove"] and not has_role:
                embed = discord.Embed(title="❌ Error!", description="User does not have the required roles!",
                                      color=discord.Color.from_rgb(255, 0, 0))
                await ctx.respond(embed=embed, ephemeral=False)
                return

            if action == "add":
                if id is not None:
                    embed = embeds.embed_IDerror1()
                    await ctx.respond(embed=embed, ephemeral=False)
                    return

                if description is None:
                    embed = embeds.embed_descerror1()
                    await ctx.respond(embed=embed, ephemeral=False)
                    return

                uscmc_db_conn = mysql.connector.connect(**main.uscmc_db)
                cursor = uscmc_db_conn.cursor()
                # Insert data
                add_award = ("INSERT INTO awards "
                            "(award_name, award_description) "
                            "VALUES (%s, %s)")
                data_award = (name, description)

                view = buttons.confirmView()
                embed = discord.Embed(title="⚠️ Confirmation Required", color=discord.Color.yellow(), description="Are you sure you would like to add the following:\n\n"
                                                                                                                  f"`{name}` -\n"
                                                                                                                  f"`{description}`")
                confirmation_message = await ctx.respond(embed=embed, view=view, ephemeral=False)
                await view.wait() # Wait for user interaction

                if view.value is None:
                    await confirmation_message.edit(embed=embeds.embed_terminated(), view=None)
                elif view.value:
                    cursor.execute(add_award, data_award)
                    uscmc_db_conn.commit()

                    award_id = cursor.lastrowid
                    embed = discord.Embed(title="✅ Success!", color=discord.Color.from_rgb(0,255,0), description=f"Award added:\n\n"
                                                                                                                        f"**ID:** `{award_id}`\n"
                                                                                                                        f"`{name}`\n"
                                                                                                                        f"`{description}`")
                    await ctx.respond(embed=embed, ephemeral=False)

                    # Close connections
                    cursor.close()
                    uscmc_db_conn.close()
                    return

            elif action == "remove":
                if id is None:
                    embed = embeds.embed_IDerror2()
                    await ctx.respond(embed=embed, ephemeral=False)
                    return

                if description is not None:
                    embed = embeds.embed_descerror2()
                    await ctx.respond(embed=embed, ephemeral=False)
                    return

                uscmc_db_conn = mysql.connector.connect(**main.uscmc_db)
                cursor = uscmc_db_conn.cursor()

                cursor.execute("SELECT * FROM awards WHERE award_id = %s", (id,))
                removed_award = cursor.fetchone()
                # print("Fetched award from database:", removed_award)

                if removed_award:
                    award_id, award_name, award_description = removed_award

                    embed = discord.Embed(title="⚠️ Confirmation Required", color=discord.Color.yellow(), description="Are you sure you would like to remove the following:\n\n"
                                                                                                                      f"`{award_name}` -\n"
                                                                                                                      f"`{award_description}`")
                    view = buttons.confirmView()
                    confirmation_message = await ctx.respond(embed=embed, view=view, ephemeral=False)
                    await view.wait()

                    if view.value is None:
                        await confirmation_message.edit(embed=embeds.embed_terminated(), view=None)
                    elif view.value:
                        # Remove data on id
                        remove_award = ("DELETE FROM awards WHERE award_id = %s")
                        cursor.execute(remove_award, (id,))

                        # Retrieve all with greater id
                        cursor.execute("SELECT award_id FROM awards WHERE award_id > %s", (id,))
                        higher_ids = cursor.fetchall()

                        # Decrement ids of awards above removed
                        for higher_id in higher_ids:
                            new_id = higher_id[0] - 1
                            update_award = ("UPDATE awards SET award_id = %s WHERE award_id = %s")
                            cursor.execute(update_award, (new_id, higher_id[0]))

                    uscmc_db_conn.commit()
                    embed = discord.Embed(title="✅ Success!", color=discord.Color.from_rgb(0, 255, 0), description=f"Award removed:\n\n"
                                                                                                                             f"`{award_name}` -\n"
                                                                                                                             f"`{award_description}`")
                    await ctx.respond(embed=embed, ephemeral=False)
                else:
                    embed = embeds.embed_removeerror()
                    await ctx.respond(embed=embed, ephemeral=False)

                # Close connections
                cursor.close()
                uscmc_db_conn.close()
                return

            elif action == "view":
                if name is not None or description is not None or id is not None:
                    embed = embeds.embed_viewerror()
                    await ctx.respond(embed=embed, ephemeral=False)
                    return

                with mysql.connector.connect(**main.uscmc_db) as conn:
                    with conn.cursor() as cursor:
                        # Check if verified
                        # cursor.execute("SELECT * FROM members WHERE discord_id = %s", (discord_id,))
                        # result = cursor.fetchone()
                        result = True

                        # If verified, view awards database
                        if result:
                            # Retrieve all
                            cursor.execute("SELECT award_id, award_name, award_description FROM awards ORDER BY award_id")
                            awards = cursor.fetchall()

                            embeds_list = []
                            for i in range(0, len(awards), 5):
                                embed = discord.Embed(title="Awards Database", color=discord.Color.from_rgb(168,67,0))
                                for award in awards[i:i+10]:
                                    embed.add_field(name=f"ID: `{award[0]}`", value=f"{award[1]}\n- *{award[2]}*", inline=False)
                                embeds_list.append(embed)

                            paginator = pages.Paginator(pages=embeds_list)
                            await paginator.respond(ctx.interaction, ephemeral=False)
                            return
                        else:
                            embed = embeds.embed_verifyerror()
                            await ctx.respond(embed=embed, ephemeral=False)
                            return

        except mysql.connector.Error as e:
            embed = discord.Embed(title="❌ Error!", description=f"System error: `{e}`", color=discord.Color.from_rgb(255, 0, 0))
            await ctx.respond(embed=embed, ephemeral=False)

    @discord.slash_command(
        name="award",
        description="Award members.",
        guild_ids=[GUILDS]
    )
    async def award_member(self, ctx,
                           users: Option(str, "The Roblox username of the persons being awarded."),
                           awards: Option(str, "The name of the awards being given."),
                           description: Option(str, "Optional description detailing the reason for the award.", default="No reason specified"),
                           remove: Option(bool, "Set to 'true' to remove the award.", default=False),
                           id: Option(int, "The specified ID of the award to be removed.", default=None)
                           ):
        users_list = users.split()
        awards_list = re.findall(r"`([^`]*)`|\b(\w+)\b", awards)
        awards_list = [a[0] or a[1] for a in awards_list]
        print("Parsed awards list: ", awards_list)

        # Required role ID's
        role_perms = ["Test HIGHCOMM"]
        author = ctx.author
        has_role = any(role.name in role_perms for role in author.roles)

        if not has_role:
            embed = discord.Embed(title="❌ Error!", description="User does not have the required roles!", color=discord.Color.from_rgb(255, 0, 0))
            await ctx.respond(embed=embed, ephemeral=False)
            return

        # Duplicate awards
        multi_awards = ["Navy Cross",
                        "Silver Star",
                        "Bronze Star",
                        "Vanguard Medal",
                        "Exceptional Service Medal",
                        "Exceptional Leadership Medal",
                        "Exceptional Host Medal",
                        "Rear Guard Medal",
                        "Purple Heart Medal"]

        # Connect to the database
        uscmc_db_conn = mysql.connector.connect(**main.uscmc_db)
        cursor = uscmc_db_conn.cursor()

        try:
            for award in awards_list:
                print(f"Processing award: {award}")
                # Find award_id from award
                cursor.execute("SELECT award_id FROM awards WHERE award_name = %s", (award,))
                award_result = cursor.fetchone()
                # print(f"Query executed for award '{award}'")
                # print(f"Query result for {award}: {award_result}")

                if not award_result:
                    embed = discord.Embed(title="❌ Error!", description=f"Award with name `{award}` not found!", color=discord.Color.from_rgb(255, 0, 0))
                    await ctx.respond(embed=embed, ephemeral=False)
                    continue

                award_id = award_result[0]

                for user in users_list:
                    print(f"Processing user: {user}")
                    # Find member_id from user
                    cursor.execute("SELECT member_id FROM members WHERE roblox_username = %s", (user,))
                    member_result = cursor.fetchone()

                    if not member_result:
                        embed = discord.Embed(title="❌ Error!", description=f"Member with Roblox username `{user}` not found!", color=discord.Color.from_rgb(255, 0, 0))
                        await ctx.respond(embed=embed, ephemeral=False)
                        continue

                    member_id = member_result[0]

                    # Check if member has this award
                    cursor.execute("SELECT * FROM member_awards WHERE member_id = %s AND award_id = %s", (member_id, award_id))
                    award_ids = cursor.fetchall()

                    if remove:
                        if id is None:
                            embed = embeds.embed_removeiderror()
                            await ctx.respond(embed=embed, ephemeral=False)
                            return

                        # Verify ID matches award name
                        cursor.execute("SELECT award_id FROM member_awards WHERE id = %s", (id,))
                        id_result = cursor.fetchone()

                        if not id_result:
                            embed = discord.Embed(title="❌ Error!", description="The ID provided does not exist.", color=discord.Color.from_rgb(255, 0, 0))
                            await ctx.respond(embed=embed, ephemeral=False)
                            return

                        id_award_id = id_result[0]

                        if id_award_id != award_id:
                            embed = discord.Embed(title="❌ Error!", description=f"The ID `{id}` does not match the award `{award}`!", color=discord.Color.from_rgb(255, 0, 0))
                            await ctx.respond(embed=embed, ephemeral=False)
                            return

                        view = buttons.confirmView()
                        embed = discord.Embed(title="⚠️ Confirmation Required", color=discord.Color.yellow(), description=f"Are you sure you would like to remove the following from `{user}`?\n\n"
                                                                                                                          f"`{awards}`")
                        confirmation_message = await ctx.respond(embed=embed, view=view, ephemeral=False)
                        await view.wait()

                        if view.value is None:
                            await confirmation_message.edit(embed=embeds.embed_terminated(), view=None)
                            return

                        if view.value:
                            cursor.execute("DELETE FROM member_awards WHERE id = %s", (id,))
                            uscmc_db_conn.commit()

                            embed = discord.Embed(title="✅ Success!", color=discord.Color.from_rgb(0, 255, 0), description=f"`{award}` removed from `{user}`:\n\n"
                                                                                                                           f"`{description}`")
                            await ctx.respond(embed=embed, ephemeral=False)
                    else:
                        view = buttons.confirmView()
                        embed = discord.Embed(title="⚠️ Confirmation Required", color=discord.Color.yellow(), description=f"Are you sure you would like to **award** the following to {user}?\n\n"
                                                                                                                          f"`{awards}`\n"
                                                                                                                          f"`{description}`")
                        confirmation_message = await ctx.respond(embed=embed, view=view, ephemeral=False)
                        await view.wait()

                        if view.value is None:
                            await confirmation_message.edit(embed=embeds.embed_terminated(), view=None)
                            return

                        if view.value:
                            if award_ids and award not in multi_awards:
                                embed = discord.Embed(title="❌ Error!", description=f"`{user}` already has the award `{awards}`!", color = discord.Color.from_rgb(255, 0, 0))
                                await ctx.respond(embed=embed, ephemeral=False)
                            else:
                                # Insert award into member_awards
                                add_award = ("INSERT INTO member_awards (member_id, award_id) VALUES (%s, %s)")
                                cursor.execute(add_award, (member_id, award_id))
                                uscmc_db_conn.commit()

                                embed = discord.Embed(title="✅ Success!", color=discord.Color.from_rgb(0, 255, 0), description=f"`{awards}` distributed to `{user}`:\n\n"
                                                                                                                               f"`{description}`")
                                await ctx.respond(embed=embed, ephemeral=False)

        except mysql.connector.Error as e:
            embed = discord.Embed(title="❌ Error!", description=f"System error: `{e}`", color=discord.Color.from_rgb(255, 0, 0))
            await ctx.respond(embed=embed, ephemeral=False)
        finally:
            cursor.close()
            uscmc_db_conn.close()

    @discord.slash_command(
        name="view",
        description="View a user's awards.",
        guild_ids=[GUILDS]
    )
    async def view(self, ctx,
                   user: Option(str, "The Roblox username of the user to view.", required=False),
                   award: Option(str, "The name of the award to view.", required=False)
                   ):
        # Connect to the database
        uscmc_db_conn = mysql.connector.connect(**main.uscmc_db)
        cursor = uscmc_db_conn.cursor()

        try:
            if award:
                # Fetch award details
                cursor.execute("""
                    SELECT award_id, award_name, award_description
                    FROM awards
                    WHERE award_name = %s
                """, (award,))
                award_result = cursor.fetchone()

                if not award_result:
                    embed = discord.Embed(title="❌ Error!", description=f"Award `{award}` not found!", color=discord.Color.from_rgb(255, 0, 0))
                    await ctx.respond(embed=embed, ephemeral=False)
                    return

                award_id, award_name, award_description = award_result

                # Fetch users with specified award
                cursor.execute("""
                    SELECT m.roblox_username, ma.date_awarded
                    FROM member_awards ma
                    JOIN members m ON ma.member_id = m.member_id
                    JOIN awards a ON ma.award_id = a.award_id
                    WHERE a.award_name = %s
                    ORDER BY ma.date_awarded DESC
                """, (award,))

                users_awards = cursor.fetchall()

                embed = discord.Embed(title=f"`{award_id}` {award_name}", color=discord.Color.from_rgb(168,67,0))
                embed.add_field(name="**Description**", value=f"- *{award_description}*", inline=False)

                if not users_awards:
                    embed.add_field(name="Users Achieved", value="`No users have received this award`", inline=False)
                else:
                    users_lists = "\n".join([f"{username}, *Date Awarded:* {date_awarded.strftime('%Y-%m-%d')}" for username, date_awarded in users_awards])
                    embed.add_field(name="Users Achieved", value=users_lists, inline=False)

                    await ctx.respond(embed=embed, ephemeral=False)
            else:
                if not user:
                    cursor.execute("SELECT roblox_username FROM members WHERE discord_id = %s", (ctx.author.id,))
                    member_result = cursor.fetchone()

                    if not member_result:
                        embed = discord.Embed(title="❌ Error!", description="Please verify with RoVer as well as QuartermasterEX, and try again.", color=discord.Color.from_rgb(255, 0, 0))
                        await ctx.respond(embed=embed, ephemeral=False)
                        return

                    user = member_result[0]

                # Find member_id from user
                cursor.execute("SELECT member_id FROM members WHERE roblox_username = %s", (user,))
                member_result = cursor.fetchone()

                if not member_result:
                    embed = discord.Embed(title="❌ Error!", description=f"Member with Roblox username `{user}` not found!", color=discord.Color.from_rgb(255, 0, 0))
                    await ctx.respond(embed=embed, ephemeral=False)
                    return

                member_id = member_result[0]

                # Fetch all awards for member
                cursor.execute("""
                                SELECT ma.id, a.award_name, a.award_description, ma.date_awarded 
                                FROM awards a
                                JOIN member_awards ma ON a.award_id = ma.award_id
                                WHERE ma.member_id = %s
                                ORDER BY ma.date_awarded DESC
                            """, (member_id,))

                awards = cursor.fetchall()

                embed = discord.Embed(title=f"{user}'s Awards", color=discord.Color.from_rgb(168,67,0))

                if not awards:
                    embed.description = "`This user has no awards`"
                    await ctx.respond(embed=embed, ephemeral=False)
                else:
                    embeds_list = []
                    # Add awards to embed
                    for i in range(0, len(awards), 15):
                        for award_id, award_name, award_description, date_awarded in awards:
                            formatted_date = date_awarded.strftime("%Y-%m-%d")
                            embed.add_field(name=f"`{award_id}` {award_name}", value=f"*Date Awarded:* {formatted_date}", inline=False)
                        embeds_list.append(embed)

                    paginator = pages.Paginator(pages=embeds_list)
                    await paginator.respond(ctx.interaction, ephemeral=False)
                    return

        except mysql.connector.Error as e:
            embed = discord.Embed(title="❌ Error!", description=f"System error: `{e}`", color=discord.Color.from_rgb(255, 0, 0))
            await ctx.respond(embed=embed, ephemeral=False)
        finally:
            cursor.close()
            uscmc_db_conn.close()

def setup(bot):
    bot.add_cog(commandList(bot))