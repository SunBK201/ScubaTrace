Statement
=========

.. autoclass:: scubatrace.Statement

   Attributes
   ----------
   .. autoattribute:: is_jump_statement
   .. autoattribute:: identifiers
   .. autoattribute:: variables
   .. autoattribute:: right_values
   .. autoattribute:: left_values
   .. autoattribute:: signature
   .. autoattribute:: text
   .. autoattribute:: start_line
   .. autoattribute:: end_line
   .. autoattribute:: start_column
   .. autoattribute:: end_column
   .. autoattribute:: length
   .. autoattribute:: file
   .. autoattribute:: function
   .. autoattribute:: post_controls
   .. autoattribute:: pre_controls
   .. autoattribute:: post_control_dependents
   .. autoattribute:: pre_control_dependents
   .. autoattribute:: pre_data_dependents
   .. autoattribute:: post_data_dependents
   .. autoattribute:: references
   .. autoattribute:: definitions
   .. autoattribute:: is_taint_from_entry

   Methods
   -------
   .. automethod:: walk_backward
   .. automethod:: walk_forward
   
   Special Methods
   ---------------
   .. automethod:: __str__
   .. automethod:: __eq__
   .. automethod:: __hash__

.. autoclass:: scubatrace.SimpleStatement

.. autoclass:: scubatrace.BlockStatement

   Attributes
   ----------
   .. autoattribute:: statements
   .. autoattribute:: block_identifiers
   .. autoattribute:: block_variables

   Methods
   -------
   .. automethod:: statements_by_line
   .. automethod:: statements_by_type
   .. automethod:: statement_by_field_name
   
   Special Methods
   ---------------
   .. automethod:: __getitem__
