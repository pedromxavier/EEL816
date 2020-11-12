from collections import deque

from .parser import parser

class Compiler:

    init_key = 'INIT'

    def __init__(self, parser, instructions: dict):
        self.parser = parser
        self.instructions = instructions

        self.queue = deque([])
        self.env = {}

    def reset(self):
        self.queue.clear()
        self.env.clear()
        self.init()

    def init(self):
        if self.init_key in self.instructions:
            self.instructions[self.init_key](self)

    def compile(self, source, bytecode=False):
        return [item for item in self._compile(source, bytecode=bytecode) if item is not None]

    def _compile(self, source, bytecode=False):
        self.reset()

        self.queue.extendleft(self.parser.parse(source))

        if bytecode: ## intermediate code
            while self.queue:
                yield self.queue.pop()
        else: ## exec
            if self.init_key in self.instructions:
                self.instructions[self.init_key](self)
        
            while self.queue:
                cmd, *args = self.queue.pop()
                yield self.instructions[cmd](self, *args)