import warnings

import discord
import os
from discord import app_commands
from src import responses

isPrivate = False
isReplyAll: bool = False


class aclient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/chat | /help")


async def send_message(message, user_message):
    global isReplyAll
    if not isReplyAll:
        author = message.user.id
        await message.response.defer(ephemeral=isPrivate)
    else:
        author = message.author.id
    try:
        response = '> **' + user_message + '** - <@' + \
                   str(author) + '> \n\n'

        response = f"{response}{await responses.official_handle_response(user_message)}"

        char_limit = 1900
        if len(response) > char_limit:
            # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
            if "```" in response:
                # Split the response if the code block exists
                parts = response.split("```")

                for i in range(0, len(parts)):
                    if i % 2 == 0:  # indices that are even are not code blocks
                        if isReplyAll:
                            await message.channel.send(parts[i])
                        else:
                            await message.followup.send(parts[i])

                    # Send the code block in a seperate message
                    else:  # Odd-numbered parts are code blocks
                        code_block = parts[i].split("\n")
                        formatted_code_block = ""
                        for line in code_block:
                            while len(line) > char_limit:
                                # Split the line at the 50th character
                                formatted_code_block += line[:char_limit] + "\n"
                                line = line[char_limit:]
                            formatted_code_block += line + "\n"  # Add the line and seperate with new line

                        # Send the code block in a separate message
                        if (len(formatted_code_block) > char_limit + 100):
                            code_block_chunks = [formatted_code_block[i:i + char_limit]
                                                 for i in range(0, len(formatted_code_block), char_limit)]
                            for chunk in code_block_chunks:
                                if isReplyAll:
                                    await message.channel.send("```" + chunk + "```")
                                else:
                                    await message.followup.send("```" + chunk + "```")
                        else:
                            if isReplyAll:
                                await message.channel.send("```" + formatted_code_block + "```")
                            else:
                                await message.followup.send("```" + formatted_code_block + "```")

            else:
                response_chunks = [response[i:i + char_limit]
                                   for i in range(0, len(response), char_limit)]
                for chunk in response_chunks:
                    if isReplyAll:
                        await message.channel.send(chunk)
                    else:
                        await message.followup.send(chunk)
        else:
            if isReplyAll:
                await message.channel.send(response)
            else:
                await message.followup.send(response)
    except Exception as e:
        if isReplyAll:
            await message.channel.send("> **Error: Something went wrong, please try again later!**")
        else:
            await message.followup.send("> **Error: Something went wrong, please try again later!**")
        raise Exception(f"Error while sending message: {e}")


async def send_start_prompt(client):
    import os.path

    config_dir = os.path.abspath(__file__ + "/../../")
    prompt_name = 'starting-prompt.txt'
    prompt_path = os.path.join(config_dir, prompt_name)
    discord_channel_id = os.getenv("DISCORD_CHANNEL_ID") or os.getenv("APPSETTING_DISCORD_CHANNEL_ID")
    try:
        if os.path.isfile(prompt_path) and os.path.getsize(prompt_path) > 0:
            with open(prompt_path, "r") as f:
                prompt = f.read()
                if (discord_channel_id):
                    print(f"Send starting prompt with size {len(prompt)}")
                    response = ""

                    response = f"{response}{await responses.official_handle_response(prompt)}"

                    channel = client.get_channel(int(discord_channel_id))
                    await channel.send(response)
                    print(f"Starting prompt response:{response}")
                else:
                    print("No Channel selected. Skip sending starting prompt.")
        else:
            print(f"No {prompt_name}. Skip sending starting prompt.")
    except Exception as e:
        raise Exception(f"Error while sending starting prompt: {e}")


def run_discord_bot():
    client = aclient()

    @client.event
    async def on_ready():
        await send_start_prompt(client)
        await client.tree.sync()
        print(f'{client.user} is now running!')

    @client.tree.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        global isReplyAll
        if isReplyAll:
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **Warn: You already on replyAll mode. If you want to use slash command, switch to normal mode, use `/replyall` again**")
            warnings.warn("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        user_message = message
        channel = str(interaction.channel)
        print(
            f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
        await send_message(interaction, user_message)

    @client.tree.command(name="private", description="Toggle private access")
    async def private(interaction: discord.Interaction):
        global isPrivate
        await interaction.response.defer(ephemeral=False)
        if not isPrivate:
            isPrivate = not isPrivate
            warnings.warn("\x1b[31mSwitch to private mode\x1b[0m")
            await interaction.followup.send(
                "> **Info: Next, the response will be sent via private message. If you want to switch back to public mode, use `/public`**")
        else:
            print("You already on private mode!")
            await interaction.followup.send(
                "> **Warn: You already on private mode. If you want to switch to public mode, use `/public`**")

    @client.tree.command(name="public", description="Toggle public access")
    async def public(interaction: discord.Interaction):
        global isPrivate
        await interaction.response.defer(ephemeral=False)
        if isPrivate:
            isPrivate = not isPrivate
            await interaction.followup.send(
                "> **Info: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
            warnings.warn("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **Warn: You already on public mode. If you want to switch to private mode, use `/private`**")
            print("You already on public mode!")

    @client.tree.command(name="replyall", description="Toggle replyAll access")
    async def replyall(interaction: discord.Interaction):
        global isReplyAll
        await interaction.response.defer(ephemeral=False)
        if isReplyAll:
            await interaction.followup.send(
                "> **Info: The bot will only response to the slash command `/chat` next. If you want to switch back to replyAll mode, use `/replyAll` again.**")
            warnings.warn("\x1b[31mSwitch to normal mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **Info: Next, the bot will response to all message in the server. If you want to switch back to normal mode, use `/replyAll` again.**")
            warnings.warn("\x1b[31mSwitch to replyAll mode\x1b[0m")
        isReplyAll = not isReplyAll

    @client.tree.command(name="reset", description="Complete reset ChatGPT conversation history")
    async def reset(interaction: discord.Interaction):

        responses.official_chatbot.reset()

        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **Info: I have forgotten everything.**")
        warnings.warn("\x1b[31mChatGPT bot has been successfully reset\x1b[0m")
        await send_start_prompt(client)

    @client.tree.command(name="help", description="Show help for the bot")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("""\n:star:**BASIC COMMANDS** \n
        - `/chat [message]` Chat with ChatGPT!
        - `/public` ChatGPT switch to public mode
        - `/replyall` ChatGPT switch between replyall mode and default mode
        - `/reset` Clear ChatGPT conversation history""")
        print("\x1b[31mSomeone need help!\x1b[0m")

    @client.event
    async def on_message(message):
        if isReplyAll:
            if message.author == client.user:
                return
            username = str(message.author)
            user_message = str(message.content)
            channel = str(message.channel)
            print(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
            await send_message(message, user_message)

    token = os.getenv("DISCORD_BOT_TOKEN") or os.getenv("APPSETTING_DISCORD_BOT_TOKEN")

    client.run(token)
