from configparser import ConfigParser
import json
import asyncio
from datetime import date, datetime
import re
import telethon
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
import sys,os
from os import path
from PIL import Image
import numpy as np
from wordcloud_fa import WordCloudFa

from telethon.sessions import StringSession
from telethon.sync import TelegramClient,events
from telethon import sessions,types,Button
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (PeerChannel)

os.chdir(sys.path[0])
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
#_____________________________parse jason date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)
#_____________________________credentials
config = ConfigParser()
config.read('config.ini')

BOT_TOKEN = config['Telegram']['bot_token']
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
api_hash = str(api_hash)
#_____________________________bot + client creation

bot = TelegramClient('sessions/ses.session',api_id,api_hash).start(bot_token=BOT_TOKEN)
CLIENTS = {}
#_____________________________start
@bot.on(events.NewMessage(pattern='/start')) 
async def start(event):
    sender = await event.get_sender()
    SENDER = sender.id
    text = "Hello There!\n\n" +\
        "I am a bot to Scrape channel messages.\n"+\
        "You give me your information and I do the job.\n\n" +\
        "To start click on <b>/Scrape</b> \n"
    await bot.send_message(SENDER, text, parse_mode="HTML")
    raise events.StopPropagation
#_____________________________Scrape
def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)

@bot.on(events.NewMessage(pattern='/Scrape')) 
async def scrape(event):
    # get the sender
    sender = await event.get_sender()
    SENDER = sender.id


    async with bot.conversation(await event.get_chat(), exclusive=True) as conv:
        await conv.send_message('Please send your phone number in the given format:\n+123456789')
        response = await conv.get_response()
        phone = response.text
#_____________________________client
        client = TelegramClient('sessions/file{}'.format(SENDER),api_id,api_hash)
        
        await client.connect()
        await client.sign_in(phone)
        await conv.send_message("Now send me the code that telegram sent you to authorize!\n"
                                    "please follow the following format: 123Code123\n"
                                    "otherwise telegram will block your account")
        code = await conv.get_response()
        code = code.text
        code = int(code[3:8])
        print(phone,code)
        try:
            await client.sign_in(phone,code)
        except SessionPasswordNeededError:
            await conv.send_message('Please provide your two-step veification password to authorize')
            response = await conv.get_response()
            password = response.text
            password = password.format()
            await client.sign_in(password=password)
            CLIENTS['SENDER'] = SENDER
            print(CLIENTS)
        await conv.send_message("Perfect! you are authorized now.\n"
                                "Now please send me the channel url you want to scrape.")
        answer = 'Y'
        while (answer == 'Y'):
            channel = await conv.get_response()
            channel = channel.text
            
            user_input_channel = channel

            if user_input_channel.isdigit():
                entity = PeerChannel(int(user_input_channel))
            else:
                entity = user_input_channel

            my_channel = await client.get_entity(entity)

    #_____________________________ scraping
            all_msgs = []
            async for msg in client.iter_messages(my_channel,limit=500):
                if not msg.media or isinstance(msg.media,types.MessageMediaWebPage):
                    print(msg.text)
                    all_msgs.append(msg.text)
            with open('msgs.txt', 'w',encoding='utf-8') as f:
                f.write(str(all_msgs))
            myText = open('msgs.txt',mode='r',encoding='utf-8').read()
            result = re.sub(r'https?://\S+', '', myText)
    #_____________________________ English wordcloud
            
            mask = np.array(Image.open("customMask.png"))

            wc1 = WordCloud(background_color='rgba(255, 255, 255, 0)', mode="RGBA", max_words=500,
                            contour_width=3, contour_color='steelblue')

            wc1.generate(result)
            wc1.to_file("Englishfront.png")

            # Front Image
            filename = 'Englishfront.png'
            # Back Image
            filename1 = 'back.png'
            
            frontImage = Image.open(filename)
            background = Image.open(filename1)
            frontImage = frontImage.convert("RGBA")
            background = background.convert("RGBA")
            
            # Calculate to be at the center
            width = (background.width - frontImage.width) // 2
            height = (background.height - frontImage.height) // 2

            background.paste(frontImage, (width, height), frontImage)
 
            background.save("English_New.png", format="png")
    #_____________________________  Persian wordcloud
            wc = WordCloudFa(background_color='white', max_words=500,mask=mask,
                            contour_width=3, contour_color='steelblue')

            wc.generate(result)
            wc.to_file("frontPersian.png")

            # Front Image
            filename = 'frontPersian.png'
            # Back Image
            filename1 = 'back.png'
        
            frontImage = Image.open(filename)
            background = Image.open(filename1)
            frontImage = frontImage.convert("RGBA")
            background = background.convert("RGBA")
            
            # Calculate to be at the center
            width = (background.width - frontImage.width) // 2
            height = (background.height - frontImage.height) // 2

            background.paste(frontImage, (width, height), frontImage)
 
            background.save("Persian_New.png", format="png")
    #_____________________________ language choice 
            Keyboard = [[Button.inline('Persian',data=b'persian')],[Button.inline('English',data=b'english')]]
            await conv.send_message('please select a language',buttons=Keyboard)
            press = await conv.wait_event(press_event(SENDER))
            if press and press.data:
                if press.data == b'persian':
                    await conv.send_message('You chose Persian')
                    await conv.send_file('Persian_New.png')
                    # Handle Persian language here
                elif press.data == b'english':
                    await conv.send_message('You chose English')
                    await conv.send_file('English_New.png')
#_____________________________ continue or not
            Keyboard2 = [[Button.inline('Yes',data=b'yes')],[Button.inline('No',data=b'no')]]
            await conv.send_message('Do you want to continue?',buttons=Keyboard2)
            press = await conv.wait_event(press_event(SENDER))
            if press and press.data:
                if press.data == b'yes':
                    answer = 'Y'
                    await conv.send_message('Please provide another channel url')
                elif press.data == b'no':
                    await conv.send_message('See you!\nBye')
                    answer = 'no'
                    
#_____________________________
        raise events.StopPropagation
    
print('Bot started')
def main():
    """Start the bot."""
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
   