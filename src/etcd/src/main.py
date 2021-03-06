#
# Copyright 2014 iXsystems, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#####################################################################

import os
import sys
import signal
import logging
import argparse
import json
import errno
import datastore
import time
import imp
import renderers
from bsd import setproctitle
from datastore.config import ConfigStore
from freenas.dispatcher.client import Client, ClientError
from freenas.dispatcher.rpc import RpcService, RpcException
from freenas.utils import configure_logging
from freenas.utils.debug import DebugService
from freenas.serviced import checkin


DEFAULT_CONFIGFILE = '/usr/local/etc/middleware.conf'
TEMPLATE_RENDERERS = {
    '.mako': renderers.MakoTemplateRenderer,
    '.py': renderers.PythonRenderer,
    '.shell': renderers.ShellTemplateRenderer,
}


class ManagementService(RpcService):
    def __init__(self, ctx):
        self.context = ctx

    def rescan_plugins(self):
        self.context.scan_plugins()

    def die(self):
        pass


class FileGenerationService(RpcService):
    def __init__(self, ctx):
        self.context = ctx
        self.context.generate_all = self.generate_all
        self.datastore = ctx.datastore

    def generate_all(self):
        for group in self.datastore.query('etcd.groups'):
            self.generate_group(group['name'])

    def generate_file(self, filename):
        if filename not in self.context.managed_files.keys():
            return

        text = self.context.generate_file(filename)
        filepath = os.path.join(self.context.root, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as fd:
                fd.write(text)
        except FileNotFoundError as e:
            self.context.logger.error('Failed to open {0}: {1}'.format(filepath, e), exc_info=True)
            return

        self.context.emit_event('etcd.file_generated', {
            'filename': filepath,
        })

    def generate_plugin(self, name):
        if name not in self.context.managed_files.keys():
            return

        try:
            pname = os.path.basename(name)
            plugin = imp.load_source(pname, self.context.managed_files[name])
        except:
            self.context.logger.error('Invalid plugin source file: {0}'.format(name), exc_info=True)
            return

        if not hasattr(plugin, 'run'):
            self.context.logger.error('Invalid plugin source {0}, no run method'.format(pname))
            return

        try:
            plugin.run(self.context)
        except Exception as err:
            self.context.logger.error('Cannot run plugin {0}: {1}'.format(name, str(err)), exc_info=True)

    def generate_group(self, name):
        group = self.datastore.get_one('etcd.groups', ('name', '=', name))
        if not group:
            raise RpcException(errno.ENOENT, 'Group {0} not found'.format(name))

        for i in group['dependencies']:
            typ, fname = i.split(':')

            if typ == 'file':
                self.generate_file(fname)
            elif typ == 'plugin':
                self.generate_plugin(fname)
            elif typ == 'group':
                self.generate_group(fname)

    def get_managed_files(self):
        return self.context.managed_files

    def get_groups(self):
        return [g['name'] for g in self.datastore.query('etcd.groups')]


class Main(object):
    def __init__(self):
        self.logger = logging.getLogger('etcd')
        self.root = None
        self.generate_all = None
        self.configfile = None
        self.config = None
        self.datastore = None
        self.configstore = None
        self.client = None
        self.plugin_dirs = []
        self.renderers = {}
        self.managed_files = {}

    def init_datastore(self):
        try:
            self.datastore = datastore.get_datastore(self.configfile)
        except datastore.DatastoreException as err:
            self.logger.error('Cannot initialize datastore: %s', str(err))
            sys.exit(1)

        self.configstore = ConfigStore(self.datastore)

    def init_dispatcher(self):
        def on_error(reason, **kwargs):
            if reason in (ClientError.CONNECTION_CLOSED, ClientError.LOGOUT):
                self.logger.warning('Connection to dispatcher lost')
                self.connect()

        self.client = Client()
        self.client.on_error(on_error)
        self.connect()

    def connect(self):
        while True:
            try:
                self.client.connect('unix:')
                self.client.login_service('etcd')
                self.client.enable_server()
                self.client.register_service('etcd.generation', FileGenerationService(self))
                self.client.register_service('etcd.management', ManagementService(self))
                self.client.register_service('etcd.debug', DebugService())
                self.client.resume_service('etcd.generation')
                self.client.resume_service('etcd.management')
                self.client.resume_service('etcd.debug')
                return
            except (OSError, RpcException) as err:
                self.logger.warning('Cannot connect to dispatcher: {0}, retrying in 1 second'.format(str(err)))
                time.sleep(1)

    def init_renderers(self):
        for name, impl in TEMPLATE_RENDERERS.items():
            self.renderers[name] = impl(self)

    def parse_config(self, filename):
        try:
            f = open(filename, 'r')
            self.config = json.load(f)
            f.close()
        except IOError as err:
            self.logger.error('Cannot read config file: %s', err.message)
            sys.exit(1)
        except ValueError:
            self.logger.error('Config file has unreadable format (not valid JSON)')
            sys.exit(1)

        self.plugin_dirs = self.config['etcd']['plugin-dirs']

    def scan_plugins(self):
        for i in self.plugin_dirs:
            self.scan_plugin_dir(i)

    def scan_plugin_dir(self, dir):
        self.logger.debug('Scanning plugin directory %s', dir)
        for root, dirs, files in os.walk(dir):
            for name in files:
                abspath = os.path.join(root, name)
                path = os.path.relpath(abspath, dir)
                name, ext = os.path.splitext(path)

                if name in self.managed_files.keys():
                    continue

                if ext in TEMPLATE_RENDERERS.keys():
                    self.managed_files[name] = abspath
                    self.logger.info('Adding managed file %s [%s]', name, ext)

    def generate_file(self, file_path):
        if file_path not in self.managed_files.keys():
            raise RpcException(errno.ENOENT, 'No such file')

        template_path = self.managed_files[file_path]
        name, ext = os.path.splitext(template_path)
        if ext not in self.renderers.keys():
            raise RuntimeError("Can't find renderer for {0}".format(file_path))

        renderer = self.renderers[ext]
        try:
            return renderer.render_template(template_path)
        except Exception as e:
            self.logger.warn('Cannot generate file {0}: {1}'.format(file_path, str(e)))
            return "# FILE GENERATION FAILED: {0}\n".format(str(e))

    def emit_event(self, name, params):
        self.client.emit_event(name, params)

    def checkin(self):
        checkin()
        os.kill(1, signal.SIGHUP)

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', metavar='CONFIG', default=DEFAULT_CONFIGFILE, help='Middleware config file')
        parser.add_argument('-f', action='store_true', default=False, help='Run in foreground')
        parser.add_argument('mountpoint', metavar='MOUNTPOINT', default='/etc', help='/etc mount point')
        args = parser.parse_args()
        configure_logging('etcd', 'DEBUG')

        setproctitle('etcd')
        self.root = args.mountpoint
        self.configfile = args.c
        self.parse_config(args.c)
        self.scan_plugins()
        self.init_renderers()
        self.init_datastore()
        self.init_dispatcher()
        self.generate_all()
        self.checkin()
        self.client.wait_forever()

if __name__ == '__main__':
    m = Main()
    m.main()

