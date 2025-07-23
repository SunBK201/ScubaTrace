Function
========

.. autoclass:: scubatrace.Function

   Attributes
   ----------
   .. autoattribute:: name
   .. autoattribute:: signature
   .. autoattribute:: lines
   .. autoattribute:: name_node
   .. autoattribute:: body_node
   .. autoattribute:: body_start_line
   .. autoattribute:: body_end_line
   .. autoattribute:: parameter_lines
   .. autoattribute:: callers
   .. autoattribute:: callees
   .. autoattribute:: calls
   .. autoattribute:: is_external
   .. autoattribute:: accessible_functions

   Methods
   -------

   .. automethod:: Function
   .. automethod:: statements_by_type
   .. automethod:: slice_by_statements
   .. automethod:: slice_by_lines
   .. automethod:: export_cfg_dot
