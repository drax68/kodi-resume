##### XBMC Resume by Matt Huisman #####

import os

import xbmc
import xbmcgui
import xbmcaddon

__addonid__ =  'script.service.xbmcresume'
__addon__   =  xbmcaddon.Addon(__addonid__)

if ( __name__ == "__main__" ):
    # Check if service is running
    if(xbmcgui.Window(10000).getProperty(__addonid__ + '_running') != "True"):
        # Service not running
        cwd   = __addon__.getAddonInfo('path').decode('utf-8')
        path  = os.path.join(cwd, 'service.py')
        # Set the service to not-resume when we start it manually
        resume = 'false'
        monitor = 'true'
        xbmc.executebuiltin("XBMC.RunScript(%s, %s, %s)" % (path, resume, monitor))
 
    # Open addon settings dialog
    __addon__.openSettings()