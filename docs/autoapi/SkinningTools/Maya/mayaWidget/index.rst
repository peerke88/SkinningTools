:mod:`SkinningTools.Maya.mayaWidget`
====================================

.. py:module:: SkinningTools.Maya.mayaWidget


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   SkinningTools.Maya.mayaWidget.DockWidget



.. py:class:: DockWidget(parent=None)



   convenience class to wrap the mixin of maya witha  QDialog
   fixes the closeevent and cleans up ui-scene on close and open

   .. attribute:: toolName
      :annotation: = mayaDockWidgetTool

      

   .. method:: closeEvent(self, event)

      override for the closeEvent, we add one here as the Mixin in maya does not call the closeEvent
      currently using NotImplementedError as the tool we are using needs a closeEvent


   .. method:: deleteInstances(self)

      remove any lingering instances of the current tool,
      make sure that the toolName used in the class is clear and unique
      then this wont break any existing tools of maya


   .. method:: dockCloseEventTriggered(self)

      this is the function that is called when you close the widget when its docked
              


   .. method:: run(self)

      show the current ui and attach to a dockwidget
              



