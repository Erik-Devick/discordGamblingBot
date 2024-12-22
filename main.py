import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import random
import os
import time



load_dotenv()

#what bot can do
intents = discord.Intents.default()
intents.guild_messages = True
intents.message_content = True

#make bot instance
bot = commands.Bot(command_prefix=">",intents=intents)



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
        await ctx.send("You are already registered")
        await ctx.send(f"Balance: ${users[user]}")
    else:
        users[user] = 1000
        with open("users.json", "w") as file:
            json.dump(users, file)
        await ctx.send("You are now registered.")
        await ctx.send("Balance: $1000")

#check balance
@bot.command()
async def balance(ctx):
    user = ctx.author.display_name
    try:
        with open("users.json") as file:
            users = json.load(file)
    except (json.JSONDecodeError):
        await ctx.send("You are not registered")
        return
    if user in users.keys():
        await ctx.send(f"Balance: ${users[user]}")
    else:
        await ctx.send("You are not registered")

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
        await ctx.send("You are not registered")
        return
    if user not in users.keys():
        await ctx.send("You are not registered")
        return
    
    #check if user has enough money
    if users[user] < int(bet):
        await ctx.send("You do not have enough money")
        return
    
    #check if side is valid
    if side != "heads" and side != "tails":
        await ctx.send("Invalid side")
        return
    
    #update balance
    users[user] -= int(bet)

    #check if user won and update balance
    if side == outcome:
        users[user] += 2*int(bet)
        await ctx.send(f"You won!")
        await ctx.send(f"New balance: ${users[user]}")
    else:
        await ctx.send(f"You lost!")
        await ctx.send(f"New balance: ${users[user]}")


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
        await ctx.send("You are not registered")
        return
    if user not in users.keys():
        await ctx.send("You are not registered")
        return
    
    #check if user has enough money
    if users[user] < int(bet):
        await ctx.send("You do not have enough money")
        return
    
    #update balance
    users[user] -= int(bet)

    #begin game
    await ctx.send("You will have 10 seconds to make your guess between numbers.")
    time.sleep(1)
    while isCorrect:
        await ctx.send(f"Current number: {startNumber}. Higher or lower?")
        def check(m):
            return m.author == ctx.author
        
        try:
            guess = await bot.wait_for("message", check=check, timeout=10)
            newNumber = random.randint(1, 100)
            if guess.content not in ["higher", "lower"]:
                await ctx.send("Invalid guess. Please enter 'higher' or 'lower'")
                continue
            elif (newNumber > startNumber and guess.content.lower() == "higher") or (newNumber < startNumber and guess.content.lower() == "lower"):
                await ctx.send(f"Correct! New number: {newNumber}")
                startNumber = newNumber
                payout = int(payout)*2
                await ctx.send(f"Current payout: ${payout}. Continue?")
                try:
                    cont = await bot.wait_for("message", check=check, timeout=10)
                    if cont.content not in ["yes", "no"]:
                        await ctx.send("Invalid response. Please enter 'yes' or 'no'")
                        continue
                    elif cont.content.lower() == "no":
                        break
                    else:
                        print("here")
                        continue
                except:
                    await ctx.send("You took too long to respond")
                    await ctx.send(f"New balance: ${users[user]}")
                    return

            else:
                await ctx.send(f"Incorrect! Number was {newNumber}")
                payout = 0
                isCorrect = False
        except:
            await ctx.send("You took too long to respond")
            await ctx.send(f"New balance: ${users[user]}")
            return
    
    #update balance
    users[user] += payout
    await ctx.send(f"New balance: ${users[user]}")

    



bot.run(os.getenv("token").strip())