#
# The implementation of the annotation parser
#

import re, sys

#----------------------------------------------------------------

class AnnParser:
    '''The class definition for the annotation parser'''

    def __init__(self, perf_params):
        '''To instantiate the annotation parser'''

        self.perf_params = perf_params
    
    #------------------------------------------------------------

    def __getTilingParams(self, assigns):
        '''To infer the tiling parameters from the given assignment list'''
        
        # initialize the default values of the tiling parameters
        num_tiling_levels = 1            # the number of tiling levels
        first_depth = 1                  # the first loop depth to be tiled
        last_depth = -1                  # the last loop depth to be tiled
        max_boundary_tiling_level = -1   # the maximum tiling level used to tile boundary tiles
        
        # iterate over all assignments
        for var, val in assigns:

            if var == 'num_tiling_levels':
                if not isinstance(val, int) or val <= -1:
                    print 'error:Tilic: the number of tiling levels must be a positive integer or zero: "%s"' % val
                    sys.exit(1)
                num_tiling_levels = val

            elif var == 'first_depth':
                if not isinstance(val, int) or val <= 0:
                    print 'error:Tilic: the first loop depth to be tiled must be a positive integer: "%s"' % val
                    sys.exit(1)
                first_depth = val

            elif var == 'last_depth':
                if not isinstance(val, int):
                    print 'error:Tilic: the last loop depth to be tiled must be an integer: "%s"' % val
                    sys.exit(1)
                last_depth = val
                
            elif var == 'max_boundary_tiling_level':
                if not isinstance(val, int):
                    print 'error:Tilic: the maximum tiling level used to tile boundary tiles must be an integer: "%s"' % val
                    sys.exit(1)
                max_boundary_tiling_level = val

            else:
                print 'error:Tilic: unknown tiling parameter: "%s"' % var
                sys.exit(1)

        # return the tiling parameters
        return (num_tiling_levels, first_depth, last_depth, max_boundary_tiling_level)

    #------------------------------------------------------------

    def __evalExp(self, text):
        '''To evaluate the given expression text'''

        try:
            val = eval(text, self.perf_params)
        except Exception, e:
            print ('error:Tilic: failed to evaluate expression: "%s"' % text)
            print ' --> %s: %s' % (e.__class__.__name__, e)
            sys.exit(1)
        return val

    #------------------------------------------------------------

    def parse(self, ann):
        '''
        Parse the given annotation text to extract the tiling parameters.
        The syntax must follow the following grammar:
          <assignments> ::= <assignment>*
          <assignment>  ::= <var> "=" <exp> ";"
        '''

        # remember the original annotation text
        orig_ann = ann

        # regular expression
        __assignment_re = r'\s*([A-Za-z_]\w*)\s*=\s*((.|\n)*?)\s*;'

        # parse the annotation text
        assigns = []
        while True:
            m = re.match(__assignment_re, ann)
            if not m:
                if ann and (not ann.isspace()):
                    print 'error:Tilic: annotation syntax error: "%s"' % orig_ann
                    sys.exit(1)
                break
            var = m.group(1)
            val = m.group(2)
            val = self.__evalExp(val)
            assigns.append((var, val))
            ann = ann[m.end():]

        # infer the tiling parameters from the parsed assignment list
        tiling_params = self.__getTilingParams(assigns)

        # return the tiling parameters
        return tiling_params

