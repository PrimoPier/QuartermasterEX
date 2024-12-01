import discord

def embed_IDerror1():
    embed = discord.Embed(
        title="❌ Error!",
        description="An ID is not required when adding an award!\n\n"
                    "`/award-data add` takes the following parameters:\n"
                    "`name` `description`",
        color=discord.Color.from_rgb(255,0,0)
    )
    return embed

def embed_descerror1():
    embed = discord.Embed(
        title="❌ Error!",
        description="A description is required when adding an award!\n\n"
                    "`/award-data add` takes the following parameters:\n"
                    "`name` `description`",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    return embed

def embed_IDerror2():
    embed = discord.Embed(
        title="❌ Error!",
        description="An ID is required to remove an award from the database!\n\n"
                    "`/award-data removes` takes the following parameters:\n"
                    "`name` `id`",
        color=discord.Color.from_rgb(255,0,0)
    )

def embed_descerror2():
    embed = discord.Embed(
        title="❌ Error!",
        description="A description is not required when removing an award from the database!\n\n"
                    "`/award-data removes` takes the following parameters:\n"
                    "`name` `id`",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    return embed

def embed_viewerror():
    embed = discord.Embed(
        title="❌ Error!",
        description="`/award-data view` takes no parameters!",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    return embed

def embed_terminated():
    embed = discord.Embed(
        title="❌ Process Terminated!",
        description="This action has been canceled.",
        color=discord.Color.from_rgb(255, 0, 0)
    )
    return embed

def embed_verifyerror():
    embed = discord.Embed(
        title="❌ Error!",
        description="You are not verified with the database!\n"
                    "Use `/verify` to verify yourself.",
        color=discord.Color.from_rgb(255,0,0)
    )
    return embed

def embed_rousererror():
    embed = discord.Embed(
        title="❌ Error!",
        description="Could not find your Roblox username. Ensure you are verified with RoVer and please try again later.",
        color=discord.Color.from_rgb(255,0,0)
    )
    return embed

def embed_rovererror():
    embed = discord.Embed(
        title="❌ Error!",
        description="There was an error verifying your account. Please contact a server administrator and try again later.",
        color=discord.Color.from_rgb(255,0,0)
    )
    return embed

def embed_removeerror():
    embed = discord.Embed(
        title="❌ Error!",
        description="No award found with that ID and/or name!",
        color=discord.Color.from_rgb(255,0,0)
    )
    return embed

def embed_help():
    embed = discord.Embed(
        title="Command List",
        description="**General Commands**\n"
                    "`/ping` - A simple ping command to test the bot's latency\n"
                    "`/verify` - Verifies a user with the database **(RoVer verification required)**\n"
                    "`/view [username]` - Shows awards achieved by a user\n"
                    "`/view [award]` - Shows a specific award, its description, and any recipients\n"
                    "`/award-data [view]` - Shows all awards in the awards database\n"
                    "`/help` - Brings up a list of all possible commands\n\n"
                    "**Administrative**\n"
                    "`/award-data [add/remove]` - Adds/removes awards from the database\n"
                    "`/award [user] [award] [description]` - Awards member(s) with an award.",
        color=discord.Color.from_rgb(168,67,0)
    )
    return embed

def embed_removeiderror():
    embed = discord.Embed(
        title="❌ Error!",
        description="An ID is required when removing an award from a user!",
        color=discord.Color.from_rgb(255,0,0)
    )
    return embed