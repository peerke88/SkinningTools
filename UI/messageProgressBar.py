from SkinningTools.UI.qt_util import *

class MessageProgressBar(QProgressBar):
    """ the progressbar
    added functionality to the progressbar to make sure it also displays the correct message on what is currently been done

    :note: add warning messages or error messages in the progressbar? change color?
    :note: possibly make this smarter by having segmented blocks in which seperate functions can still access the progressbar but dont take up 100% just a smaller portion
    """
    def __init__(self, parent = None):
        """ the constructor
        
        :param parant: the parent of the current widget
        :type parent: QWidget
        """
        super(MessageProgressBar, self).__init__(parent = parent)
        self.setAlignment(Qt.AlignCenter)
        self.__currentMessage = ''

    def _setMessage(self, inMessage):
        """ override the text on the progress bar with a personal message

        :param inMessage: the message to add
        :type inMessage: string
        """
        if inMessage == '':
            self.__currentMessage = ''
            return
        if not inMessage.rstrip().endswith(":"):
            inMessage = "%s : " % inMessage
        self.__currentMessage = inMessage

    def _getMessage(self):
        """ return the current message of the progressbar
        :note: probably not really necessary, just added for the possibility, 
        could be usefull to expand with some string operations in multilayered tools
        
        :return: the message in the progressbar
        :rtype: string
        """
        return self.__currentMessage.rsplit(":")[0]

    message = property(_getMessage, _setMessage)

    def setValue(self, inValue):
        """ set the actual value of the progressbar, adds in the message as well

        :param inValue: the value to set the progressbar to
        :type inValue: float
        """
        if inValue > 100.0:
            inValue = 100
        super(MessageProgressBar, self).setValue(inValue)
        self.setFormat("%s%i%%" % (self.__currentMessage, inValue))
