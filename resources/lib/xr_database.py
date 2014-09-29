##### XBMC Resume by Matt Huisman #####

import json
import xbmc
from sqlite3 import dbapi2 as sqlite

class Database:
    def __init__(self, db_file):
        self._db_file = db_file
        self._createTable()
        
    # Returns the path to the current database file
    def getDBPath(self):
        return self._db_file
    
    # Creates the main data table if not exists
    def _createTable(self):
        if ( self._connect() ):
            try:
                self._cursor.execute("CREATE TABLE IF NOT EXISTS xbmc_resume (name TEXT, data BLOB, PRIMARY KEY (name));")
                self._conn.commit()
            except: pass
            self._disconnect()   

    # Connect to database and return connection result
    def _connect(self):
        try:
            self._conn = sqlite.connect(self._db_file)
            self._cursor = self._conn.cursor()
            connected = True
        except:
            self._disconnect()
            connected = False
        return connected
        
    # Closes the database
    def _disconnect(self):
        try: self._cursor.close()
        except: pass
        try: self._conn.close()
        except: pass
        
    # Loads the state data from the database
    def getStateData(self, default_data):
        data = default_data.copy()
        
        # Build query using default data keys so we only get the states we require
        query = "SELECT name, data FROM xbmc_resume WHERE name IN (%s)" % ", ".join('"%s"' % i for i in data.keys())
        if ( self._connect() ):
            try:
                self._cursor.execute(query)
                results = self._cursor.fetchall()
                if ( results ):
                    for result in results:
                        # Override default data values (fullback if data not in database)
                        data[result[0]] = json.loads(str(result[1]))
            except: pass
            self._disconnect()
        return data
        
    # Saves any changed state data to database
    def saveStateData(self, new_data, old_data):
        # Delay the actual save, as sometimes the state can be save while xbmc is aborting
        # and no song data is saved
        xbmc.sleep(1000)
        if (not xbmc.abortRequested):
            # Abort isnt being requested, do the actual save
            result = False
            
            data = []
            query = "REPLACE INTO xbmc_resume (name, data) VALUES"
            for name in new_data:
                if ( (name not in old_data) or (new_data[name] != old_data[name]) ):
                    query = "%s ('%s', ?)," % (query, name)
                    data.append(json.dumps(new_data[name]))
            query = query.rstrip(',')
    
            if ( self._connect() ):
                try:
                    self._cursor.execute(query, data)
                    self._conn.commit()
                    result = True
                except: pass
                self._disconnect()
            return result
        return False