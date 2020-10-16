from SkinningTools.UI.qt_util import *


# @note: add warning messages or error messages in the progressbar? change color?
# @note: possibly make this smarter by having segmented blocks in which seperate functions can still access the progressbar
# but dont take up 100% just a smaller portion
class MessageProgressBar(QProgressBar):
    def __init__(self, parent = None):
        super(MessageProgressBar, self).__init__(parent = parent)
        self.setAlignment(Qt.AlignCenter)
        self.__currentMessage = ''

    def _setMessage(self, inMessage):
        if inMessage == '':
            self.__currentMessage = ''
            return
        if not inMessage.rstrip().endswith(":"):
            inMessage = "%s : " % inMessage
        self.__currentMessage = inMessage

    def _getMessage(self):
        return self.__currentMessage.rsplit(":")[0]

    message = property(_getMessage, _setMessage)

    def setValue(self, inValue):
        if inValue > 100.0:
            inValue = 100
        super(MessageProgressBar, self).setValue(inValue)
        self.setFormat("%s%i%%" % (self.__currentMessage, inValue))
