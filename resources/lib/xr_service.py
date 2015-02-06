##### Kodi Resume by Matt Huisman #####

import sys

import xbmc

import xr_settings
import xr_state
import xr_timer
import xr_util
        
__addonname__ = sys.modules[ "__main__" ].__addonname__
__language__  = sys.modules[ "__main__" ].__language__
        
class Service:              
    def start(self, resume=None, monitor=None, firstRun=False):
        self._initVariables()
        
        # Resume state if system argument provided or if resume setting enabled and not running for the first time
        if ( (resume == True) or ( resume == None and self._setts.getBool("resume_state") and not firstRun ) ):
            self._state.beginResume()
        else:
            # Show service started notification
            xr_util.notification(__addonname__, __language__(30104), 3000)
        
        # If monitoring hasn't been disabled
        if ( monitor != False ):            
            # Implement settings
            self._implementSettings()
            
            # Start main checking loop
            self._mainLoop()

            # Script finishing
            self._stop()
        
    def _initVariables(self):
        # Create settings and state objects
        self._setts = xr_settings.Settings()
        self._state = xr_state.State(self._setts)

        # Set inital variable values
        self._settingsMonitor = None
        self._stateMonitor = None
        self._exit = False
        self._doSettingsCallback = False
        self._doStateCallback = False
        
    def _mainLoop(self):
        # Loop until self._exit varaible set or kodi aborting
        while ( (not self._exit and not xbmc.abortRequested) ):
            # check to see if any timer callback flags have been set
            self._checkCallbacks()
            if ( not self._exit and not xbmc.abortRequested ):
                # Sleep for 250ms between checks
                xbmc.sleep(250)
                
    def _checkCallbacks(self):
        # Check if either timer callback flags have been set
        
        if ( self._doStateCallback ):
            # stateMonitor flag has been set, reset the flag and grab the current state
            self._doStateCallback = False
            self._state.grab()
            
            if ( self._state.hasChanged() ):
                # If state has changed, reset hasChanged flag and then do stuff (nothing required yet)
                self._state.resetChanged()
        
        if ( self._doSettingsCallback ):
            # settingMonitor flag has been set, reset the flag and check for settings changed
            self._doSettingsCallback = False
            self._setts.check()

            if ( self._setts.haveChanged() ):
                # If settings have changed, reset hasChanged flag and then implment changed settings
                self._setts.resetChanged()
                self._implementSettings()
                # Show Settings Updated notification
                xr_util.notification(__addonname__, __language__(30103), 3000)
        
    def _implementSettings(self):
        # Start/stop stateMonitor if monitorState setting has changed
        if ( self._setts.changed("monitor_state") ):
            if ( self._setts.getBool("monitor_state") ):
                self._startStateMonitor()
            else: self._stopStateMonitor()
            
        # If state interval setting changed & stateMonitor is running - then set stateMonitor to new interval
        if ( self._stateMonitor != None and self._setts.changed("state_interval") ):
            self._stateMonitor.setInterval(self._setts.getEnum('state_interval'))
        
        # Start/stop settingsMonitor if monitorSettings setting has changed
        if ( self._setts.changed("monitor_settings") ):
            if ( self._setts.getBool("monitor_settings") ):
                self._startSettingsMonitor()
            else: self._stopSettingsMonitor()
            
        # If settsInterval setting changed & settingsMonitor is running - then set settingsMonitor to new interval
        if ( self._settingsMonitor != None and self._setts.changed("setts_interval") ):
            self._settingsMonitor.setInterval(self._setts.getEnum('setts_interval'))
            
        if ( self._setts.changed("custom_db_path") or self._setts.changed('database_dir') or self._setts.changed('database_file') ):
            self._state.setDatabase()
        
        # If both stateMonitor and settingsMonitor not running - then set exit flag.
        if ( (not self._stateMonitor) and (not self._settingsMonitor) ):
            self._exit = True
                   
    def _startSettingsMonitor(self):
        # Start settingsMonitor if not already started
        if ( (self._settingsMonitor == None) or (not self._settingsMonitor.isAlive()) ):
            self._settingsMonitor = xr_timer.Timer(self._setts.getEnum('setts_interval'), self._settingsCallback, continuous=True)
            self._settingsMonitor.start()
            
    def _startStateMonitor(self):        
        # Start stateMonitor if not already started
        if ( (self._stateMonitor == None) or (not self._stateMonitor.isAlive()) ):
            self._stateMonitor = xr_timer.Timer(self._setts.getEnum('state_interval'), self._stateCallback, continuous=True)
            self._stateMonitor.start()
            
    def _stopSettingsMonitor(self):
        # Stop & wait for settings monitor to finish if running
        if ( (self._settingsMonitor != None) and (self._settingsMonitor.isAlive()) ):
            self._settingsMonitor.stop()
            self._settingsMonitor.join()
        self._settingsMonitor = None
        
    def _stopStateMonitor(self):
        # Stop & wait for state monitor to finish if running
        if ( (self._stateMonitor != None) and (self._stateMonitor.isAlive()) ):
            self._stateMonitor.stop()
            self._stateMonitor.join()
        self._stateMonitor = None
        
    def _settingsCallback(self):
        # Settings timer thread has just ticked. Set settings flag for main thread to detect.
        self._doSettingsCallback = True
        
    def _stateCallback(self):
        # State timer thread has just ticked. Set state flag for main thread to detect.
        self._doStateCallback = True

    def _stop(self):
        # Stop and wait for both timer threads to finish
        self._stopSettingsMonitor()
        self._stopStateMonitor()
        # Show Service Stopped notification
        xr_util.notification(__addonname__, __language__(30105), 3000)
