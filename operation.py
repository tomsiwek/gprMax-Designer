class TOperation(object):
    """
    Class represents a single operation performed in program.

    :param o_type: operation type.
    :type o_type: string
    :param shape: shape on which the operation was performed.
    :type shape: TShape, TRect, TCylin, TCylinSector, TPolygon
    :param shape_num: shape list index.
    :type shape_num: integer
    """

    def __init__(self, o_type = None, **kwargs):
        """
        Initialise the object.
        """
        self.set_operation(o_type, **kwargs)
    
    def set_operation(self, o_type = None, **kwargs):
        """
        Set the parameters of an operation.

        :param o_type: operation type.
        :type o_type: string
        :param shape: shape on which the operation was performed.
        :type o_type: TShape, TRect, TCylin, TCylinSector, TPolygon
        :param shape_num: shape list index.
        :type shape_num: integer
        """
        self.o_type = o_type
        self.shape = kwargs.pop('shape', None)
        self.num = kwargs.pop('num', None)
