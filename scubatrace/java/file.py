from functools import cached_property

from ..file import File
from . import language


class JavaFile(File):
    @property
    def package(self) -> str:
        package_node = self.parser.query_oneshot(self.text, language.JAVA.query_package)
        if package_node is None:
            return ""
        package = package_node.text.decode()  # type: ignore
        return package

    @cached_property
    def imports(self) -> list[File]:
        import_name_node = self.parser.query_all(
            self.text, language.JAVA.query_import_name
        )
        import_files = []
        for node in import_name_node:
            include = self.lsp.request_definition(
                self.relpath,
                node.start_point[0],
                node.start_point[1],
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
    def import_class(self) -> list[str]:
        import_node = self.parser.query_all(self.text, language.JAVA.query_import)
        imports = []
        for node in import_node:
            assert node.text is not None
            scoped_identifier = node.text.decode()
            imports.append(scoped_identifier)
        return imports
