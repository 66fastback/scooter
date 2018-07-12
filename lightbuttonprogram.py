#!/usr/bin/env python
# Andrew Renz Jan 16, 2017
#lots of help from PHDJ Sep
#lights and sounds. 
 
import os
import time
import RPi.GPIO as GPIO
from bibliopixel.led import LEDStrip
from bibliopixel.animation import AnimationQueue
from bibliopixel.drivers.APA102 import DriverSPIBase, ChannelOrder, DriverAPA102
from BiblioPixelAnimations.strip import HalvesRainbow, LarsonScanners, LinearRainbow, Rainbows, FireFlies, ColorFade, ColorPattern, ColorChase, ColorWipe
import bibliopixel.colors as colors
import random as random
import subprocess
import threading
import math

# from bibliopixel import log
# log.setLogLevel(log.DEBUG)

# STRIP SETTINGS
FPS = 24
STPS = (FPS * 30)
SPI = 2
NUMPIX = 30

# COLORS
RAINBOW = [colors.Red, colors.Orange, colors.Yellow, colors.Green, colors.Blue, colors.Indigo, colors.Violet]
RED = [colors.Red]
GREEN = [colors.Green]

# HARDWARE SETTINGS
MAIN_PIN = 17
DRIVER = DriverAPA102(NUMPIX, c_order = ChannelOrder.BGR, use_py_spi = True, dev="/dev/spidev0.0", SPISpeed = SPI)
LED = LEDStrip(DRIVER)

# GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(MAIN_PIN, GPIO.IN)

# GLOBAL VARIABLES

# Helper Functions
				
class animation(object):
	def __init__(self):
		self.anim = AnimationQueue(LED)
		mylarson = {} #should really turn this into a class too
		for i in range(0,12):
			a = i
			mylarson[a] = LarsonScanners.LarsonScanner(LED, color = colors.hue2rgb(random.randint(0,255)), tail = 2, start = 0, end = NUMPIX)
			self.anim.addAnim(mylarson[a],fps = 26, max_steps = 165) #stuff goes haywire when max steps isnt 3.5, 5.5 or 7.5 times NUMPIX
		rain = Rainbows.Rainbow(LED)
		self.anim.addAnim(rain, fps = FPS, max_steps = STPS)
		mychase = {}
		for i in range(0,11):
			a = i
			mychase[a] = ColorChase.ColorChase(LED, color = colors.hue_helper(random.randint(1,255), 100, 10), width = 2)
			self.anim.addAnim(mychase[a],fps = FPS, max_steps= FPS * 2)
		halves = HalvesRainbow.HalvesRainbow(LED)
		self.anim.addAnim(halves,amt = 1, fps = FPS, max_steps = STPS + 10)
 		pattern=ColorPattern.ColorPattern(LED, RAINBOW, 2)
		self.anim.addAnim(pattern,amt = 1, fps = FPS / 2, max_steps = FPS * 30)
		linear = LinearRainbow.LinearRainbow(LED, max_led = -1, individual_pixel=True)
		self.anim.addAnim(linear,fps = FPS, max_steps = STPS)
		fade = ColorFade.ColorFade(LED, RAINBOW, step = 10)
		self.anim.addAnim(fade,fps = FPS, max_steps = STPS + 10)
		fire = FireFlies.FireFlies(LED, RAINBOW, width = 2, count = 4)
		self.anim.addAnim(fire,fps = 4, max_steps = 4 * 6)
		mywipe = {}
		for i in range(0,11):
			a = i
			mywipe = ColorWipe.ColorWipe(LED, color=colors.hue_helper(random.randint(1, 255), 100, 20))
			self.anim.addAnim(mywipe,fps = FPS, max_steps = FPS * 2)
		rainCycle = Rainbows.RainbowCycle(LED)
		self.anim.addAnim(rainCycle,fps = FPS * 3, max_steps = STPS *4)
		
	def runShow(self):
		self.anim.run(fps = 30, max_steps=1, untilComplete=True)	
		self.anim.stopThread()
		return

	def runShowIdle(self):
		if self.anim.stopped():
			self.anim.run(fps = 30, threaded=True)	
		
	def stopShow(self):
		self.anim.stopThread()
		
	def isStopped(self):
		return self.anim.stopped()

def runstuff(loops): #resets GPIO for callback sounds and loops led show 
	current = 0
#	print "starting program with ", loops, " 5 min loops"
	while current < loops:
		GPIO.remove_event_detect(MAIN_PIN)
		time.sleep(1)
		GPIO.add_event_detect(MAIN_PIN,GPIO.RISING,callback = playsound, bouncetime=15000)
		#long bouncetime to limit simultaneous sound playback
		#bouncetime must be greater than duration of soundfile or will repeat
		time.sleep(1)
		ledshow=animation()
		ledshow.runShow()
		current = current + 1
	endshow()

def endshow():
	GPIO.remove_event_detect(MAIN_PIN)
	LED.fillRGB(255, 0, 0)
	LED.update()
	time.sleep(0.1)
	return

def flash(num, color, len):
	i = 0
	while i < num:
		LED.all_off()
		LED.update()
		LED.fill(color)
		LED.update()
		time.sleep(len)
		LED.all_off()
		LED.update()
		i = i + 1
		time.sleep(len)

def playsound(channel):
# 	import pdb; pdb.set_trace()
	LED.fillRGB(255, 0, 0)
	LED.update()
	soundfile="/boot/sounds/" + str(random.randint(1, 6)) + ".wav"
	command = ['aplay']
	command.append(soundfile)
 	(out,err) = subprocess.Popen(command,stdout = subprocess.PIPE,stderr = subprocess.PIPE).communicate()

# Start the program
try:
	num = 0
	numberpressed = 0
	numberlong = 0
	global idle
	idle=animation()
	idle.runShowIdle()
	while numberpressed < 5:
		GPIO.wait_for_edge(MAIN_PIN, GPIO.RISING, bouncetime = 200)
		#wait for gpio button push
		numberpressed += 1
		idle.stopShow() #stop led idle show
		time.sleep(0.1)
		LED.all_off()
		LED.update()
# 		flasher = threading.Thread(target = flash, args = (1, colors.Violet, .5),)
# 		flasher.start()
# 		flasher.join()
		start = time.time() #start timing button push
		while GPIO.input(MAIN_PIN) == GPIO.LOW:
			time.sleep (0.1)
# 			LED.fill(colors.Violet)
# 			LED.update()
			#loop while button pushed
		length = time.time() - start #record duration of button push
		if (length > 1) & (numberpressed >= 2): #continue to run show after long button push
			#carla had me change this to two seconds. 
			numberlong += 1
			time.sleep(.1)
			num = numberpressed - 1
			flasher = threading.Thread(target = flash, args = (num, colors.Green,.75), ) #should put this into a class...
			flasher.start()
			flasher.join()
			runstuff(num)
			numberpressed = 0
		else:
			if numberpressed < 5:
				time.sleep(0.1)
				LED.fill(colors.Blue, 0, numberpressed - 1)
				LED.update()
# 				flasher = threading.Thread(target = flash, args = (numberpressed, colors.Blue, .5 ), ) #should put this into a class...
# 				flasher.start()
# 				flasher.join()
		if numberpressed >= 5:
			numberpressed = 0
			LED.fill(colors.Red, 0, -1)
			LED.update()
# 			time.sleep(1)
# 			flasher = threading.Thread(target = flash, args = (3, colors.Red, .5), )
# 			flasher.start()
# 			flasher.join()
			idle=animation()
			if idle.isStopped():
				idle.runShowIdle() #restart led idle show
 		time.sleep(0.1)

# If CTRL+C is pressed, exit cleanly:
except KeyboardInterrupt: 
	idle.stopShow()
	GPIO.cleanup()
	LED.all_off()
	LED.update()
