##### XBMC Resume by Matt Huisman #####

import sys
import os

import xbmc
import xbmcvfs

__addon__          =  sys.modules[ "__main__" ].__addon__
__profile_dir__    =  sys.modules[ "__main__" ].__profile_dir__
__settings_file__  =  sys.modules[ "__main__" ].__settings_file__

class Settings:    
    def __init__(self):
        self._initVariables()
        self._load()
        
    def _initVariables(self):
        # Define default user settings
        self._defaults = {
                 # Default main settings
                 'resume_state'         :  'true',
                 'monitor_settings'     :  'true',
                 'setts_interval'       :  '0',
                 'monitor_state'        :  'false',
                 'state_interval'       :  '0',
                 'resume_delay'         :  '0',
                 'custom_db_path'       :  'false',
                 'database_dir'         :  __profile_dir__,
                 'database_file'        :  'xbmcresume.db',
                 
                 # Default states to resume settings                 
                 'resume_video'            :  'true',
                 'resume_video_time'       :  'true',
                 'resume_video_playlist'   :  'true',
                 
                 'resume_audio'            :  'true',
                 'resume_audio_time'       :  'true',
                 'resume_audio_playlist'   :  'true',
                
                 'resume_window'           :  'true',
                 'resume_volume'           :  'false',
                 'resume_muted'            :  'false',  
        }
        
        self._settings = {  # Holds current settings. Preload with non-user settings
                 'setts_interval_enum'  :  (5,10,30,60),
                 'state_interval_enum'  :  (5,10,30,60),
                 'resume_delay_enum'    :  (0,5,10,30,60),
        }

        self._previousSettings = {}  # Holds last saved settings
        self._lastModTime = 0
        self._haveChanged = False
        
    # Returns custom db path if set, or default path if not
    def getDBPath(self):
        if ( self.getBool('custom_db_path') and self._settings['database_dir'].strip() != '' and self._settings['database_file'].strip() != ''):
            db_dir = xbmc.translatePath(self._settings['database_dir'].strip()).decode('utf-8')
            db_file = self._settings['database_file'].strip().decode('utf-8')
            db_path = os.path.join(db_dir, db_file)
        else:
            db_dir = self._defaults['database_dir']
            db_file = self._defaults['database_file']
            db_path = os.path.join(db_dir, db_file)
        
        return db_path
  
    # Return the last modified time of the settings file if exists
    def _getModTime(self):
        if ( xbmcvfs.exists(__settings_file__) ):
            return os.path.getmtime(__settings_file__)
        else: return 0
    
    # Saves user settings to XBMC settings xml file
    def save(self):
        if ( not xbmc.abortRequested ):
            for name in self._defaults:
                if name in self._settings:
                    setting = self._settings[name]
                else: setting = self._defaults[name]

                try: __addon__.setSetting(name, setting)
                except: pass

            self._lastModTime  = self._getModTime()
  
    # Loads the user settings from XBMC settings xml file, fallback on default if setting not in xml file
    def _load(self):
        self._previousSettings = self._settings.copy()
        for name in self._defaults:
            try: setting = __addon__.getSetting(name)
            except: setting = None
            if (not setting):
                self._settings[name] = self._defaults[name]
            self._settings[name] = setting
        self._lastModTime  = self._getModTime()
         
    # Checks if settings xml file has been modified - if yes - then loades new settings
    def check(self):
        if ( self._getModTime() != self._lastModTime ):
            self._load()
            # After loading settings - see if any setting actually have changed
            if(self._settings != self._previousSettings):
                self._haveChanged = True

    # Returns boolean if a particular setting has changed
    def changed(self, name):
        changed = True
        if (name in self._settings and name in self._previousSettings and self._settings[name] == self._previousSettings[name]):
            changed = False
        return changed

    # Converts a xbmc setting string to a boolean
    def _stringToBool(self, string):
        boolean = False
        if (string == 'true'):
            boolean = True
        return boolean
            
    # Returns true if a setting exists and is set to true - optional default
    def getBool(self, setting, default=False):
        boolean = default
        if (setting in self._settings):
            boolean = self._stringToBool(self._settings[setting])
        return boolean
    
    # Returns the actual value for a enumeration setting
    def getEnum(self, setting, default=None):
        value = default
        if (setting in self._settings and setting + '_enum' in self._settings):
            try:
                index = int(self._settings[setting])
                value = self._settings[setting + '_enum'][index]
            except:pass
        return value

    # Resets the settings has changed flag to false
    def resetChanged(self):
        self._haveChanged = False
        
    # Returns true if any settings have changed
    def haveChanged(self):
        return self._haveChanged
    
