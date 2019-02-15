import sublime
import sublime_plugin
import os
import os.path
import subprocess

class TortoiseSvnCommand(sublime_plugin.WindowCommand):
    def run(self, cmd, paths=None, isHung=False):
        if paths is not None:
            for index, path in enumerate(paths):
              if "${PROJECT_PATH}" in path:
                  project_data  = sublime.active_window().project_data()
                  project_folder = project_data['folders'][0]['path']
                  path = path.replace("${PROJECT_PATH}", project_folder);
                  paths[index] = path
        dir = self.get_path(paths)

        if not dir:
            return

        settings = self.get_setting()
        tortoiseproc_path = settings.get('tortoiseproc_path')
        pathEncoding = settings.get('pathEncoding')

        if not os.path.isfile(tortoiseproc_path):
            sublime.error_message('can\'t find TortoiseProc.exe,'
                ' please config setting file' '\n   --sublime-TortoiseSVN')
            raise

        cmd = '"' + tortoiseproc_path + '"' + ' /command:' + cmd + ' /path:"%s"' % dir

        proce = subprocess.Popen(cmd.encode(pathEncoding) if pathEncoding else cmd , stdout=subprocess.PIPE)

        # This is required, cause of ST must wait TortoiseSVN update then revert
        # the file. Otherwise the file reverting occur before SVN update, if the
        # file changed the file content in ST is older.
        if isHung:
            proce.communicate()

    def get_path(self, paths):
        path = None
        if paths:
            path = '*'.join(paths)
        else:
            view = sublime.active_window().active_view()
            path = view.file_name() if view else None

        return path

    def get_setting(self):
        return sublime.load_settings('TortoiseSVN.sublime-settings')


class MutatingTortoiseSvnCommand(TortoiseSvnCommand):
    def run(self, cmd, paths=None):
        TortoiseSvnCommand.run(self, cmd, paths, True)

        self.view = sublime.active_window().active_view()
        row, col = self.view.rowcol(self.view.sel()[0].begin())
        self.lastLine = str(row + 1);
        sublime.set_timeout(self.revert, 100)

    def revert(self):
        self.view.run_command('revert')
        sublime.set_timeout(self.revertPoint, 600)

    def revertPoint(self):
        self.view.window().run_command('goto_line', {'line':self.lastLine})


class SvnUpdateCommand(MutatingTortoiseSvnCommand):
    def run(self, paths=None):
        settings = self.get_setting()
        closeonend = ('3' if True == settings.get('autoCloseUpdateDialog')
            else '0')
        MutatingTortoiseSvnCommand.run(self, 'update /closeonend:' + closeonend,
            paths)


class SvnCommitCommand(TortoiseSvnCommand):
    def run(self, paths=None):
        settings = self.get_setting()
        closeonend = ('3' if True == settings.get('autoCloseCommitDialog')
            else '0')
        TortoiseSvnCommand.run(self, 'commit /closeonend:' + closeonend, paths)


class SvnRevertCommand(MutatingTortoiseSvnCommand):
    def run(self, paths=None):
        MutatingTortoiseSvnCommand.run(self, 'revert', paths)


class SvnLogCommand(TortoiseSvnCommand):
    def run(self, paths=None):
        TortoiseSvnCommand.run(self, 'log', paths)


class SvnSwitchCommand(TortoiseSvnCommand):
    def run(self, paths=None):
        TortoiseSvnCommand.run(self, 'switch', paths)


class SvnDiffCommand(TortoiseSvnCommand):
    def run(self, paths=None):
        TortoiseSvnCommand.run(self, 'diff', paths)


class SvnBlameCommand(TortoiseSvnCommand):
    def run(self, paths=None):
        view = sublime.active_window().active_view()
        row = view.rowcol(view.sel()[0].begin())[0] + 1

        TortoiseSvnCommand.run(self, 'blame /line:' + str(row), paths)

    def is_visible(self, paths=None):
        file = self.get_path(paths)
        return os.path.isfile(file) if file else False


class SvnAddCommand(TortoiseSvnCommand):
    def run(self, paths=None):
        TortoiseSvnCommand.run(self, 'add', paths)


class SvnBranchCommand(TortoiseSvnCommand):
    def run(self, paths=None):
        TortoiseSvnCommand.run(self, 'copy', paths)
