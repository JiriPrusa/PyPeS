from configparser import SafeConfigParser

global _WorkHeight
global _StartxPosition

global _ShakeHeight
global _ShakeXDist
global _ShakeStepDelay
global _ShakeStepAngleRange

global _servoFillAngle

global _Zfeedrate
global _Xfeedrate

global _HWservoDelay    # Delay after servo move (MUST BE SAME IN FIRMWARE (for MARLIN in config.h)!!!)
global _ActualSyringeStatus

global _SyringeHomeRest  # sec to wait before synthesis start

global _servosAttachPin
global _LoadStepDelay
global _UnloadStepDelay
global _MaxLoadRange    # ml

global _DefaultLoadRange

_WorkHeight = 60
_StartxPosition = 100
_Zfeedrate = 666
_Xfeedrate = 1600
_MaxLoadRange = 8.0  # ml
_SyringeHomeRest = 20  # sec to wait before synthesis start

_ShakeHeight = 60
_ShakeXDist = 150
_ShakeStepDelay = 800
_ShakeStepAngleRange = [5, 160]

_servoFillAngle = 171
_HWservoDelay = 5  # Delay after servo move (MUST BE SAME IN FIRMWARE (for MARLIN in config.h)!!!)
_servosAttachPin = 57
_LoadStepDelay = 230
_UnloadStepDelay = 140
_DefaultLoadRange=8.0

configs = {'WorkHeight':60,
           'StartxPosition':100,
           'Zfeedrate':666,
           'Xfeedrate':1600,
           'MaxLoadRange':8.0,
           'SyringeHomeRest':20,
           'ShakeHeight':60,
           'ShakeXDist':150,
           'ShakeStepDelay':800,
           'ShakeTopAngle':5,
           'ShakeBottomAngle':160,
           'ServoFillAngle':171,
           'HWservoDelay':5,
           'ServosAttachPin':57,
           'LoadStepDelay':230,
           'UnloadStepDelay':140,
           'DefaultLoadRange':8.0
           }

def init():
    global _WorkHeight
    global _StartxPosition

    global _ShakeHeight
    global _ShakeXDist
    global _ShakeStepDelay
    global _ShakeStepAngleRange

    global _servoFillAngle

    global _Zfeedrate
    global _Xfeedrate

    global _HWservoDelay  # Delay after servo move (MUST BE SAME IN FIRMWARE (for MARLIN in config.h)!!!)
    global _ActualSyringeStatus

    global _SyringeHomeRest  # sec to wait before synthesis start

    global _servosAttachPin
    global _LoadStepDelay
    global _UnloadStepDelay
    global _MaxLoadRange  # ml
    global _DefaultLoadRange

    config = SafeConfigParser()
    config.read('pypes.ini')

    #config.add_section('main')
    configs['WorkHeight'] = config.getint('main', 'workheight')
    configs['StartxPosition'] = config.getint('main', 'startxposition')
    configs['Zfeedrate'] = config.getint('main', 'zfeedrate')
    configs['Xfeedrate'] = config.getint('main', 'xfeedrate')
    configs['MaxLoadRange'] = config.getfloat('main', 'maxloadrange')
    configs['SyringeHomeRest'] = config.getint('main', 'syringehomerest')

    #config.add_section('shake')
    configs['ShakeHeight'] = config.getint('shake', 'shakeheight')
    configs['ShakeXDist'] = config.getint('shake', 'shakexdist')
    configs['ShakeStepDelay'] = config.getint('shake', 'shakestepdelay')
    configs['ShakeTopAngle'] = config.getint('shake', 'shaketopangle')
    configs['ShakeBottomAngle'] = config.getint('shake', 'shakebottomangle')

    #config.add_section('servo')
    configs['ServoFillAngle'] = config.getint('servo', 'servofillangle')
    configs['HWservoDelay'] = config.getint('servo', 'hwservodelay')
    configs['ServosAttachPin'] = config.getint('servo', 'servosattachpin')
    configs['LoadStepDelay'] = config.getint('servo', 'loadstepdelay')
    configs['UnloadStepDelay'] = config.getint('servo', 'unloadstepdelay')

    # config.add_section('gui')
    configs['DefaultLoadRange'] = config.getfloat('gui', 'defaultloadrange')

def saveConfig():
    config = SafeConfigParser()
    #config.read('pypes.ini')
    config.add_section('main')
    config.set('main', 'workheight', str(configs['WorkHeight']))
    config.set('main', 'startxposition', str(configs['StartxPosition']))
    config.set('main', 'zfeedrate', str(configs['Zfeedrate']))
    config.set('main', 'xfeedrate', str(configs['Xfeedrate']))
    config.set('main', 'maxloadrange', str(configs['MaxLoadRange']))
    config.set('main', 'syringehomerest', str(configs['SyringeHomeRest']))

    config.add_section('shake')
    config.set('shake', 'shakeheight', str(configs['ShakeHeight']))
    config.set('shake', 'shakexdist', str(configs['ShakeXDist']))
    config.set('shake', 'shakestepdelay', str(configs['ShakeStepDelay']))
    config.set('shake', 'shaketopangle' , str(configs['ShakeTopAngle']))
    config.set('shake', 'shakebottomangle', str(configs['ShakeBottomAngle']))

    config.add_section('servo')
    config.set('servo', 'servofillangle', str(configs['ServoFillAngle']))
    config.set('servo', 'hwservodelay', str(configs['HWservoDelay']))
    config.set('servo', 'servosattachpin', str(configs['ServosAttachPin']))
    config.set('servo', 'loadstepdelay', str(configs['LoadStepDelay']))
    config.set('servo', 'unloadstepdelay', str(configs['UnloadStepDelay']))

    config.add_section('gui')
    config.set('gui', 'defaultloadrange', str(configs['DefaultLoadRange']))


    with open('pypes.ini', 'w') as f:
        config.write(f)