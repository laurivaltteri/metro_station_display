# Main script for polling stuff for display
# -*- coding: utf-8 -*-
from twitter import Api
import pychromecast
import spotipy, spotipy.util
from time import sleep, strftime, strptime, gmtime, mktime
from serial import Serial, SEVENBITS, STOPBITS_ONE, PARITY_EVEN
from random import randint
import re

## GLOBAL VARS
STX = chr(2); ETX = chr(3); EOT = chr(4); ENQ = chr(5); PAD = chr(127)
SLP = 1

## SET TWITTER API
# https://apps.twitter.com/app/*yourappno*/keys
config ={"consumer_key":  *yourkeys*,
    "consumer_secret": *yourkeys*,
    "access_key": *yourkeys*,
    "access_secret": *yourkeys*}

api = Api(config["consumer_key"], config["consumer_secret"],
    config["access_key"], config["access_secret"])

## CHECK FOR CHROMECASTS
chromecasts = pychromecast.get_chromecasts()
shortnames = {"YouTube": "Tube", "Yle Areena": "Yle", "HBO Nordic": "HBO",
    "Netflix": "Flix"}

## SET SPOTIFY API (first time you need to give the app to rights to the scope)
# Adding rights to scope you need to follow the prompt protocol from spotipy doc
SPOTIPY_CLIENT_ID = *yourkeys*
SPOTIPY_CLIENT_SECRET = *yourkeys*
token = spotipy.util.prompt_for_user_token("ahonenlauri",
    "user-read-currently-playing", client_id = SPOTIPY_CLIENT_ID,
    client_secret = SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth=token)

## SET SERIAL PORT
ser = Serial("/dev/ttyUSB0", 600, SEVENBITS, PARITY_EVEN, STOPBITS_ONE)

## ----------------

## FUNCTIONS
def send_ser(linestr):
    padline = PAD + PAD + linestr + PAD + PAD
    ser.write(bytearray(padline, encoding = "ascii"))

def write_line(message, seg):
    send_ser(EOT)
    sleep(SLP)
    send_ser("01" + ENQ) # address (from dip switches)
    sleep(SLP)

    if seg == 3:
        send_ser(STX + "32000blT" + clear_scands(message) + ETX + "p")
    elif seg == 2 and len(message) < 22:
        send_ser(STX + "22000nrT" + clear_scands(message) + ETX + "p")
    elif seg == 1 and len(message) < 22:
        send_ser(STX + "12000nrT" + clear_scands(message) + ETX + "p")
    elif len(message) > 21:
        spaces = [m.start(0) for m in re.finditer(u' ', message)]
        spaces = [x - len(message) for x in spaces]
        spltidx = [i for i in spaces if i > -22]
        if len(message) > 41 and len(spltidx) > 0:
            send_ser(STX + "12000nrT" + clear_scands(u'..'+message[spltidx[0]-19:spltidx[0]]) + ETX + "p")
        elif len(spltidx) > 0:
            send_ser(STX + "12000nrT" + clear_scands(message[spltidx[0]-20:spltidx[0]]) + ETX + "p")
        else:
            send_ser(STX + "12000nrT" + clear_scands(message[-41:-21]) + ETX + "p")
        send_ser(EOT)
        sleep(SLP)
        send_ser(EOT)
        sleep(SLP)
        send_ser("01" + ENQ) # address (from dip switches)
        sleep(SLP)
        if len(spltidx) > 0:
            send_ser(STX + "22000nlT" + clear_scands(message[spltidx[0]+1:]) + ETX + "p")
        else:
            send_ser(STX + "22000nlT" + clear_scands(message[-21:]) + ETX + "p")
    else:
        print "nothing send to serial"
    send_ser(EOT)
    sleep(SLP)

def clear_scands(message):
    message = message.replace(u'ä', chr(123))
    message = message.replace(u'ö', chr(124))
    message = message.replace(u'å', chr(125))
    message = message.replace(u'Ä', chr(91))
    message = message.replace(u'Ö', chr(92))
    message = message.replace(u'Å', chr(93))
    message = message.replace(u'ü', chr(126))
    message = message.replace(u'Ü', chr(94))
    return message

def default_disp():
    # WRITE INFO
    write_line("Tweet", 3)

    # TWITTER TRENDS
    # WOE_ID for Finland not existing
    # api.GetTrendsWoeid(23424954) # Sweden
    ctrnd = api.GetTrendsCurrent()
    ctrnd = list(iter(cc for cc in ctrnd if all(ord(c) < 128 for c in cc.name)))
    twtrln = ctrnd[randint(0,9)].name
    write_line(twtrln, 1)

    # DATE
    dayn = int(strftime("%d"))
    if dayn == 1:
        dayn = "1st"
    elif dayn == 2:
        dayn = "2nd"
    elif dayn == 3:
        dayn = "3rd"
    else:
        dayn = str(dayn)+"th"

    dateln = strftime("%a ") + dayn + strftime(" of %b, %Y")
    write_line(dateln, 2)

def cast_info(mc,dname):
    if dname in shortnames:
        msource = shortnames[dname]
    else:
        msource = dname
    write_line(msource, 3)
    sleep(SLP)
    if dname == "Netflix":
        write_line("Netflix and chill", 1)
        return
    else:
        write_line(mc.title, 1)

    if mc.artist:
        write_line(mc.artist, 2)
    elif 'item' in mc.media_custom_data:
        write_line(mc.media_custom_data['item']['title'], 2)
    elif u'subtitle' in mc.media_metadata:
        write_line(mc.media_metadata[u'subtitle'], 2)

def spotify_info(sitem):
    artist = sitem['item']['artists'][0]['name']
    song = sitem['item']['name']
    write_line("Sptfy", 3)
    write_line(song, 1)
    write_line(artist, 2)

def disp_message(message):
    write_line("Msg", 3)
    write_line(message, 1)


while 1:
    #print(u'ok')
    metweet = api.GetSearch("#metronäyttö",since = strftime("%Y-%m-%d",gmtime()))
    if len(metweet) > 0:
        mtime = strptime(metweet[0].created_at, '%a %b %d %H:%M:%S +0000 %Y')
        if mktime(gmtime()) - mktime(mtime) < 3600:
            metweet = metweet[0].text.split(": ",1)[1]
            metweet = metweet.replace("#metronäyttö","")
            disp_message(metweet.text)

    if sp.currently_playing() != None:
        if sp.currently_playing()['is_playing']==True:
            spotify_info(sp.currently_playing())
        else:
            for cc in chromecasts:
                cc.wait()
                mc = cc.media_controller.status
                if mc.player_state == u'PLAYING':
                    cast_info(mc, cc.status.display_name)
                else:
                    default_disp()
    else:
        for cc in chromecasts:
            cc.wait()
            mc = cc.media_controller.status
            if mc.player_state == u'PLAYING':
                cast_info(mc, cc.status.display_name)
            else:
                default_disp()
    sleep(SLP)
