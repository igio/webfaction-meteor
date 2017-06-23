#!/usr/bin/env python3

import os
import subprocess
import paramiko
import argparse

# Manage the command line arguments

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--update', action='store_true', help='Update the application')
parser.add_argument('-b', '--build', action='store_true', help='If true, build application before update. Defaults to true.')
parser.add_argument('-f', '--file', help='Settings file')

args = parser.parse_args()
if args.update:
    update = True
else:
    update = False

if args.build:
    build = True
else:
    build = False

# Read the settings from file
with open(args.file) as settings_file:
    settings = json.load(settings_file)

# Set up some variables for improved legibility

local = settings['local']
server = settings['server']
db = settings['db']

##
# Steps
#
# Build the app
# Upload app at appropriate locations
# Unpack
# Install dependencies
# Generate and upload the startup file
# Run the application
##

# Build the app

temp_folder = os.path.expanduser('~/%s/%s_build' % (local['path'], local['app']))

if build:
    cmds = [
        'cd %s/%s' % (local['path'], local['app']),
        'meteor build %s --architecture os.linux.x86_64 --server %s' % (temp_folder, server['url'])
        ]
    print('Building application...')
    output = subprocess.check_output(";".join(cmds), shell=True)
    print(output.decode(encoding='utf-8'))

# Connect to server and upload the app built

print('Connecting to the server...')
conn = paramiko.SSHClient()
conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
conn.connect(server['remote'], username=server['user'], password=server['password'])
print('Connection established!')
print('Starting SFTP session...')
sftp = conn.open_sftp()
print('SFTP session open!')
sftp.chdir('webapps/%s' % server['app'])
print('Start uploading app archive...')
sftp.put('%s/%s.tar.gz' % (temp_folder, local['app']), '%s.tar.gz' % local['app'])
print('Upload done!')

# Unpack

print('Extracting archive files...')
cmds = [
    'cd ~/webapps/%s' % server['app'],
    'rm -rf bundle',
    'tar -zxf %s.tar.gz' % local['app'],
    'rm %s.tar.gz' % local['app']
]
si, so, se = conn.exec_command(';'.join(cmds))
print(''.join(so.readlines()))
print('Files extracted!')

# Install dependencies

print('Installing dependencies...')
cmds = [
    'cd ~/webapps/%s/bundle/programs/server' % server['app'],
    'PATH=~/webapps/%s/bin/:$PATH' % server['app'],
    'npm install --silent'
]
si, so, se = conn.exec_command(';'.join(cmds))
print(''.join(so.readlines()))
print('Dependencies installed!')

# Generate and upload the startup file

if not update:
    print('Generate startup file...')
    base = '/home/%s/webapps/%s' % (server['user'], server['app'])
    lines = [
        '#!/bin/sh',
        'mkdir -p %s/run' % base,
        'export MONGO_URL=%s' % db['mongodb'],
        'export ROOT_URL=%s' % server['url'],
        'export PORT=%s' % server['port'],
        'pid=$(/sbin/pidof %s/bin/node)' % base,
        'if echo "$pid" | grep -q " "; then',
        '   pid=""',
        'fi',
        'if [ -n "$pid" ]; then',
        '   user=$(ps -p $pid -o user:20 | tail -n 1)',
        '   if [ $user = "gionas" ]; then',
        '       exit(0)',
        '   fi',
        'fi',
        'nohup %s/bin/node %s/bundle/main.js > /dev/null 2>&1 &' % (base, base),
        '/sbin/pidof %s/bin/node > %s/run/node.pid' % (base, base)
    ]
    file = open('%s/start' % temp_folder, 'w')
    file.write('\n'.join(lines))
    print('Remove the current start file...')
    cmds = [
        'cd ~/webapps/%s/bin' % server['app'],
        'rm start'
    ]
    si, so, se = conn.exec_command(';'.join(cmds))
    if not se:
        print('Start file removed!')
    else:
        print(''.join(se.readlines()))
        exit(1)
    print('Uploading new start file...')
    sftp.chdir('webapps/%s/bin' % server['app'])
    sftp.put('%s/start' % temp_folder)
    print('Start file uploaded!')

# Start the application (if everything worked out fine)

print('(re)Starting the app...')
cmds = [
    '~/webapps/%s/bin/stop' % server['app'],
    '~/webapps/%s/bin/start' % server['app']
]
si, so, se = conn.exec_command(';'.join(cmds))
print('Meteor application started')

conn.close()
print('All done! Good bye!')
