from functools import cached_property

from ..file import File


class JavaScriptFile(File):
    @cached_property
    def imports(self) -> list[File]:
        import_identifier_node = self.parser.query_by_capture_name(
            self.text, self.language.query_import_identifier, "name"
        )
        import_files = []
        for node in import_identifier_node:
            include = self.lsp.request_definition(
                self.relpath,
                node.start_point[0],
                node.start_point[1],
            )
            if len(include) == 0:
                continue
            include = include[0]
            include_abspath = include["absolutePath"]
            if include_abspath in self.project.files_abspath:
                import_files.append(self.project.files_abspath[include_abspath])
            else:
                # If the file is not in the project, we still add it to the imports
                import_files.append(File.create(include_abspath, self.project))
        return import_files
