##### XBMC Resume by Matt Huisman #####

import json

import xbmc

class XBMC_JSON:
    # Builds JSON request with provided json data
    def _buildRequest(self, method, params={}, jsonrpc='2.0', rid='1'):
        request = {
                   'jsonrpc' : jsonrpc,
                   'method'  : method,
                   'params'  : params,
                   'id'      : rid,
                   }
        return request
    
    # Performs multiple JSON queries and returns result boolean, data array, and errors array
    def _multipleQuery(self, requests):
        data = []
        errors = []
        
        if ( requests ):
            responses = self._execute(requests)
            if ( responses ):
                for response in responses:
                    responseResult = self._checkReponse(response)
                    if ( responseResult ):
                        data.append(response['result'])
                    else: errors.append(response['error'])
        
        if ( errors or not data ):
            result = False
        else: result = True
        
        return (result, data, errors)
    
    # Performs single JSON query and returns result boolean, data dictionary and error string
    def _query(self, request):
        result = False
        data = {}
        error = ''
        
        if ( request ):
            response = self._execute(request)
            if ( response ):
                result = self._checkReponse(response)
                if ( result ):
                    data = response['result']
                else: error = response['error']
                
        return (result, data, error)
                    
    # Checks JSON response and returns boolean result
    def _checkReponse(self, response):
        result = False
        if ( ('result' in response) and ('error' not in response) ):
            result = True
        return result
    
    # Executes JSON request and returns the JSON response
    def _execute(self, request):
        request_string = json.dumps(request)
        response = xbmc.executeJSONRPC(request_string)  
        if ( response ):
            response = json.loads(response)
        return response
    
    # Using a provided playerid, retrieves the currently playing item. 
    # Returns playlist item or None if not playing.
    def getPlaying(self, playerid):
        playing = None
        request = self._buildRequest('Player.GetItem', {'playerid' : playerid, 'properties' : ['file']})
        result, data = self._query(request)[:2]
        if ( result and 'item' in data and data['item'] ):
            playing = {}
            item = data['item']
            # If the playing item has a type (library item) then store the type+id and the id
            if ( 'type' in item and item['type'] != 'unknown' and 'id' in item ):
                playing[item['type']+'id'] = item['id']
            else:
                # Not a library item, store the filepath
                playing['file'] = item['file']
        return playing
    
    # Using a provided playlistid, retrieves the current playlist. Returns array of playlist_items
    def getPlaylist(self, playlistid):
        playlist = []
        request = self._buildRequest('Playlist.GetItems', {'playlistid' : playlistid, 'properties' : ['file']})
        result, data = self._query(request)[:2]
        if ( result and 'items' in data and data['items'] ):
            for item in data['items']:
                playlist_item = {}
                # If the playing item has a type (library item) then store the type+id and the id
                if ( 'type' in item and item['type'] != 'unknown' and 'id' in item ):
                    playlist_item[item['type']+'id'] = item['id']
                else:
                    # Not a library item, store the filepath
                    playlist_item['file'] = item['file']
                # Add playlist_item to playlist array
                playlist.append(playlist_item)
        return playlist
    
    # Using a provided playlistid and playlist - adds the playlist items to the current XBMC playlist
    def loadPlaylist(self, playlistid, playlist):
        requests = []
        for item in playlist:
            request = self._buildRequest('Playlist.Add', {'playlistid' : playlistid, 'item' : item})
            requests.append(request)
        result = self._multipleQuery(requests)[:1]
        return result
    
    # Starts playing the provided item
    def playItem(self, item):
        request = self._buildRequest('Player.Open', {'item' : item})
        result = self._query(request)[:1]
        return result
    
    # Seeks to a provided position
    def playerSeek(self, playerid, position):
        request = self._buildRequest('Player.Seek', {'playerid' : playerid, 'value' : position})
        result = self._query(request)[:1]
        return result
    
    # Returns a single XBMC info label as a string - default value can also be provided.
    def getInfoLabel(self, label, default='', allowEmpty=True):
        infoLabel = default
        request = self._buildRequest('XBMC.GetInfoLabels', {'labels' : [label]})
        result, data = self._query(request)[:2]
        if ( result and ( allowEmpty or data[label] ) ):
            infoLabel = data[label]
        return infoLabel
    
    # Returns multiple XBMC info labels in a dictionary - default values in a dictionary can be provided.
    def getInfoLabels(self, labels, defaults={}, allowEmpty=True):
        infoLabels = {}
        for label in labels:
            if ( label in defaults ):
                infoLabels[label] = defaults[label]
            else: infoLabels[label] = None

        request = self._buildRequest('XBMC.GetInfoLabels', {'labels' : labels})
        result, data = self._query(request)[:2]
        if ( result ):
            for label in labels:
                if ( allowEmpty or data[label] ):
                    infoLabels[label] = data[label]

        return infoLabels
    
    # Execute a query without and simply returns boolean of success/failure.
    def executeNonQuery(self, method, params={}):
        request = self._buildRequest(method, params)
        result = self._query(request)[:1]
        return result
    
    # Executes a query and returns a single value. Default value can be returned if query fails.
    def executeScalar(self, method, params={}, default='', allowEmpty=True):
        value = default
        request = self._buildRequest(method, params)
        result, data = self._query(request)[:2]
        if ( result and data ):
            if isinstance(data, dict):
                data = data[data.keys()[0]]
            if ( allowEmpty or data ):
                value = data
        return value