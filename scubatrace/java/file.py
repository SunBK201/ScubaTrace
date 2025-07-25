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
