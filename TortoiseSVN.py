import sublime
import sublime_plugin
import os
import subprocess


def execut_command(command,path):
	settings = sublime.load_settings('TortoiseSVN.sublime-settings')
	tortoiseproc = settings.get('tortoiseproc_path');
	cmd = [tortoiseproc, '/closeonend:3', ('/command:' + command), ('/path:' + path)]
	#cmd = '"%s" /closeonend:3 /command:%s /path:%s' % (tortoiseproc, command, path)
	popen = subprocess.Popen(cmd)
	popen.communicate()

class SvnUpdateCommand(sublime_plugin.TextCommand):
	def run(self, edit, paths=None):
		if paths:
			dir = '*'.join(paths)
		else:
			dir = self.view.file_name()

		execut_command('update', dir)
		(row,col) = self.view.rowcol(self.view.sel()[0].begin())
		self.lastLine = str(row + 1);

		if not paths:
			sublime.set_timeout(self.revert, 100)

	def revert(self):
		self.view.run_command('revert')
		sublime.set_timeout(self.revertPoint, 600)

	def revertPoint(self):
		self.view.window().run_command('goto_line',{'line':self.lastLine})



class SvnCommitCommand(sublime_plugin.TextCommand):
	def run(self, edit, paths=None):
		if paths:
			dir = '*'.join(paths)
		else:
			dir = self.view.file_name()

		execut_command('commit', dir)

