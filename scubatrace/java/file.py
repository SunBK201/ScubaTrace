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
    def import_class(self) -> list[str]:
        import_node = self.parser.query_all(self.text, language.JAVA.query_import)
        imports = []
        for node in import_node:
            assert node.text is not None
            scoped_identifier = node.text.decode()
            imports.append(scoped_identifier)
        return imports
