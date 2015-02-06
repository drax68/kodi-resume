##### Kodi Resume by Matt Huisman #####
##### Modified by Ryan Davies     #####

import sys
import os

import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

# Remote debugging enabled
REMOTE_DEBUG = False

# Get all super-global script contents
__addonid__          =  'script.service.kodiresume'
__addon__            =  xbmcaddon.Addon(__addonid__)
__addonname__        =  __addon__.getAddonInfo('name')
__addonauthor__      =  __addon__.getAddonInfo('author')
__language__         =  __addon__.getLocalizedString

__cwd__              =  xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')
__profile_dir__      =  xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')

__resource__         =  os.path.join(__cwd__, 'resources', 'lib')
__settings_file__    =  os.path.join(__profile_dir__, 'settings.xml')
__notificationicon__ =  os.path.join(__cwd__, 'resources', 'media', 'notification-icon.png')

sys.path.append(__resource__)

import xr_service

def start():
    # Set a window property that let's other scripts know we are running (window properties are cleared on kodi start)
    xbmcgui.Window(10000).setProperty(__addonid__ + '_running', 'True')

    # Try to get any system arguments
    try:
        if ( sys.argv[1] == 'true' ):
            resume = True
        else: resume = False
    except: resume = None
    try:
        if ( sys.argv[2] == 'true' ):
            monitor = True
        else: monitor = False
    except: monitor = None
    
    
    # If resume argument not supplied and we are not on home window 
    #     - assume we are enabling the addon and therefore don't want it to resume
    if ( resume == None and xbmcgui.getCurrentWindowId() != 10000 ):
        resume = False
            
    # If script data directory doesn't exist - create it and assume the script is starting for the first time
    if ( not xbmcvfs.exists(__profile_dir__) ):
        xbmcvfs.mkdir(__profile_dir__)
        firstRun = True
    else: firstRun = False

    # Create and start the main service - passing it any system arguments and first run status
    m = xr_service.Service()
    m.start(resume, monitor, firstRun)
    del m
    
    # Script finishing so clear the window running property
    xbmcgui.Window(10000).clearProperty(__addonid__ + '_running')

if ( __name__ == "__main__" ):
    # IF we are in remote debug mode - start trace
    if ( REMOTE_DEBUG ):
        import time
        try:
            import pydevd
            pydevd.settrace(stdoutToServer=True, stderrToServer=True)
            # Delay to let remote debugger become ready
            time.sleep(2)
        except: pass
        
    start()
    
    if ( REMOTE_DEBUG ):
        time.sleep(5)
    
    sys.modules.clear()
