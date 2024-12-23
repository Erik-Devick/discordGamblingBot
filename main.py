import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import random
import os
import time
from table2ascii import table2ascii as t2a



load_dotenv()

#what bot can do
intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True

#make bot instance
bot = commands.Bot(command_prefix=">",intents=intents,help_command=None)


@bot.command(name="help")
async def help(ctx):
    header = ["Category","Command","Example","Description"]
    welcome = "Welcome to the casino! If you haven't already, please register by typing '>register'."
    body = [["User","help",">help","Displays this message"],
            ["User","register",">register","Creates account for user balance"],
            ["User","balance",">balance","Display user balance"],
            ["User","reset",">reset","Resets balance to $1000.00"],
            ["User","leaderboard",">leaderboard","Displays all users sorted by balance"],
            ["Game","highlow",">highlow <bet>","plays the higher or lower game"],
            ["Game","coinflip",">coinflip <bet> <side>","bet on the outcome of a coin flip"]]
    helpTable = t2a(header=header,body=body)
    await ctx.send(f"```{welcome}\n{helpTable}```")

#register user
@bot.command()
async def register(ctx):
    user = ctx.author.display_name
    try:
        with open("users.json") as file:
            users = json.load(file)
    except (json.JSONDecodeError):
        users = {}

    if user in users.keys():
        await ctx.send(f"```You are already registered.\nBalance: ${users[user]}```")
    else:
        users[user] = format(1000,".2f")
        with open("users.json", "w") as file:
            json.dump(users, file)
        await ctx.send("```You are now registered.\nBalance: $1000.00```")

#check balance
@bot.command()
async def balance(ctx):
    user = ctx.author.display_name
    try:
        with open("users.json") as file:
            users = json.load(file)
    except (json.JSONDecodeError):
        await ctx.send("```You are not registered. Please type '>register'.```")
        return
    if user in users.keys():
        await ctx.send(f"```Balance: ${users[user]}```")
    else:
        await ctx.send("```You are not registered```")

#Coin flip
@bot.command()
async def coinflip(ctx, bet, side):
    user = ctx.author.display_name
    outcome = random.choice(["heads", "tails"])

    #make sure user is registered
    try:
        with open("users.json") as file:
            users = json.load(file)
    except (json.JSONDecodeError):
        await ctx.send("```You are not registered. Please type '>register'.```")
        return
    if user not in users.keys():
        await ctx.send("```You are not registered. Please type '>register'.```")
        return
    
    #check if user has enough money
    if float(users[user]) < float(bet):
        await ctx.send("```You do not have enough money```")
        return
    
    #check if side is valid
    if side != "heads" and side != "tails":
        await ctx.send("```Invalid side```")
        return
    
    #update balance
    users[user] = float(users[user])-float(bet)
    users[user] = format(users[user],".2f")

    #check if user won and update balance
    if side == outcome:
        users[user] = float(users[user])+(2*float(bet))
        users[user] = format(users[user],".2f")
        await ctx.send(f"```You won!\nNew balance: ${users[user]}```")
    else:
        await ctx.send(f"```You lost!\nNew balance: ${users[user]}```")


    #save balance
    with open("users.json", "w") as file:
        json.dump(users, file)

#higher or lower
@bot.command()
async def highlow(ctx, bet):
    startNumber = random.randint(1, 100)
    user = ctx.author.display_name
    isCorrect = True
    payout = bet

    #make sure user is registered
    try:
        with open("users.json") as file:
            users = json.load(file)
    except (json.JSONDecodeError):
        await ctx.send("```You are not registered. Please type '>register'.```")
        return
    if user not in users.keys():
        await ctx.send("```You are not registered. Please type '>register'.```")
        return
    
    #check if user has enough money
    if float(users[user]) < float(bet):
        await ctx.send("```You do not have enough money```")
        return
    
    #update balance
    users[user] = float(users[user])-float(bet)
    users[user] = format(users[user],".2f")

    #begin game
    await ctx.send("```You will have 10 seconds to make your guess of higher or lower.\nNumbers are between 1 and 100.```")
    time.sleep(2)
    while isCorrect:
        await ctx.send(f"```Will the next number be higher or lower than {startNumber}?```")
        def check(m):
            return m.author == ctx.author
        
        try:
            validGuess = False
            while not validGuess:
                guess = await bot.wait_for("message", check=check, timeout=10)
                if guess.content in ["higher","lower"]:
                    validGuess = True
                if not validGuess:
                    await ctx.send("Invalid guess, please enter 'higher' or 'lower'.")
            newNumber = random.randint(1,100)
            if (newNumber > startNumber and guess.content.lower() == "higher") or (newNumber < startNumber and guess.content.lower() == "lower"):
                
                startNumber = newNumber
                payout = format(float(payout)*2,".2f")
                await ctx.send(f"```Correct! The number was {newNumber}\nCurrent payout: ${payout}\nContinue? (yes/no)```")
                try:
                    validResponse = False
                    while not validResponse:
                        cont = await bot.wait_for("message", check=check, timeout=10)
                        if cont.content in ["yes","no"]:
                            validResponse = True
                        if not validResponse:
                            await ctx.send("```Invalid response please enter 'yes' or 'no'.```")
                    if cont.content.lower() == "no":
                        break
                    else:
                        continue
                except:
                    await ctx.send(f"```You took too long to respond\nNew balance: ${users[user]}```")
                    return

            else:
                await ctx.send(f"```Incorrect! Number was {newNumber}.```")
                payout = 0
                isCorrect = False
        except:
            await ctx.send(f"```You took too long to respond.\nNew balance: ${users[user]}```")
            return
    
    #update balance
    users[user] = float(users[user])+float(payout)
    users[user] = format(users[user],".2f")
    await ctx.send(f"```New balance: ${users[user]}```")

    #save balance
    with open("users.json", "w") as file:
        json.dump(users, file)

#reset balance
@bot.command() 
async def reset(ctx):
    user = ctx.author.display_name

    #make sure user is registered
    try:
        with open("users.json") as file:
            users = json.load(file)
    except (json.JSONDecodeError):
        await ctx.send("```You are not registered. Please type '>register'```")
        return
    if user not in users.keys():
        await ctx.send("```You are not registered. Please type '>register'```")
        return
    
    #make sure
    await ctx.send("```Are you sure you want to reset your balance? (yes/no)```")
    def check(m):
        return m.author == ctx.author
    try:
        response = await bot.wait_for("message", check=check, timeout=10)
        if response.content not in ["yes", "no"]:
            await ctx.send("```Balance reset cancelled```")
            return
        elif response.content.lower() != "yes":
            await ctx.send("```Balance reset cancelled```")
            return
        else:
            users[user] = format(1000,".2f")
            with open("users.json", "w") as file:
                json.dump(users, file)
            await ctx.send("```Balance reset\nNew balance: $1000.00```")
    except:
        await ctx.send("```You took too long to respond\nBalance reset Cancelled```")
        return

#leaderboard
@bot.command()
async def leaderboard(ctx):
    try:
        with open("users.json") as file:
            users = json.load(file)
    except (json.JSONDecodeError):
        await ctx.send("```No users registered```")
        return
    
    sorted_users = sorted(users.items())
    body = [list(pair) for pair in sorted_users]
    for i in range(len(body)):
        body[i].insert(0, i+1)
        body[i][2] = f"${body[i][2]}"
    header = ["Rank", "User", "Balance"]

    table = t2a(header=["Rank","User","Balance"],
                body=body)
    
    await ctx.send(f"```{table}```")


bot.run(os.getenv("token").strip())