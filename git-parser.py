#!/usr/bin/env python

import re
import argparse
from openpyxl import Workbook
import subprocess

# illegal characters parse
ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013]-[\014]|[\016-\037]')

# array to store dict of commit data
commits = []
angular_types = ['build', 'ci', 'docs', 'feat', 'fix', 'pref', 'refactor', 'style', 'test']
	

def parseCommit(commitLines):
	# dict to store commit data
	commit = {}
	# iterate lines and save
	for nextLine in commitLines:
		if nextLine == '' or nextLine == '\n':
			# ignore empty lines
			pass
		elif bool(re.match('commit', nextLine, re.IGNORECASE)):
			# commit xxxx
			if len(commit) != 0:		## new commit, so re-initialize
				commits.append(commit)
				commit = {}
			commit = {'hash' : re.match('commit (.*)', nextLine, re.IGNORECASE).group(1) }
		elif bool(re.match('Merge ', nextLine, re.IGNORECASE)):
			# Merge xxxx xxxx
			pass
		elif bool(re.match('Merge: ', nextLine, re.IGNORECASE)):
			# Merge: xxxx xxxx
			pass
		elif bool(re.match('author:', nextLine, re.IGNORECASE)):
			# Author: xxxx <xxxx@xxxx.com>
			m = re.compile('Author: (.*) <(.*)>').match(nextLine)
			commit['author'] = m.group(1)
			commit['email'] = m.group(2)
		elif bool(re.match('date:', nextLine, re.IGNORECASE)):
			# Date: xxx
			date = re.compile('Date:   (.*)').match(nextLine).group(1)
			commit['date'] = date
		elif bool(re.match('    ', nextLine, re.IGNORECASE)):
			# (4 empty spaces)
			message = nextLine.strip()
			if(len(message) == 0):
				continue

			#header- AngularJS types
			typeBefore = commit.get('type')
			for type in angular_types:
				if bool(re.match(type, message, re.IGNORECASE)):
					commit['type'] = type
					if bool(re.match(type + ':', message, re.IGNORECASE)):
						m = re.compile(type + ':(.*)').match(message)
						commit['subject'] = m.group(1).strip()
						continue
					elif bool(re.match(type + '\((.*)\):', message, re.IGNORECASE)):
						m = re.compile(type + '\((.*)\):(.*)', re.IGNORECASE).match(message)
						commit['scope'] = m.group(1)
						commit['subject'] = m.group(2).strip()
						continue
			typeAfter = commit.get('type')
			if typeBefore != typeAfter:
				continue

			#footer - Breaking change
			if bool(re.match('BREAKING CHANGE', message, re.IGNORECASE)):
				m = re.compile('BREAKING CHANGE (.*)').match(message)
				commit['BreakingChange'] = m.group(1)
				continue

			#footer - issue
			if bool(re.match('Closes', message, re.IGNORECASE)):
				m = re.compile('Closes (.*)').match(message)
				if commit.get('issue') is None:
					commit['issue'] = m.group(1)
				else:
					issue = commit.get('issue')
					commit['issue'] = issue + ',' + m.group(1)
				continue

			#footer - change-id (ignore)
			if bool(re.match('Change-Id', message, re.IGNORECASE)):
				continue

			#body
			if(len(message) == 0):
				continue
			commit['body'] = message

		else:
			print ('ERROR: Unexpected Line: ' + nextLine)

def save_to_excel():
	wb = Workbook()
	ws = wb.active
	ws.append(['Commit Hash', 'Author', 'Email', 'Date', 'Type', 'Scope', 'Subject', 'Body', 'Issues', 'BreakingChange'])
	for commit in commits:
			commit_info = [commit.get('hash'), commit.get('author'), commit.get('email'), commit.get('date'), commit.get('type'), commit.get('scope'), commit.get('subject'), commit.get('body'), commit.get('issue'), commit.get('BreakingChange')]
			try:
				ws.append(commit_info)
			except Exception as e:
				for item in commit_info:
					if item is str:
						item = ILLEGAL_CHARACTERS_RE.sub(r'', item)

	wb.save('./git_log.xlsx')
	print("Git log saved to git_log.xlsx")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='基于AngularJS规范的GitLog提取小脚本')
	parser.add_argument('--after', '-after', default=None,help='选择需要提取的Git Log起始日期(YYYY-MM-DD)')
	parser.add_argument('--before', '-before', default=None,help='选择需要提取的Git Log终止日期(YYYY-MM-DD)')
	args = parser.parse_args()

	content = []

	if args.after is None:
		if args.before is None:
			command = 'git log --date=short'
			output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
			content = output.split('\n')
		else:
			command = 'git log --date=short --before=' + args.before
			output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
			content = output.split('\n')

		parseCommit(content)
	else:
		if args.before is None:
			command = 'git log --date=short --since=' + args.after
			output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
			content = output.split('\n')
		else:
			command = 'git log --date=short --since=' + args.after + ' --before=' + args.before
			output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
			content = output.split('\n')

		parseCommit(content)

	if(len(commits) != 0):
		save_to_excel()
	