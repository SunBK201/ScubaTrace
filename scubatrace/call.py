class Call:
    def __init__(self, src, dst, line: int, column: int):
        self.src = src
        self.dst = dst
        self.line = line
        self.column = column
        self._shared_report = None

    def __eq__(self, other):
        if not isinstance(other, Call):
            return False
        return (
            self.src == other.src
            and self.dst == other.dst
            and self.line == other.line
            and self.column == other.column
        )
