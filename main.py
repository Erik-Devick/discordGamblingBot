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
            ["Game","coinflip",">coinflip <bet> <side>","bet on the outcome of a coin flip"],
            ["Game","baccarat",">baccarat <bet> <side>","play a game of baccarat"]]
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

#baccarat
@bot.command()
async def baccarat(ctx, bet, side):
    user = ctx.author.display_name
    payout = bet

    #make sure side is valid
    if side != "banker" and side != "player":
        await ctx.send("```Invalid side. Valid sides are 'player', 'banker'.```")
        return

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

    def calcHand(hand):
        numHand = []
        for card in hand:
            if card in ['A','J','Q','K']:
                numHand.append(faceToNum[card])
            else:
                numHand.append(card)
        return sum(numHand)%10
    
    def handToString(hand):
        output = ""
        for card in hand:
            output += f"{str(card)}, "
        output = output[:-2]
        return output

    #begin game
    deck = ['A',1,2,3,4,5,6,7,8,9,10,'J','Q','K']*4
    random.shuffle(deck)
    faceToNum = {'A':1,'J':10,'Q':10,'K':10}
    playerHand = []
    bankerHand = []

    #initial deal
    playerHand.append(deck.pop())
    bankerHand.append(deck.pop())
    playerHand.append(deck.pop())
    bankerHand.append(deck.pop())

    await ctx.send(f"```Initial deal:\nPlayer hand: {handToString(playerHand)} = {calcHand(playerHand)}\nBanker hand: {handToString(bankerHand)} = {calcHand(bankerHand)}```")

    #check for natural win
    natural = False
    if (calcHand(playerHand) == 8 or calcHand(playerHand) == 9) and (calcHand(bankerHand) == 8 or calcHand(bankerHand)== 9):
        await ctx.send("```Natural tie!```")
        natural = True
        winner = "tie"
    elif (calcHand(playerHand) == 8 or calcHand(playerHand) == 9) and (calcHand(bankerHand)!=8 and calcHand(bankerHand)!=9):
        await ctx.send("```Natural win for player!```")
        natural = True
        winner = "player"
    elif (calcHand(bankerHand) == 8 or calcHand(bankerHand) == 9) and (calcHand(playerHand)!=8 and calcHand(playerHand)!=9):
        await ctx.send("```Natural win for banker!```")
        natural = True
        winner = "banker"

    if not natural:
        time.sleep(1)
        #check for player third card
        if calcHand(playerHand) <= 5:
            playerHand.append(deck.pop())
            await ctx.send(f"```Player dealt third card:\nPlayer hand: {handToString(playerHand)} = {calcHand(playerHand)}```")
        else:
            await ctx.send("```Players stays```")

        time.sleep(1)
        #check for banker third card
        playerScore = calcHand(playerHand)
        bankerScore = calcHand(bankerHand)
        if playerScore == 8 and bankerScore <= 2:
            bankerHand.append(deck.pop())
            await ctx.send(f"```Banker dealt third card:\nBanker hand: {handToString(bankerHand)} = {calcHand(bankerHand)}```")
        elif (playerScore == 6 or playerScore == 7) and bankerScore <= 6:
            bankerHand.append(deck.pop())
            await ctx.send(f"```Banker dealt third card:\nBanker hand: {handToString(bankerHand)} = {calcHand(bankerHand)}```")
        elif (playerScore == 4 or playerScore == 5) and bankerScore <= 5:
            bankerHand.append(deck.pop())
            await ctx.send(f"```Banker dealt third card:\nBanker hand: {handToString(bankerHand)} = {calcHand(bankerHand)}```")
        elif (playerScore == 2 or playerScore == 3) and bankerScore <= 4:
            bankerHand.append(deck.pop())
            await ctx.send(f"```Banker dealt third card:\nBanker hand: {handToString(bankerHand)} = {calcHand(bankerHand)}```")
        elif (playerScore == 0 or playerScore == 1 or playerScore == 9) and bankerScore <= 3:
            bankerHand.append(deck.pop())
            await ctx.send(f"```Banker dealt third card:\nBanker hand: {handToString(bankerHand)} = {calcHand(bankerHand)}```")
        else:
            await ctx.send("```Banker stays```")

        time.sleep(1)
        await ctx.send(f"```Final hands:\nPlayer hand: {handToString(playerHand)} = {calcHand(playerHand)}\nBanker hand: {handToString(bankerHand)} = {calcHand(bankerHand)}```")

        #decide winner
        bankerScore = calcHand(bankerHand)
        playerScore = calcHand(playerHand)
        if bankerScore == playerScore:
            winner = "tie"
        elif bankerScore > playerScore:
            winner = "banker"
        elif bankerScore < playerScore:
            winner = "player"
    
    await ctx.send(f"```WINNER: {winner}!```")

    #determine payment
    if winner == "tie":
        payout = float(bet)*1.5
    elif side == winner:
        payout = float(bet)*2
    else:
        payout = 0

    #update balance
    users[user] = float(users[user])+float(payout)
    users[user] = format(users[user],".2f")
    await ctx.send(f"```New balance: ${users[user]}```")

    #save balance
    with open("users.json", "w") as file:
        json.dump(users, file)
    
    


bot.run(os.getenv("token").strip())