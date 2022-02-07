.. SkinningTools documentation master file, created by
   sphinx-quickstart on Sat Aug 22 08:58:42 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SkinningTools's documentation!
=========================================

Contents:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
   autoapi/index
   autoapi/SkinningTools/Maya/index
   autoapi/SkinningTools/UI/index

Install
==================

use the package creator to create a package and install through the mel file 
or place the skinningtools folder in a location maya can find (mydocuments/maya/scripts for example on windows)
after that use the following python commands:

* for release / use

.. code-block:: python
  
  import SkinningTools
  myWindow = SkinningTools.tool()

* for development

.. code-block:: python
  
  from SkinningTools import reloader
  reload(reloader)
  reloader.unload(newScene=False)

  from SkinningTools.UI import SkinningToolsUI
  reload(SkinningToolsUI)
  myWindow = SkinningToolsUI.showUI()

Notes
==================

refactor of the original skinning tools
https://gumroad.com/l/skinningTools_PL

main goal of the tools is to make clean code that is ready for Python 3
maya code should be seperated in the Maya folder hopefully we can make some parts DCC agnostic to get the same or similar functionality in other dcc tools

Authors
==================

* `Robert Joosten`_

* `Mio Zwickl`_

* `Rodolphe Vaillant`_

* `Trevor van Hoof`_

* `Jan Pijpers`_

* `Perry Leijten`_

.. _Robert Joosten: http://technicaldirector.nl/
.. _Mio Zwickl: https://www.artstation.com/ikitamonday
.. _Rodolphe Vaillant: http://rodolphe-vaillant.fr/
.. _Trevor van Hoof: http://trevorius.com/scrapbook/
.. _Jan Pijpers: https://www.janpijpers.com/
.. _Perry Leijten: https://www.perryleijten.com/


Prerequisites
==================


 - Maya 2017+
 - Python 2.7 (3.7)
 - sphinx (extensions: sphinx-autoapi,  groundwork-sphinx-theme)


Acknowledgments
==================

``kdTree``
  * Author: Matej Drame
  * License: MIT license


``Controls sliders``
  * Author: `Daniele Niero`_
  * License: GNU license


``paint skin weight pickwalking``
  * Author: `Ryan Porter`_

``pyprof2calltree``
  * Author: `David Allouche`_
  * License: MIT license

``qcahcegrind``
  * Author: `Josef Weidendorfer`_
  * Licences:
    - kcachegrind: GPLv2 
    - Qt: LGPL 2.1 
    - dot: EPL

``google_trans_new``
  * Author: `LuShan`_
  * License: Freeware(MIT)

``requests``
  * Author: `Kenneth Reitz`_
  * License: Apache 2.0

.. _Daniele Niero: https://github.com/daniele-niero
.. _Ryan Porter: https://yantor3d.wordpress.com/
.. _David Allouche: https://github.com/pwaller/pyprof2calltree/blob/master/LICENSE
.. _Josef Weidendorfer: http://kcachegrind.sourceforge.net/html/Home.html
.. _LuShan: https://github.com/lushan88a/google_trans_new
.. _Kenneth Reitz: http://python-requests.org