import sublime
import sublime_plugin
import os
import os.path
import subprocess

class TortoiseSvnCommand(sublime_plugin.WindowCommand):
	def run(self, cmd, paths=None, isHung=False):
		dir = self.getPath(paths)

		if not dir:
			return
			
		settings = sublime.load_settings('TortoiseSVN.sublime-settings')
		tortoiseproc_path = settings.get('tortoiseproc_path')

		if not os.path.isfile(tortoiseproc_path):
			sublime.error_message(''.join(['can\'t find TortoiseProc.exe,',
				' please config setting file', '\n   --sublime-TortoiseSVN']))
			raise

		proce = subprocess.Popen('"' + tortoiseproc_path + '"' + 
			' /command:' + cmd + ' /path:"%s"' % dir , stdout=subprocess.PIPE)

		# This is required, cause of ST must wait TortoiseSVN update then revert
		# the file. Otherwise the file reverting occur before SVN update, if the
		# file changed the file content in ST is older.
		if isHung:
			proce.communicate()

	def getPath(self, paths):
		path = None
		if paths:
			path = '*'.join(paths)
		else:
			view = sublime.active_window().active_view()
			path = view.file_name() if view else None

		return path


class MutatingTortoiseSvnCommand(TortoiseSvnCommand):
	def run(self, cmd, paths=None):
		TortoiseSvnCommand.run(self, cmd, paths, True)
		
		self.view = sublime.active_window().active_view()
		(row,col) = self.view.rowcol(self.view.sel()[0].begin())
		self.lastLine = str(row + 1);
		sublime.set_timeout(self.revert, 100)

	def revert(self):
		self.view.run_command('revert')
		sublime.set_timeout(self.revertPoint, 600)

	def revertPoint(self):
		self.view.window().run_command('goto_line',{'line':self.lastLine})


class SvnUpdateCommand(MutatingTortoiseSvnCommand):
	def run(self, paths=None):
		settings = sublime.load_settings('TortoiseSVN.sublime-settings')
		closeonend = '3' if True == settings.get('autoCloseUpdateDialog') else '0'
		MutatingTortoiseSvnCommand.run(self, 'update /closeonend:'+closeonend, paths)


class SvnCommitCommand(TortoiseSvnCommand):
	def run(self, paths=None):
		TortoiseSvnCommand.run(self, 'commit', paths)


class SvnRevertCommand(MutatingTortoiseSvnCommand):
	def run(self, paths=None):
		MutatingTortoiseSvnCommand.run(self, 'revert', paths)


class SvnLogCommand(TortoiseSvnCommand):
	def run(self, paths=None):
		TortoiseSvnCommand.run(self, 'log', paths)


class SvnDiffCommand(TortoiseSvnCommand):
	def run(self, paths=None):
		TortoiseSvnCommand.run(self, 'diff', paths)


class SvnBlameCommand(TortoiseSvnCommand):
	def run(self, paths=None):
		TortoiseSvnCommand.run(self, 'blame', paths)

	def is_visible(self, paths=None):
		file = self.getPath(paths)
		return os.path.isfile(file) if file else False
