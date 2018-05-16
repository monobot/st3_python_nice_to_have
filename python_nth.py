import os
import string
import sublime
import sublime_plugin


class _FileBaseClass(sublime_plugin.TextCommand):

    def is_enabled(self):
        return bool(self.view.file_name())

    def get_path(self):
        return min(
            (
                os.path.relpath(self.view.file_name(), folder)
                for folder in self.view.window().folders()
            ),
            key=len,
        )


class CopyRelativePathCommand(_FileBaseClass):
    def run(self, edit):
        minimal_path = self.get_path()
        sublime.set_clipboard(minimal_path)


class CopyPackageRelativePathCommand(_FileBaseClass):
    def run(self, edit):
        minimal_path = self.get_path()
        trim_file_extension = '.'.join(minimal_path.split('.')[:-1])
        sublime.set_clipboard(trim_file_extension.replace('/', '.'))


class CopyReferenceCommand(_FileBaseClass):
    def is_enabled(self):
        return len(self.view.sel()) == 1

    def run(self, edit):
        minimal_path = self.get_path()
        trim_file_extension = '.'.join(minimal_path.split('.')[:-1])
        reference = self.view.sel()[0]
        if reference.begin() == reference.end():
            reference = self.view.word(reference)

        trim_file_extension += '.' + self.view.substr(reference)
        sublime.set_clipboard(trim_file_extension.replace('/', '.'))


class CopyFilenameCommand(_FileBaseClass):
    def run(self, edit):
        minimal_path = self.get_path()
        trim_file_extension = '.'.join(minimal_path.split('.')[:-1])
        sublime.set_clipboard(trim_file_extension.replace('/', '.'))


class _RegionBaseClass(sublime_plugin.TextCommand):

    def is_enabled(self):
        return bool(self.view.sel())

    def run(self, edit):
        for sel in self.view.sel():
            current_text = self.view.substr(sel)
            already_changed = []
            while self.view.find(current_text, 0):
                sub_sel = self.view.find(current_text, 0)
                if sub_sel not in already_changed:
                    already_changed.append(sub_sel)
                else:
                    break
                self.view.replace(
                    edit,
                    sub_sel,
                    text=self.converter(current_text)
                )


class RefactorCamelcaseCommand(_RegionBaseClass):

    def converter(self, txt):
        response_txt = txt.lstrip().lstrip('_')
        if response_txt:
            normalized_txt = txt.replace('_', '||').replace(' ', '||')

            response_txt = ''
            cap_next = False
            for char in normalized_txt:
                if cap_next:
                    char = char.capitalize()
                    cap_next = False

                if char != '|':
                    response_txt += char
                else:
                    cap_next = True

        return response_txt


class RefactorUnderscoreCommand(_RegionBaseClass):

    def converter(self, txt):
        response_txt = txt.lstrip()
        if txt:
            response_txt = txt[0].lower()
            for char in txt[1:]:
                if char in string.ascii_uppercase:
                    char = '_' + char.lower()
                response_txt += char

        return response_txt
        return txt[::-1]


class RefactorCapfirstCommand(_RegionBaseClass):

    def converter(self, txt):
        if txt:
            txt = txt[0].capitalize() + txt[1:]
        return txt
