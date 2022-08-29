import os
import re
import sys
import ast


# [S001]
class LongStringException(Exception):
    def __init__(self, line):
        self.message = f'Line {line}: S001 Too long'
        super().__init__(self.message)


# [S002]
class IndentationException(Exception):
    def __init__(self, line):
        self.message = f'Line {line}: S002 Indentation is not a multiple of four'
        super().__init__(self.message)


# [S003]
class UnnecessarySemicolon(Exception):
    def __init__(self, line):
        self.message = f'Line {line}: S003 Unnecessary semicolon'
        super().__init__(self.message)


# [S004]
class InlineComments(Exception):
    def __init__(self, line):
        self.message = f'Line {line}: S004 At least two spaces required before inline comments'
        super().__init__(self.message)


# [S005]
class ToDo(Exception):
    def __init__(self, line):
        self.message = f'Line {line}: S005 TODO found'
        super().__init__(self.message)


# [S006]
class TwoBlankLines(Exception):
    def __init__(self, line):
        self.message = f'Line {line}: S006 More than two blank lines used before this line'
        super().__init__(self.message)


# [S007]
class ConstructionNameSpaceException(Exception):
    def __init__(self, line, string):
        self.construction_name = string.split()[0]
        self.message = f"Line {line}: S007 Too many spaces after '{self.construction_name}'"
        super().__init__(self.message)


# [S008]
class CamelCaseException(Exception):
    def __init__(self, line, string):
        self.class_name = string.split()[1].split('(')[0]
        self.message = f"Line {line}: S008 Class name '{self.class_name}' should be written in CamelCase"
        super().__init__(self.message)


# [S009]
class ShakeCaseException(Exception):
    def __init__(self, line, string):
        self.def_name = string.split()[1].split('(')[0]
        self.message = f"Line {line}: S009 Function name '{self.def_name}' should use snake_case"
        super().__init__(self.message)


# [S010]
class ArgumentCaseException(Exception):
    def __init__(self, line, arg):
        self.arg = arg
        self.message = f"Line {line}: S010 Argument name '{self.arg}' should use snake_case"
        super().__init__(self.message)


# [S011]
class VariableCaseException(Exception):
    def __init__(self, line, variable):
        self.variable = variable
        self.message = f"Line {line}: S011 Variable '{self.variable}' should be written in snake_case"
        super().__init__(self.message)


# [S012]
class MutableDefaultValueException(Exception):
    def __init__(self, line):
        self.message = f"Line {line}: S012 Default argument value is mutable"
        super().__init__(self.message)


# _____________________________
# class template for Exceptions
class ErrorCheck:
    def __init__(self, string, line):
        self.string = string
        self.line = line


# [S001]
class LengthCheck(ErrorCheck):
    def length_check(self):
        if len(self.string) > 79:
            raise LongStringException(self.line)


# [S002]
class IndentationCheck(ErrorCheck):
    def indentation_check(self):
        if self.string != '\n' and (len(self.string) - len(self.string.lstrip())) % 4:
            raise IndentationException(self.line)


# [S003]
class SemicolonCheck(ErrorCheck):
    def semicolon_check(self):
        if self.string.rstrip('\n') != '' and self.string[0] != '#':
            try:
                if ';' in self.string.rstrip('\n').split('#')[0].rstrip(' ')[-1]:
                    raise UnnecessarySemicolon(self.line)
            except IndexError:
                pass


# [S004]
class CommentSpaceCheck(ErrorCheck):
    def comment_space_check(self):
        if '#' in self.string:
            if len(self.string) > 1 and self.string.split('#')[0][-2:] != '  ' and self.string[0] != '#':
                raise InlineComments(self.line)


# [S005]
class ToDoCheck(ErrorCheck):
    def todo_check(self):
        if '#' in self.string:
            if 'TODO' in self.string.upper():
                raise ToDo(self.line)


# [S006]
class BlankSpace(ErrorCheck):
    counter = 0

    def __init__(self, string, line):
        # increment
        super().__init__(string, line)
        if self.string.rstrip('\n') == '':
            BlankSpace.counter += 1
        elif BlankSpace.counter > 2:
            BlankSpace.counter = 0
            raise TwoBlankLines(self.line)
        elif len(self.string.rstrip('\n')) > 1:
            BlankSpace.counter = 0


# [S007]
class TooManySpaces(ErrorCheck):
    def space_check(self):
        if re.match(r'\s*\bclass', self.string) or re.match(r'\s*\bdef', self.string) is not None:
            if re.match(r'\s*\b(?:def|class)\s[A-z].*_?[A-z].*', self.string) is None:
                raise ConstructionNameSpaceException(self.line, self.string)


# [S008]
class CamelCase(ErrorCheck):
    def camel_case(self):
        if re.match(r'\s*\bclass', self.string) is not None:
            if re.match(r'class *[A-Z]*[A-Z].*', self.string) is None:
                raise CamelCaseException(self.line, self.string)


# [S009]
class SnakeCase(ErrorCheck):
    def snake_case(self):

        if 'def' in self.string:
            if '_' in self.string:
                if re.match(r'(\s*def *[a-z\d]*_[a-z].*)|(\s*def *\b__[a-z\d]*__)', self.string.split('(')[0]) is None:
                    raise ShakeCaseException(self.line, self.string)
            else:
                if re.match(r'(\s*def *[a-z\d].*)', self.string.split('(')[0]) is None:
                    raise ShakeCaseException(self.line, self.string)


# [S010]
class ArgumentName:
    call = 0
    dict_ = {}

    def __init__(self, tree, string, line):
        self.tree = tree
        self.string = string
        self.line = line

    def snake_case(self):
        ArgumentName.dict_ = {}
        if 'def' in self.string:
            tree = ast.parse(self.tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.arguments):
                    function_name = node.args
                    ArgumentName.dict_.update({i.arg: i.lineno for i in function_name})

        for key, value in ArgumentName.dict_.items():
            if value == self.line:
                if re.match(r'(^[a-z\d]*_[a-z\d]*$)|(^[a-z\d]*$)', key) is None:
                    raise ArgumentCaseException(self.line, key)


# [S011]
class VariableName:
    def __init__(self, tree, line):
        self.tree = tree
        self.line = line

    def snake_case(self):
        var = []
        line = []
        shake_case = []
        tree = ast.parse(self.tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                variable_name = node.targets[0].__dict__.get('id')
                if variable_name is None:
                    break

                var_line = node.targets[0].lineno
                case_check = re.match(r'(^[a-z\d]*_[a-z\d]*_?[a-z\d]*$)|(^[a-z\d]*)$', variable_name) is not None

                var.append(variable_name)
                line.append(var_line)
                shake_case.append(case_check)

        var_dict = list(zip(var, line, shake_case))

        for i in range(len(var_dict)):
            if self.line == var_dict[i][1]:
                if var_dict[i][-1] is False:
                    raise VariableCaseException(self.line, var_dict[i][0])


# [S012]
class MutableArgument:
    def __init__(self, tree, line):
        self.tree = tree
        self.line = line

    def check_mutable_def_args(self):
        def_var_dict_ = {}
        tree = ast.parse(self.tree)

        for node in ast.walk(tree):
            help_dict = {}
            mutability_list = []
            if isinstance(node, ast.FunctionDef):
                function_name = node.args.defaults
                def_line = node.lineno
                for i in function_name:
                    if type(i) == ast.List or type(i) == ast.Dict or type(i) == ast.Set:
                        mutability_list.append(True)
                    else:
                        mutability_list.append(False)

                help_dict[def_line] = mutability_list
            def_var_dict_.update(help_dict)

        for key in def_var_dict_.keys():
            if key == self.line:
                if any(def_var_dict_[key]):
                    raise MutableDefaultValueException(self.line)


class OpenFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.n = 0

    def error_check(self, a, file=''):
        if not file.endswith('\\') and file.endswith('.py'):
            path = f'{self.file_path}\{file}:'
        else:
            path = f'{self.file_path}:'

        tree = ast.parse(open(path.rstrip(':')).read())

        for line, string in enumerate(a, 1):
            # [S001]
            try:
                LengthCheck(string, line).length_check()
            except LongStringException as error:
                print(path, error)
            # [S002]
            try:
                IndentationCheck(string, line).indentation_check()
            except IndentationException as error:
                print(path, error)
            # [S003]
            try:
                SemicolonCheck(string, line).semicolon_check()
            except UnnecessarySemicolon as error:
                print(path, error)
            # [S004]
            try:
                CommentSpaceCheck(string, line).comment_space_check()
            except InlineComments as error:
                print(path, error)
            # [S005]
            try:
                ToDoCheck(string, line).todo_check()
            except ToDo as error:
                print(path, error)
            # [S006]
            try:
                BlankSpace(string, line)
            except TwoBlankLines as error:
                print(path, error)
            # [S007]
            try:
                TooManySpaces(string, line).space_check()
            except ConstructionNameSpaceException as error:
                print(path, error)
            # [S008]
            try:
                CamelCase(string, line).camel_case()
            except CamelCaseException as error:
                print(path, error)
            # [S009]
            try:
                SnakeCase(string, line).snake_case()
            except ShakeCaseException as error:
                print(path, error)
            # [S010]
            try:
                ArgumentName(tree, string, line).snake_case()
            except ArgumentCaseException as error:
                print(path, error)
            # [S011]
            try:
                VariableName(tree, line).snake_case()
            except VariableCaseException as error:
                print(path, error)
            # [S012]
            try:
                MutableArgument(tree, line).check_mutable_def_args()
            except MutableDefaultValueException as error:
                print(path, error)

    def open_file(self):
        try:
            files = filter(lambda x: x.endswith('.py'), os.listdir(self.file_path))
            for file in list(files):
                os.chdir(self.file_path)
                with open(file, 'r') as open_file:
                    a = open_file.readlines()
                    OpenFile.error_check(self, a, open_file.name)

        except NotADirectoryError:
            with open(self.file_path, 'r') as open_file:
                a = open_file.readlines()
                OpenFile.error_check(self, a)


file1 = OpenFile(sys.argv[1])
file1.open_file()
