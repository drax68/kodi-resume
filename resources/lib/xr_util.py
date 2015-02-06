##### Kodi Resume by Matt Huisman #####

import xbmc
import sys

__addonid__          =  sys.modules[ "__main__" ].__addonid__
__notificationicon__ = sys.modules[ "__main__" ].__notificationicon__

# Unicode function
def smart_unicode(s):
    """credit : sfaxman"""
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def smart_utf8(s):
    return smart_unicode(s).encode('utf-8')

def notification(title, message, timeout=2000, image=__notificationicon__):
    command = 'Notification(%s,%s,%s,%s)' % (smart_utf8(title), smart_utf8(message), timeout, smart_utf8(image))
    xbmc.executebuiltin(command)
    
def log(msg, level=xbmc.LOGDEBUG):
    if type(msg).__name__=='unicode':
        msg = msg.encode('utf-8')

    xbmc.log("[%s] %s"%(__addonid__, msg.__str__()), level)
