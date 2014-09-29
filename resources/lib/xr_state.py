##### XBMC Resume by Matt Huisman #####

import sys
import time

import xbmcgui
import xbmc

import xr_database
import xr_json
import xr_util

__language__     = sys.modules[ "__main__" ].__language__
__addonname__    = sys.modules[ "__main__" ].__addonname__
__addonauthor__  = sys.modules[ "__main__" ].__addonauthor__

class State:
    # XBMC Window ID Constants
    WINDOW_HOME      = 10000 
    WINDOW_VIDEO     = 12005
    WINDOW_AUDIO     = 12006
    WINDOW_SLIDESHOW = 12007
    
    def __init__(self, settings):
        self._setts = settings

        self._initVariables()
        self.setDatabase()
        self._setDefaults()
        self._load()

    def _initVariables(self):
        # Define order of grab methods
        self._grab_methods = (
                                '_grab_video',
                                '_grab_audio',
                                '_grab_window',
                                '_grab_volume_muted',
                                '_validate_data',
                                )
  
        # Define order of resume methods
        self._resume_methods = (
                                  '_resume_video',
                                  '_resume_audio',
                                  '_resume_window',
                                  '_resume_volume',
                                  ) 

        # Define default state values
        self._defaults = {
                      'volume'         : 100,
                      'muted'          : False,
                      'video'          : None,
                      'video_time'     : None,
                      'video_playlist' : [],
                      'audio'          : None,
                      'audio_time'     : None,
                      'audio_playlist' : [],
                      'window_id'      : self.WINDOW_HOME,
                      'window_path'    : '',
                      }

        self._data = {}
        self._db_data = {}
        self._db = None
        self._hasChanged = False
        self._validData  = False
        self._seekMinimum = 5
        self._muteFor     = 0
        self._json = xr_json.XBMC_JSON()

    # Change the state database if different path been set
    def setDatabase(self):
        if (self._db):
            current_path = self._db.getDBPath()
        else: current_path = ''
        new_path = self._setts.getDBPath()

        if ( new_path != current_path ):
            self._db = xr_database.Database(new_path)
            self._db_data = {}

    # Load the state data from the database
    def _load(self):
        self._db_data = self._db.getStateData(self._defaults)
        self._data = self._db_data.copy()

    # Save the state data to the database
    def _save(self):  
        if (not xbmc.abortRequested):
            if ( self._db.saveStateData(self._data, self._db_data) ):
                self._db_data = self._data.copy()

    # If data is validated and different to last saved data then save
    def _check(self):
        if ( self._validData and self._data != self._db_data ):
            self._validData = False
            self._hasChanged = True
            self._save()

    # Reset data has changed flag
    def resetChanged(self):
        self._hasChanged = False

    # Returns true if data has changed
    def hasChanged(self):
        return self._hasChanged

    # Loop through and call all grab methods   
    def grab(self):
        self._setDefaults() #reset all data back to original so is overwritten by grab states (or will remain default if grab state disabled)
        for name in self._grab_methods:
            if ( self._abort() ):
                break

            try: 
                method = getattr(self, name)
                method()
            except: pass

        if ( not self._abort() ):
            self._check()

    # Shortcut method to xbmc abortRequested flag
    def _abort(self):
        return xbmc.abortRequested

    # Set's current data to default data
    def _setDefaults(self):
        self._data = self._defaults.copy()

    # Public method 
    def beginResume(self):
        finish = time.time() + self._setts.getEnum('resume_delay')
        while not self._abort() and time.time() < finish:
            self._sleep(500)
        if ( not self._abort() ):
            self._resume()
        
    # Loop through and call all resume methods
    def _resume(self):
        xr_util.notification(__addonname__, __language__(30101), 3000)
        for name in self._resume_methods:
            try: 
                method = getattr(self, name)
                method()
            except: pass
        
    # Shortcut method to get settings boolean value
    def _enabled(self, setting):
        return self._setts.getBool(setting)

    # Shortcut method to get XBMC's current window id as int
    def _getWindowID(self):
        return xbmcgui.getCurrentWindowId()
    
    # Returns current XBMC window/folder path as string
    def _getWindowPath(self):
        return self._json.getInfoLabel('Container.FolderPath', self._defaults['window_path'])
    
    # Returns current XBMC volume level as integer (0-100)
    def _getVolume(self):
        return int(self._json.executeScalar('Application.GetProperties', {'properties' : ['volume']}, self._defaults['volume']))
    
    # Returns True if XBMC muted
    def _getMuted(self):
        return bool(self._json.executeScalar('Application.GetProperties', {'properties' : ['muted']}, self._defaults['muted']))
    
    # Set XBMC to muted (value=True) or not-muted (value=False)
    def _setMuted(self, value):
        self._json.executeNonQuery('Application.SetMute', {'mute' : value})
            
    # Returns XBMC playing time or none if nothing playing
    def _getPlayingTime(self):
        try: time = int(xbmc.Player().getTime())
        except: time = None
        return time
            
    # Grabs media states (current playing, position, playlist) using provided playlistid and state name
    def _grab_media(self, playlistid, name):
        resumePlaying = self._enabled('resume_' + name)
        resumePlayingTime = self._enabled('resume_' + name + '_time')
        resumePlaylist = self._enabled('resume_' + name + '_playlist')
        
        # If resumePlaying enabled
        if ( resumePlaying ):
            # Get playing item
            self._data[name] = self._json.getPlaying(playlistid)
            
        # If resumePlayingTime enabled and item playing
        if ( resumePlayingTime and self._data[name] ):
            # Get item time (position)
            self._data[name + '_time'] = self._getPlayingTime()

        # If resumePlaylist enabled
        if ( resumePlaylist ):
            # Get playlist
            self._data[name + '_playlist'] = self._json.getPlaylist(playlistid)        
          
    # Resumes media states (current playing, position, playlist) using provided playlistid and state name
    def _resume_media(self, playlistid, name):
        resumePlaying = self._enabled('resume_' + name)
        resumePlayingTime = self._enabled('resume_' + name + '_time')
        resumePlaylist = self._enabled('resume_' + name + '_playlist')
        
        if ( resumePlaying or resumePlaylist ):
            playing = self._data[name]
            playingTime = self._data[name + '_time']
            playlist = self._data[name + '_playlist']
            playlist_pos = None

            # If resumePlaylist enabled and item playing and item in playlist
            if ( resumePlaylist and playing and (playing in playlist) ):
                # Get playlist position
                playlist_pos = playlist.index(playing)

            # If resumePlaying enabled and item playing and item not in playlist
            if ( resumePlaying and playing and playlist_pos == None ):
                # Start playing item
                self._play(playing, resumePlayingTime, playingTime)
                
            # If resumePlaylist enabled and playlist not empty
            if ( resumePlaylist and playlist ):
                # Load playlist into XBMC
                self._json.loadPlaylist(playlistid, playlist)
                # If resumePlaying enabled and item playing and item in playlist
                if ( resumePlaying and playing and playlist_pos != None ):
                    # Build new playlist item
                    item = {'playlistid' : playlistid, 'position' : playlist_pos}
                    # Start playing playlist item
                    self._play(item, resumePlayingTime, playingTime)

    # Shortcut method to xbmc sleep method
    def _sleep(self, ms):
        xbmc.sleep(ms)

    # Play and seek a media item
    def _play(self, item, resumePlayingTime, playingTime):    
        seek = False
        # If resumePlayingTime enabled and there is a playing time and playingtime is greater than seek minimum
        if ( resumePlayingTime and playingTime and playingTime > self._seekMinimum ):
            seek = True
            # Get current mute status - so can revert
            muteStatus = self._getMuted()
            # If not currently muted - mute so we don't start hearing item before seeking
            if ( muteStatus == False ):
                self._setMuted(True)

        # Start playing the item
        self._json.playItem(item)

        if ( seek ):
            self._sleep(200)
            # Seek to playtime minus 3 seconds
            xbmc.Player().seekTime(playingTime - 3)

            # If muteStatus was false or if resume_muted enabled and false - then un-mute
            if ( muteStatus == False or (self._enabled('resume_muted') and self._data['muted'] == False) ):
                self._sleep(1000)
                self._setMuted(False)

    # Last method call to make sure JSON is still returning valid data before we save
    def _validate_data(self):
        if ( not self._abort() ):
            json_test = self._json.executeScalar('Application.GetProperties', {'properties' : ['volume']}, None)
            if ( json_test != None ):
                self._validData = True


    # Grabs current volume level and mute status if states enabled
    def _grab_volume_muted(self):
        if ( self._enabled('resume_volume') ):
            self._data['volume'] = self._getVolume()

        if ( self._enabled('resume_muted') ):
            self._data['muted'] = self._getMuted()
                    
    # Resumes volume state (mute status is resumed in the _play method)
    def _resume_volume(self):
        if ( self._enabled('resume_volume') and self._data['volume'] != self._getVolume() ):
            self._json.executeNonQuery('Application.SetVolume', {'volume' : self._data['volume']})



    # Grab the current video states (playing, position, playlist) if states enabled
    def _grab_video(self):
        self._grab_media(1, 'video')
     
    # Resumes video states if states enabled
    def _resume_video(self):
        self._resume_media(1, 'video')         



    # Grab the current audio states (playing, position, playlist) if states enabled
    def _grab_audio(self):        
        self._grab_media(0, 'audio')

    # Resumes audio states if states enabled
    def _resume_audio(self):
        self._resume_media(0, 'audio')

    # Grabs the current window and path if state enabled
    def _grab_window(self):
        if ( self._enabled('resume_window') ):
            self._data['window_id']   = self._getWindowID()
            self._data['window_path'] = self._getWindowPath()
                
    # Resume the window/path state if state enabled and window is valid
    def _resume_window(self):
        if ( self._enabled('resume_window') ):
            self._sleep(1000)
            
            window_id   =  self._getWindowID()
            window_path = self._getWindowPath()
            player = xbmc.Player()
            if not ( ( self._data['window_id'] == window_id and self._data['window_path'] == window_path ) or 
                     ( self._data['window_id'] == self.WINDOW_AUDIO and not player.isPlayingAudio() ) or
                     ( self._data['window_id'] == self.WINDOW_VIDEO ) or
                     ( self._data['window_id'] == self.WINDOW_SLIDESHOW ) ):
                xbmc.executebuiltin('ActivateWindow(%s, %s)' % (self._data['window_id'], self._data['window_path']))