import sublime
import sublime_plugin
import os

def execut_command(command,path):
	settings = sublime.load_settings('TortoiseSVN.sublime-settings')
	tortoiseproc = settings.get('tortoiseproc_path');
	cmd = '"%s" /closeonend:3 /command:%s /path:%s' % (tortoiseproc, command, path)
	os.popen(cmd)

class SvnUpdateCommand(sublime_plugin.TextCommand):
	def run(self, edit, paths=None):
		if paths:
			dir = '*'.join(paths)
		else:
			dir = self.view.file_name()

		execut_command('update', dir)

class SvnCommitCommand(sublime_plugin.TextCommand):
	def run(self, edit, paths=None):
		if paths:
			dir = '*'.join(paths)
		else:
			dir = self.view.file_name()

		execut_command('commit', dir)

