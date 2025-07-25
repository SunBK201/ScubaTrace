from functools import cached_property

from ..file import File


class CFile(File):
    @cached_property
    def source_header(self) -> File | None:
        """
        switch between the main source file (*.cpp) and header (*.h)
        """
        uri = self.lsp.request_switch_source_header(self.relpath, self.uri)
        if len(uri) == 0:
            return None
        return self.project.files_uri.get(uri, None)
