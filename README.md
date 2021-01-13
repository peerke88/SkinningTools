# SkinningTools

refactor of the original skinning tools
https://gumroad.com/l/skinningTools_PL

main goal of the tools is to make clean code that is ready for Python 3
maya code should be seperated in the Maya folder hopefully we can make some parts DCC agnostic to get the same or similar functionality in other dcc tools (future dev)

### todo:
 - add all functionality to menubar
 - add settings page (size of elements/icons, language, etc)
 - add translator class for automated language information, option to save and modify
 - create small videos/gifs to explain the tools as tooltips (use this for testing functionality)


## documentation

[API](https://www.perryleijten.com/skinningtool/html)

## Authors

* [Mio Zwickl](https://www.artstation.com/ikitamonday)
* [Rodolphe Vaillant](http://rodolphe-vaillant.fr/)
* [Trevor van Hoof](http://trevorius.com/scrapbook/)
* [Jan Pijpers](https://www.janpijpers.com/)
* [Perry Leijten](https://www.perryleijten.com/)


## Prerequisites

```
 - Maya 2017+
 - Python 2.7 (3.7)
 - sphinx (extensions: sphinx-autoapi,  groundwork-sphinx-theme)
```


## Acknowledgments

* kdTree
```
  Author: Matej Drame
  License: MIT license
```

* Controls sliders
```
  Author: [Daniele Niero](https://github.com/daniele-niero)
  License: GNU license
```

* paint skin weight pickwalking
``` 
  Author: [Ryan Porter](https://yantor3d.wordpress.com/)
```

* pyprof2calltree
```
  Author: David Allouche
  Licences: Freeware(MIT) https://github.com/pwaller/pyprof2calltree/blob/master/LICENSE
```

* qcahcegrind
```
  Author: Josef Weidendorfer
  Licences:
    - kcachegrind: GPLv2 (http://kcachegrind.sourceforge.net/html/License.html)
    - Qt: LGPL 2.1 (http://qt-project.org/doc/qt-5.0/qtdoc/lgpl.html)
    - dot: EPL (http://www.graphviz.org/License.php)
```
* google_trans_new
```
  Author: LuShan
  Licences: Freeware(MIT) https://github.com/lushan88a/google_trans_new
```
* requests
```
  Author: Kenneth Reitz
  Licences: Apache 2.0 http://python-requests.org
```