import re
from functools import cached_property

from ..identifier import Identifier


class CIdentifier(Identifier):
    @cached_property
    def type_info(self) -> str:
        type_info = ""
        hover = self.lsp.request_hover(
            self.file.relpath, self.start_line - 1, self.start_column - 1
        )
        if hover is None:
            return type_info
        contents = hover["contents"]
        if isinstance(contents, dict):
            value = contents.get("value", "")
        else:
            value = contents
        if not isinstance(value, str):
            return type_info
        pattern = r"\s+Type:\s+(.*)\s+"
        match = re.search(pattern, value)
        if match:
            type_info = match.group(1)
        return type_info.strip()

    @property
    def is_pointer(self) -> bool:
        return self.type_info.endswith("*")
