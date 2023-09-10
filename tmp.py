import configparser
import json
import asyncio
from datetime import date, datetime
import sys,os
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from wordcloud_fa import WordCloudFa
import re
from urllib.parse import urlparse

from telethon import TelegramClient,functions,types
import telethon
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt


os.chdir(sys.path[0])
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()



myText = open('msgs.txt',mode='r',encoding='utf-8').read()

result = re.sub(r'https?://\S+', '', myText)


wc = WordCloudFa(background_color='rgba(255, 255, 255, 0)', mode="RGBA", max_words=500,
                contour_width=10,stopwords=STOPWORDS)

wc.generate(result)

wc.to_file("front.png")
  

  
# Front Image
filename = 'front.png'
  
# Back Image
filename1 = 'back.png'
  
# Open Front Image
frontImage = Image.open(filename)
  
# Open Background Image
background = Image.open(filename1)
  
# Convert image to RGBA
frontImage = frontImage.convert("RGBA")
  
# Convert image to RGBA
background = background.convert("RGBA")
  
# Calculate width to be at the center
width = (background.width - frontImage.width) // 2
  
# Calculate height to be at the center
height = (background.height - frontImage.height) // 2
  
# Paste the frontImage at (width, height)
background.paste(frontImage, (width, height), frontImage)
  
# Save this image
background.save("new.png", format="png")
# show
# plt.imshow(wc, interpolation='bilinear')
# plt.axis("off")
# plt.figure()
# plt.imshow(mask, cmap=plt.cm.gray, interpolation='bilinear')
# plt.axis("off")
# plt.show()
