import pyaudio
import sys
import numpy as np
import aubio

import pygame
import random

from threading import Thread

import queue
import time

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-input", required=False, type=int, help="Audio Input Device")
parser.add_argument("-f", action="store_true", help="Run in Fullscreen Mode")
args = parser.parse_args()

if not args.input:
    print("No input device specified. Printing list of input devices now: ")
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print("Device number (%i): %s" % (i, p.get_device_info_by_index(i).get('name')))
    print("Run this program with -input 1, or the number of the input you'd like to use.")
    exit()

pygame.init()

if args.f:
    # run in fullscreen
    screenWidth, screenHeight = 1920, 1280
    screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

else:
    # run in window
    screenWidth, screenHeight = 1020, 768
    screen = pygame.display.set_mode((screenWidth, screenHeight))


black = (35, 35, 35)

class Circle(object):
    def __init__(self, x, y, color, size):
        self.x = x
        self.y = y
        self.color = color
        self.size = size

    def shrink(self):
        self.size -= random.randint(8,12)

    def bigger(self):
        self.size+=8

def colorChooser(mix):
    red = random.randint(0,255)
    green = random.randint(0,255)
    blue = random.randint(0,255)

    redNew = (red+mix)/2
    greenNew = (green+mix)/2
    blueNew = (blue+mix)/2

    return (redNew, greenNew, blueNew)

def hexToRGB(hexString):
   try:
       hexTuple = tuple(int(hexString[i:i + 2], 16) for i in (0, 2, 4))
   except ValueError:
       hexTuple = (255,255,255)
   return hexTuple

def pageRead():
   import requests
   from bs4 import BeautifulSoup as bs
   import pprint
   import re
   page = requests.get("https://www.awwwards.com/trendy-web-color-palettes-and-material-design-color-schemes-tools.html")

   if str(page.status_code) == '400' or str(page.status_code) == '500':
       exit("probable error")

   soup = bs(page.content, 'html.parser')
   listOfTags = list(soup.find_all("span"))

   stringSearch = re.compile(r"\>#(.*?)\<")

   item = []

   for i in range(int(len(listOfTags))):
       listOfTags[i] = str(listOfTags[i])
       if listOfTags[i][0:23] == '<span class="ColorCube"':
           item.append(stringSearch.search(str(listOfTags[i])).group(1))

   for i in range(len(item)):
       item[i] = hexToRGB(item[i])

   itemList = []
   for i in range(int(len(item)/16)):
       itemList.append([item[i],item[i+1],item[i+2],item[i+3]])

   return itemList

colors = []
for i in range(5):
    colors.append(colorChooser(255))
circleList = []

# initialise pyaudio
p = pyaudio.PyAudio()

clock = pygame.time.Clock()

# open stream

buffer_size = 4096 # needed to change this to get undistorted audio
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 44100
stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                input_device_index=args.input,
                frames_per_buffer=buffer_size)



# setup onset detector
tolerance = 0.8
win_s = 4096 # fft size
hop_s = buffer_size // 2 # hop size
onset = aubio.onset("default", win_s, hop_s, samplerate)


q = queue.Queue()


allColors = pageRead()
allColors.append([hexToRGB('E27D60'),hexToRGB('085DCB'),hexToRGB('E8A87C'),hexToRGB('C38D9E'),hexToRGB('41B3A3')])
allColors.append([hexToRGB('05386B'),hexToRGB('379683'),hexToRGB('5CDB95'),hexToRGB('8EE4AF'),hexToRGB('EDF5E1')])
allColors.append([hexToRGB('F8E9A1'),hexToRGB('F76C6C'),hexToRGB('A8DOE6'),hexToRGB('374785'),hexToRGB('24305E')])
allColors.append([hexToRGB('5D001E'),hexToRGB('E3E2DF'),hexToRGB('E3AFBC'),hexToRGB('9A1750'),hexToRGB('EE4C7C')])
allColors.append([hexToRGB('FF6AD5'),hexToRGB('C774E8'),hexToRGB('AD8CFF'),hexToRGB('8795E8'),hexToRGB('94D0FF')])


def draw_pygame():
    running = True
    biggerCircles = True
    colorScheme = colors
    while running:
        key = pygame.key.get_pressed()

        if key[pygame.K_q]:
            running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(black)

        if key[pygame.K_z]:
            biggerCircles = True
        elif key[pygame.K_x]:
            biggerCircles = False

        if key[pygame.K_1]:
            colorScheme = allColors[0]
        elif key[pygame.K_2]:
            colorScheme = allColors[1]
        elif key[pygame.K_3]:
            colorScheme = allColors[2]
        elif key[pygame.K_4]:
            colorScheme = allColors[3]
        elif key[pygame.K_5]:
            colorScheme = allColors[4]
        elif key[pygame.K_6]:
            colorScheme = allColors[5]
        elif key[pygame.K_7]:
            colorScheme = allColors[6]
        elif key[pygame.K_8]:
            colorScheme = allColors[7]
        elif key[pygame.K_9]:
            colorScheme = allColors[8]
        elif key[pygame.K_0]:
            colorScheme = allColors[9]

        if not q.empty():
            b = q.get()
            if biggerCircles == True:

                newCircle = Circle(960, 640,colorScheme[random.randint(0,len(colorScheme)-1)], 200)
                circleList.append(newCircle)

            else:
                newCircle1 = Circle(random.randint(0,screenWidth), random.randint(0,screenHeight),
                                    colorScheme[random.randint(0,len(colorScheme)-1)], 300)
                circleList.append(newCircle1)

        if biggerCircles == True:

            for place, circle in enumerate(circleList):
                if circle.size >= 1310:
                    circleList.pop(place)
                else:
                    pygame.draw.circle(screen, circle.color, (circle.x, circle.y), circle.size)
                circle.bigger()
        else:

            for place, circle in enumerate(circleList):
                if circle.size < 1:
                    circleList.pop(place)
                else:
                    pygame.draw.circle(screen, circle.color, (circle.x, circle.y), circle.size)
                circle.shrink()


        pygame.display.flip()
        clock.tick(90)

def get_onsets():
    while True:
        try:
            buffer_size = 2048 # needed to change this to get undistorted audio
            audiobuffer = stream.read(buffer_size, exception_on_overflow=False)
            signal = np.fromstring(audiobuffer, dtype=np.float32)


            if onset(signal):
                q.put(True)

        except KeyboardInterrupt:
            print("*** Ctrl+C pressed, exiting")
            break


t = Thread(target=get_onsets, args=())
t.daemon = True
t.start()

draw_pygame()
stream.stop_stream()
stream.close()
pygame.display.quit()