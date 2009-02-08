#
# The main file for the parametric multilevel tiling for imperfectly nested loops
#

import sys
import ann_parser, code_parser, module.module, pprinter, semant, transformator

#-----------------------------------------

class Tilic(module.module.Module):
    '''The class definition for Tilic module'''
    
    def __init__(self, perf_params, module_body_code, annot_body_code, cmd_line_opts,
                 line_no, indent_size, language='C'):
        '''To instantiate an Tilic tiling module'''
        
        module.module.Module.__init__(self, perf_params, module_body_code, annot_body_code,
                                      cmd_line_opts, line_no, indent_size, language)

    #---------------------------------------------------------------------
    
    def __generate(self, stmts, int_vars):
        '''To generate the tiled loop code'''

        # generate the declaration code for the new integer variables
        code = ''
        for i, iv in enumerate(int_vars):
            if i%10 == 0:
                code += '\n  int '
            code += str(iv)
            if i%10 == 9 or i == len(int_vars)-1:
                code += ';'
            else:
                code += ','
        if int_vars:
            code += '\n\n'

        # generate the tiled code
        p = pprinter.PrettyPrinter()
        for s in stmts:
            code += p.pprint(s)

        # append and prepend newlines (if necessary)
        if code[0] != '\n':
            code = '\n' + code
        if code[-1] != '\n':
            code = code + '\n'

        # return the generated code
        return code

    #---------------------------------------------------------------------
    
    def transform(self):
        '''To perform loop tiling'''

        # parse the text in the annotation module body to extract the tiling information
        tiling_params = ann_parser.AnnParser(self.perf_params).parse(self.module_body_code)

        # parse the code (in the annotation body) to extract the corresponding AST
        stmts = code_parser.getParser().parse(self.annot_body_code)

        # check and enforce the AST semantics
        stmts = semant.SemanticChecker().check(stmts)

        # perform loop-tiling transformation
        (stmts, int_vars) = transformator.Transformator(tiling_params).transform(stmts)

        # generate the tiled code
        code = self.__generate(stmts, int_vars)

        # return the tiled code
        return code
