"""@package data_structure

Package that contains the two files that coordinates the structure of data in BladePy.

\arg \c data_structure.case_node File that contains the class data_structure.case_node.CaseNode. Every data of each case
will be stored in a Node. When modifying any display characteristic, the data will be retrieved and saved from and to
this node.

\arg \c data_structure.case_model File that contains a customized class data_structure.case_model.CaseModel for
QtCore.QAbstractItemModel. It defines the standard interface that item models must use to be able to interoperate
with other components in the model/view architecture. The functioning principle of this class can be a bit
complex and further search on how this works is highly recommended

"""