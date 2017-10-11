
# coding=utf-8
from serial import Serial, SEVENBITS, STOPBITS_ONE, PARITY_EVEN
from time import sleep


ser = Serial("/dev/ttyUSB0", 600, SEVENBITS, PARITY_EVEN, STOPBITS_ONE)
#ser = Serial("/dev/cu.UC-232AC", 600, SEVENBITS, PARITY_EVEN, STOPBITS_ONE)
STX = chr(2); ETX = chr(3); EOT = chr(4); ENQ = chr(5); PAD = chr(127)

addr = "01" # low bit says write
def wr(x):
        #oput = bytearray([c for c in PAD + PAD + x + PAD + PAD])
        oput = [c for c in PAD + PAD + x PAD + PAD]
        byten = ser.write(oput)

        print oput
        print byten

slp = 1 # sometimes even smaller works, sometimes need to retry with this
message = "Perrrrjantai\nIHQ!! IHQ!!"
message = message.replace("ä", chr(123))
message = message.replace("ö", chr(124))
message = message.replace("å", chr(125))
message = message.replace("Ä", chr(91))
message = message.replace("Ö", chr(92))
message = message.replace("Å", chr(93))
message = message.replace("&lt;", "<")
message = message.replace("&gt;", ">")
message = message.replace("&amp;", "&")
message = message.replace("ü", chr(126))
message = message.replace("Ü", chr(94))
rows = message.split('\n')
while 1:
    # display text immediately 1st row
    # version?
    # sbn: text type
    # lrmz: left right middle something
    wr(EOT)
    sleep(slp)
    wr(addr + ENQ)
    sleep(slp)
    # row = b'1' # 1=top, 2=bottom, 3=clock
    # side = b'2' # wtf?
    # # b=caps, s=big spaces, n=big text
    #wr(STX + NULL + "1" + "007" + "E" + "4" + "2" + NULL + "3" + "RL30" + ETX + "p")
    wr(STX + "12000nrT" + rows[0] + ETX + "p")
    wr(EOT)
    # display text immediately 2nd row
    sleep(slp)

    wr(EOT)
    sleep(slp)
    wr(addr + ENQ)
    sleep(slp)

    wr(STX + "22000nrT" + rows[1] + ETX + "p")
    wr(EOT)
    # sleep(slp)

    wr(EOT)
    sleep(slp)
    wr(addr + ENQ)
    sleep(slp)
    # wr(addr + ENQ)
    # sleep(slp)
    row = "3" # 1=top, 2=bottom, 3=clock
    side = "2"
    # # b=caps, s=big spaces, n=big text
    wr(STX + row + side + "000blT" + "HBO" + ETX + "p")
    wr(EOT)

    wr(EOT)
    sleep(slp)
    wr(addr + ENQ)
    sleep(slp)

    n = "01" # default (timeout)
    ver = "004"
    site = "2" # 1=one side blinks in a broken way, 2=both work, 3=no clock on other side
    secs = "42"
    traingfx = "16"
    wr(STX + "x" + site + ver + "xxE" + secs + traingfx + n + n + "RL30" + ETX + "p")
    wr(EOT)
    sleep(slp)
