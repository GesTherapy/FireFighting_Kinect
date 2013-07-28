import viz
import vizact
import vizshape
import math
import random
import time

viz.go(viz.FULLSCREEN)

import vizinfo
info = vizinfo.add( 'You can control water using your hand!\nHelp put out as many flames as you can in the next 30 seconds!\nPress SPACE to begin the activity.\nPress S to exit the activity.' )
info.translate( [.98, .3] )

# dojo, gallery, lab, maze, piazza, pit, sky_day, sky_night
ground = viz.add('lab.osgb')

#Kinect Tracker object ID's
HEAD = 0
NECK = 1
TORSO = 2
WAIST = 3
LEFTCOLLAR = 4
LEFTSHOULDER = 5
LEFTELBOW = 6
LEFTWRIST = 7
LEFTHAND = 8
LEFTFINGERTIP = 9
RIGHTCOLLAR = 10
RIGHTSHOULDER = 11
RIGHTELBOW = 12
RIGHTWRIST = 13
RIGHTHAND = 14
RIGHTFINGERTIP = 15
LEFTHIP = 16
LEFTKNEE = 17
LEFTANKLE = 18
LEFTFOOT = 19
RIGHTHIP = 20
RIGHTKNEE = 21
RIGHTANKLE = 22
RIGHTFOOT = 23

#store trackers
trackers = []

#start vrpn
vrpn = viz.addExtension('vrpn7.dle')

#now add all trackers
for i in range(0,24):
  t = vrpn.addTracker( 'Tracker0@localhost',i )
	trackers.append(t)

avatar = viz.add('Full_Body_Bip001\kinect_full_body.cfg', pos=[0, 0.8, 0], euler=[0, 0, 0])

RF = vrpn.addTracker('Tracker0@localhost', RIGHTFOOT)
LF = vrpn.addTracker('Tracker0@localhost', LEFTFOOT)
RK = vrpn.addTracker('Tracker0@localhost', RIGHTKNEE)
LK = vrpn.addTracker('Tracker0@localhost', LEFTKNEE)
Torso = vrpn.addTracker('Tracker0@localhost', TORSO)
head = vrpn.addTracker('Tracker0@localhost', HEAD)
neck = vrpn.addTracker('Tracker0@localhost', NECK)
rightShoulder = vrpn.addTracker('Tracker0@localhost', RIGHTSHOULDER)
rightElbow = vrpn.addTracker('Tracker0@localhost', RIGHTELBOW)
leftShoulder = vrpn.addTracker('Tracker0@localhost', LEFTSHOULDER)
leftElbow = vrpn.addTracker('Tracker0@localhost',LEFTELBOW)
rightHip = vrpn.addTracker('Tracker0@localhost',RIGHTHIP)
rightKnee = vrpn.addTracker('Tracker0@localhost',RIGHTKNEE)
leftHip = vrpn.addTracker('Tracker0@localhost',LEFTHIP)
leftKnee = vrpn.addTracker('Tracker0@localhost',LEFTKNEE)

waist = vrpn.addTracker('Tracker0@localhost', WAIST)
rootWaist = avatar.getBone('Bip001')
rootWaist.lock()

headBone = avatar.getBone('Bip01 Head')
headBone.lock()

kinectToCharacter = {	'Bip01 L UpperArm':(rightShoulder, [0, 90, 0]), \
'Bip01 L Forearm':(rightElbow, [0, 90, 0]), \
'Bip01 R UpperArm':(leftShoulder, [0, -90, 180]), \
'Bip01 R Forearm':(leftElbow, [0, -90, 180]), \
'Bip01 L Thigh':(rightHip, [90, 0, -90]), \
'Bip01 L Calf':(rightKnee, [90, 0, -90]), \
'Bip01 R Thigh':(leftHip, [90, 0, -90]), \
'Bip01 R Calf':(leftKnee, [90, 0, -90]), \
'Bip001':(waist, [0, 90, -90]) \
}

bones = {}
for boneName in kinectToCharacter:
	b = avatar.getBone(boneName)
	b.lock()
	bones[b] = kinectToCharacter[boneName]
	
import vizmat
def animate():
	for bone in bones:
		kinectTracker = bones[bone][0]
		euler = kinectTracker.getEuler()
		m = vizmat.Transform()
		m.setEuler(euler)
		m.preEuler(bones[bone][1])
		bone.setEuler(m.getEuler(), viz.ABS_GLOBAL)
		
vizact.ontimer(0, animate)

viz.MainView.setPosition([0, 2.5, 1.8])
viz.MainView.setEuler([180, 25, 0])


############### interactive activity ###############

viz.phys.enable()

#Set right hand interaction
rightHandSphere = vizshape.addSphere(radius = 0.08)
rightHandSphere.color( viz.BLUE )
rightHandSphere.alpha( 0.3 )
rightHandSphere.collideSphere(radius = 0.08)
rightHandSphere.enable( viz.COLLIDE_NOTIFY )
rightHandSphere.disable( viz.DYNAMICS )
rightHandLink = viz.link( avatar.getBone('Bip01 R Finger0') , rightHandSphere )
rightHandLink.preTrans([0,0,0])

#Set left hand interaction
leftHandSphere = vizshape.addSphere(radius = 0.08)
leftHandSphere.color( viz.BLUE )
leftHandSphere.alpha( 0.3 )
leftHandSphere.collideSphere(radius = 0.08)
leftHandSphere.enable( viz.COLLIDE_NOTIFY )
leftHandSphere.disable( viz.DYNAMICS )
leftHandLink = viz.link( avatar.getBone('Bip01 L Finger0') , leftHandSphere )
leftHandLink.preTrans([0,0,0])

#Declare boundary constants
MULTIPLE = 10.0
X_MIN = -0.8
X_MAX = 0.8
Y_MIN = 1
Y_MAX = 2
Z_MIN = -0.5
Z_MAX = -0.2

#Add a selection model
select = viz.addChild('fire.osg',cache=viz.CACHE_CLONE)
select.collideSphere(radius = 0.2)
select.disable( viz.DYNAMICS )
select.disable( viz.COLLIDE_NOTIFY )

#Set the position of the selection
def RandomSelection():
	x_factor = random.randint(1, MULTIPLE)
	y_factor = random.randint(1, MULTIPLE)
	z_factor = random.randint(1, MULTIPLE)
	X_DISP = (x_factor/MULTIPLE)*(X_MAX - X_MIN)
	Y_DISP = (y_factor/MULTIPLE)*(Y_MAX - Y_MIN)
	Z_DISP = (z_factor/MULTIPLE)*(Z_MAX - Z_MIN)
	select.setPosition(X_MIN + X_DISP, Y_MIN + Y_DISP, Z_MIN + Z_DISP)
	select.setEuler([0,0,0])

globalSelected = 0
viz.playSound('Full_Body_Bip001\water-splash-2.wav',viz.SOUND_PRELOAD)
#Called when two objects collide in the physics simulator
def onCollide(e):
	if e.obj1 is select:
		viz.playSound('Full_Body_Bip001\water-splash-2.wav')
		global globalSelected
		globalSelected += 1
		RandomSelection()
	
viz.callback( viz.COLLIDE_BEGIN_EVENT, onCollide )

#Set up activity sounds
viz.playSound('Full_Body_Bip001/fire3.wav',viz.SOUND_PRELOAD)
viz.playSound('Full_Body_Bip001/fire_siren_horn.wav',viz.SOUND_PRELOAD)

#Results after completion of activity
def ShowResults():
	select.disable( viz.RENDERING )
	select.disable( viz.COLLIDE_NOTIFY )
	viz.playSound('Full_Body_Bip001/fire3.wav',viz.STOP)
	global globalSelected
	viz.message( 'Great Job!\nYou put out {0:d} fires in 30 seconds!'.format(globalSelected) )

##Set up activity framework	
#game_timer = vizact.ontimer2(30, 0, ShowResults)
#game_timer.setEnabled(0)

def newActivity():
	viz.playSound('Full_Body_Bip001/fire_siren_horn.wav')
	select.enable( viz.RENDERING )
	select.enable( viz.COLLIDE_NOTIFY )
	global globalSelected
	globalSelected = 0
	RandomSelection()
	viz.playSound('Full_Body_Bip001/fire3.wav',viz.LOOP)
	global game_timer
	game_timer = vizact.ontimer2(30, 0, ShowResults)
	
def killActivity():
	global game_timer
	game_timer.setEnabled(0)
	select.disable( viz.RENDERING )
	select.disable( viz.COLLIDE_NOTIFY )
	viz.playSound('Full_Body_Bip001/fire_siren_horn.wav',viz.STOP)
	viz.playSound('Full_Body_Bip001/fire3.wav',viz.STOP)
	global globalSelected
	globalSelected = 0
	
#Pressing SPACE starts activity
vizact.onkeydown( ' ', newActivity )
#Pressing s stops activity
vizact.onkeydown( 's', killActivity )
