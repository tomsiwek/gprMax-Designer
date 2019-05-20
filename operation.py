class TOperation(object):
    """
    Class represents single operation performed in program.
    """

    def __init__(self, o_type = None, **kwargs):
        self.set_operation(o_type, **kwargs)
    
    def set_operation(self, o_type = None, **kwargs):
        self.o_type = o_type
        self.shape = kwargs.pop('shape', None)
        self.num = kwargs.pop('num', None)
