
"""
the translator class is there to provide ease of acces on changing ui language
(looking into qtranslator, but that has a lot of difficult extra mess to it so lets write our own)

the class will hold dictionary information of all possible languages the ui hass
the translator will load the information from seperate json files.
in these json files we will have keys that map the elements.
lets make sure that the returned value from the dictionary is decoded properly so it will always display the correct value

we can also let the translator call a qt widget that allows us to make a new language map
this for ease of access to create new languages if necessary, if these are saved in the same folder as the other languages, 
then this can be picked up automatically by te translator

we need to make sure that the keys for the dictionary are descriptive enough, preferably single word identifiers

so:
   - we need the current language identifier as a variable
   - we need to load different json modules to identify the amount of languages accessable
   - we only load the current json as a cached dictionary and return that, or we load in every language we want to switch between and cache that when requested
   - add a hook that we update the text of elements where possible, maybe make a mapping on qt on how to set text for specific elements

also check with the language of our current dcc tool to get that as a default

use google trans to get the first draft made? always have the original available when doing translations?
request possible languages from googletrans

- add a rightclick menu to the combobox that allows changing of the language to add a language (maybe use LANGUAGES to make sure there are no mistakes)

-------------------------------------------------
from SkinningTools.ThirdParty.googletrans import Translator , LANGUAGES

t = Translator()
txt = t.translate("to translate this piece of text", dest="ja")
print txt.text

print LANGUAGES.values()

"""
import json
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *
from SkinningTools.ThirdParty.google_trans import Translator, LANGUAGES


class DictionaryCreator(QWidget):
	def __init__(self, inLanguage, inDict, parent = None):
		super(DictionaryCreator, self).__init__(parent)
		self.setLayout(nullVBoxLayout())
		self.currentLanguage =''
		
		_res = self.setCurrentLanguage(inLanguage)
		if not _res:
			return



	def setCurrentLanguage(inLanguage):
		#@Note this might not be necessary if we force the user to take the languages from google api
		if inLanguage in LANGUAGES.keys()
			self.currentLanguage = inLanguage
			return True
		if inLanguage in LANGUAGES.values():
			for key, value in LANGUAGES.iteritems():
				if inLanguage != value:
					continue
				self.currentLanguage = key
				return True
		if self.currentLanguage == '':
			return False




class Translator(object):
	def __init__(self):

		self.languageFiles = [] #glob the json files from somwhere, english should exist by default
		self.__defaultLanguage = "EN"
		self.__currentLanguage = ''


