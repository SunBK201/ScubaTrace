File
========

.. autoclass:: scubatrace.File

   Attributes
   ----------
   .. autoattribute:: name
   .. autoattribute:: signature
   .. autoattribute:: abspath
   .. autoattribute:: relpath
   .. autoattribute:: uri
   .. autoattribute:: text
   .. autoattribute:: lines
   .. autoattribute:: parser
   .. autoattribute:: node
   .. autoattribute:: imports
   .. autoattribute:: classes
   .. autoattribute:: functions
   .. autoattribute:: statements
   .. autoattribute:: identifiers
   .. autoattribute:: variables
   .. autoattribute:: is_external

   Methods
   -------

   .. automethod:: File
   .. automethod:: function_by_line
   .. automethod:: statements_by_line
   
   Special Methods
   ---------------

   .. automethod:: __str__
   .. automethod:: __hash__
   