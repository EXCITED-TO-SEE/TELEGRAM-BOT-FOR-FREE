import json
import telebot
from telebot import apihelper
from telebot import types
from telebot import util as _util
from decouple import config
from translate import Translator
from weather import getCurrentWeather
from telebot import types,util
from googletrans import Translator

BOT_TOKEN = config("BOT_TOKEN")
bot= telebot.TeleBot(BOT_TOKEN)

weather = ["weather","temp","temprature"]
greetings = ["hello","hi","hey"]
whoAreYou = ["who","what"]
botName = "my bot name"

bot_data={
    "name" : ["my bot name"]
}

text_messages={
    "welcome": "welcome to xxxx Telegram group",
    "welcomeNewMember" : 
                u"Hey, you{name} in our private group",
    "saying goodbye":
                u"the member{name} left the group",

    "leave":"I have been added to a group other than the group I was designed for, bye🧐",
    "call" : "how can I help ?😀",
    "warn": u"❌ I have used {name} One of the forbidden words ❌\n"
            u" 🔴 you have left {safeCounter} Chances are, if the number is exceeded, you will be expelled 🔴",
    "kicked": u"👮‍♂️⚠ The member has been kicked out {name} ID owner {username} For violating one of the group rules👮‍♂️⚠"           
}

commands = {
    "translate":["translate"]
}
def handleNewUserData(message):
    id = str(message.new_chat_member.user.id)
    name = message.new_chat_member.user.first_name
    username =  message.new_chat_member.user.username

    with open("data.json","r") as jsonFile:
        data = json.load(jsonFile)
    jsonFile.close()
    
    users = data["users"]
    if id not in users:
        print("new user detected !")
        users[id] = {"safeCounter":5}
        users[id]["username"] = username
        users[id]["name"] = name
        print("new user data saved !")

    data["users"] = users
    with open("data.json","w") as editedFile:
        json.dump(data,editedFile,indent=3)
    editedFile.close()    

def handleOffensiveMessage(message):
    id = str(message.from_user.id)
    name = message.from_user.first_name
    username =  message.from_user.username
    
    with open("data.json","r") as jsonFile:
        data = json.load(jsonFile)
    jsonFile.close()
    
    users = data["users"]
    if id not in users:
        print("new user detected !")
        users[id] = {"safeCounter":5}
        users[id]["username"] = username
        users[id]["name"] = name
        print("new user data saved !")

    for index in users:
        if index == id :
            print("guilty user founded !")
            users[id]["safeCounter"] -= 1

    safeCounterFromJson = users[id]["safeCounter"]
    if safeCounterFromJson == 0:
        bot.kick_chat_member(message.chat.id,id)
        users.pop(id)
        bot.send_message(message.chat.id,text_messages["kicked"].format(name=name , username = username))
    else:
        bot.send_message(message.chat.id,text_messages["warn"].format(name=name , safeCounter = safeCounterFromJson))

    data["users"] = users
    with open("data.json","w") as editedFile:
        json.dump(data,editedFile,indent=3)
    editedFile.close()

    return bot.delete_message(message.chat.id,message.message_id)
       
@bot.message_handler(commands=["start"])
def startBot(message):
    bot.send_message(message.chat.id,text_messages["welcome"])

#answering every message not just commands
def isMSg(message):
    return True


@bot.message_handler(func=isMSg)
def reply(message):
    words = message.text.split()
    if words[0].lower() in weather :
        report = getCurrentWeather()
        return bot.send_message(message.chat.id,report or "failed to get weather !!")
    if words[0].lower() in whoAreYou :
        return bot.reply_to(message,f"i am {botName}")
    if words[0].lower() in greetings :
        return bot.reply_to(message,"hey how is going!")
    else:
        return bot.reply_to(message,"that's not a command of mine!")


#* saying Welcome to joined members
#* saying goodbye to left members
@bot.chat_member_handler()
def handleUserUpdates(message:types.ChatMemberUpdated):
    newResponse = message.new_chat_member
    if newResponse.status == "member":
        handleNewUserData(message=message)
        bot.send_message(message.chat.id,text_messages["welcomeNewMember"].format(name=newResponse.user.first_name))
    if newResponse.status == "left":
        bot.send_message(message.chat.id,text_messages["saying goodbye"].format(name=newResponse.user.first_name))


#* leave anychat thats not mine
@bot.my_chat_member_handler()
def leave(message:types.ChatMemberUpdated):
    update = message.new_chat_member
    if update.status == "member":
        bot.send_message(message.chat.id,text_messages["leave"])
        bot.leave_chat(message.chat.id)


#* listening to group messages
#* respond to bot name
@bot.message_handler(func=lambda m:True)
def reply(message):
    words = message.text.split()
    if words[0] in bot_data["name"]:
        bot.reply_to(message,text_messages["call"])
    
#* adding googletrans api
#* translating word to arabic
#* translating sentence to arabic
    if words[0] in commands["translate"]:
        translator = Translator()
        translation = translator.translate(" ".join(words[1:]),dest="ar")
        bot.reply_to(message,translation.text)

#* : checking if any word in message is offensive print("offensive")
#* : creating a data json file reading/writing 
#* : saving users info from message (id,name,username)
#* : adding safeCounter data to each user safeCounter = TRIES
#* : kick chat member that break the rules

bot.infinity_polling(allowed_updates=util.update_types)
