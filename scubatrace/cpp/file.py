from functools import cached_property

from ..file import File
from . import language


class CFile(File):
    def __init__(self, path: str, project):
        super().__init__(path, project)

    @cached_property
    def imports(self) -> list[File]:
        include_node = self.parser.query_all(
            self.text, language.C.query_include
        )
        import_files = []
        for node in include_node:
            include_path_node = node.child_by_field_name("path")
            if include_path_node is None:
                continue
            include = self.lsp.request_definition(
                self.relpath,
                include_path_node.start_point[0],
                include_path_node.start_point[1],
            )
            if len(include) == 0:
                continue
            include = include[0]
            include_abspath = include["absolutePath"]
            if include_abspath not in self.project.files_abspath:
                continue
            import_files.append(self.project.files_abspath[include_abspath])
        return import_files

    @cached_property
    def source_header(self) -> File | None:
        """
        switch between the main source file (*.cpp) and header (*.h)
        """
        uri = self.lsp.request_switch_source_header(self.relpath, self.uri)
        if len(uri) == 0:
            return None
        return self.project.files_uri.get(uri, None)
