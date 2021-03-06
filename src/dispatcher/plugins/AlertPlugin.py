#
# Copyright 2015 iXsystems, Inc.
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

import errno
import logging
from typing import Optional, List, Set, Any
from collections import deque
from datetime import datetime

from datastore import DatastoreException
from freenas.dispatcher.rpc import (
    RpcException,
    SchemaHelper as h,
    accepts,
    description,
    returns,
    private,
    generator
)
from task import Provider, Task, TaskException, TaskDescription, query
from freenas.dispatcher.model import BaseStruct, BaseEnum, BaseVariantType
from freenas.dispatcher.model.typing import Range
from freenas.utils import normalize, query as q
from debug import AttachRPC


logger = logging.getLogger('AlertPlugin')
registered_alerts = {}
pending_alerts = deque()
pending_cancels = deque()


class AlertSeverity(BaseEnum):
    CRITICAL = 'CRITICAL'
    WARNING = 'WARNING'
    INFO = 'INFO'


class Alert(BaseStruct):
    id: int
    clazz: str
    subtype: str
    severity: AlertSeverity
    target: str
    title: str
    description: str
    user: str
    happened_at: datetime
    cancelled_at: Optional[datetime]
    dismissed_at: Optional[datetime]
    last_emitted_at: Optional[datetime]
    active: bool
    dismissed: bool
    one_shot: bool
    send_count: int
    properties: dict


class AlertClass(BaseStruct):
    id: str
    type: str
    subtype: str
    severity: AlertSeverity


class AlertEmitterConfig(BaseVariantType):
    pass


class AlertEmitterParameters(BaseVariantType):
    pass


class AlertEmitter(BaseStruct):
    id: str
    name: str
    config: AlertEmitterConfig


class AlertPredicateOperator(BaseEnum):
    EQ = '=='
    NE = '!='
    LE = '<='
    GE = '>='
    LT = '<'
    GT = '>'
    MATCH = '~'


class AlertPredicate(BaseStruct):
    property: str
    operator: AlertPredicateOperator
    value: Any


class AlertFilter(BaseStruct):
    id: str
    index: Range[int, 0]
    clazz: str
    emitter: str
    parameters: AlertEmitterParameters
    predicates: List[AlertPredicate]


@description('Provides access to the alert system')
class AlertsProvider(Provider):
    @query('Alert')
    @generator
    def query(self, filter=None, params=None):
        return self.datastore.query_stream('alerts', *(filter or []), **(params or {}))

    @private
    @accepts(str, str)
    @returns(h.one_of(h.ref('Alert'), None))
    def get_active_alert(self, cls, target):
        return self.datastore.query(
            'alerts',
            ('clazz', '=', cls), ('target', '=', target), ('active', '=', True),
            single=True
        )

    @description("Dismisses an alert")
    def dismiss(self, id: int) -> None:
        alert = self.datastore.get_by_id('alerts', id)
        if not alert:
            raise RpcException(errno.ENOENT, 'Alert {0} not found'.format(id))

        if alert['dismissed']:
            raise RpcException(errno.ENOENT, 'Alert {0} is already dismissed'.format(id))

        if alert['one_shot']:
            alert['active'] = False

        alert.update({
            'dismissed': True,
            'dismissed_at': datetime.utcnow()
        })

        self.datastore.update('alerts', id, alert)
        self.dispatcher.dispatch_event('alert.changed', {
            'operation': 'update',
            'ids': [id]
        })

    @description("Dismisses/Deletes all alerts from the database")
    def dismiss_all(self) -> None:
        alert_list = self.query([('dismissed', '=', False)])
        alert_ids = []
        for alert in alert_list:
            alert.update({
                'dismissed': True,
                'dismissed_at': datetime.utcnow()
            })
            self.datastore.update('alerts', alert['id'], alert)
            alert_ids.append(alert['id'])

        if alert_ids:
            self.dispatcher.dispatch_event('alert.changed', {
                'operation': 'update',
                'ids': alert_ids
            })

    @private
    @description("Emits an event for the provided alert")
    @accepts(h.all_of(
        h.ref('Alert'),
        h.required('clazz')
    ))
    @returns(int)
    def emit(self, alert):
        cls = self.datastore.get_by_id('alert.classes', alert['clazz'])
        if not cls:
            raise RpcException(errno.ENOENT, 'Alert class {0} not found'.format(alert['clazz']))

        normalize(alert, {
            'when': datetime.utcnow(),
            'dismissed': False,
            'active': True,
            'one_shot': False,
            'severity': cls['severity']
        })

        alert.update({
            'type': cls['type'],
            'subtype': cls['subtype'],
            'send_count': 0
        })

        id = self.datastore.insert('alerts', alert)
        self.dispatcher.dispatch_event('alert.changed', {
            'operation': 'create',
            'ids': [id]
        })

        try:
            self.dispatcher.call_sync('alertd.alert.emit', id)
        except RpcException as err:
            if err.code == errno.ENOENT:
                # Alertd didn't start yet. Add alert to the pending queue
                pending_alerts.append(id)
            else:
                raise

        return id

    @private
    @description("Cancels already scheduled alert")
    def cancel(self, id: int) -> int:
        alert = self.datastore.get_by_id('alerts', id)
        if not alert:
            raise RpcException(errno.ENOENT, 'Alert {0} not found'.format(id))

        if not alert['active']:
            raise RpcException(errno.ENOENT, 'Alert {0} is already cancelled'.format(id))

        alert.update({
            'active': False,
            'cancelled_at': datetime.utcnow()
        })

        self.datastore.update('alerts', id, alert)
        self.dispatcher.dispatch_event('alert.changed', {
            'operation': 'update',
            'ids': [id]
        })

        try:
            self.dispatcher.call_sync('alertd.alert.cancel', id)
        except RpcException as err:
            if err.code == errno.ENOENT:
                # Alertd didn't start yet. Add alert to the pending queue
                pending_cancels.append(id)
            else:
                raise

        return id

    @description("Returns list of registered alerts")
    def get_alert_classes(self) -> List[AlertClass]:
        return self.datastore.query('alert.classes')

    @description("Returns list of registered alert severities")
    def get_alert_severities(self) -> Set[AlertSeverity]:
        alert_classes = self.get_alert_classes()
        return {alert_class['severity'] for alert_class in alert_classes}


@description('Provides access to the alerts filters')
class AlertFiltersProvider(Provider):
    @query('AlertFilter')
    @generator
    def query(self, filter=None, params=None):
        order = self.configstore.get('alert.filter.order')

        def extend(obj):
            obj['index'] = order.index(obj['id'])
            return obj

        filters = self.datastore.query('alert.filters', ('id', 'in', order), callback=extend)
        return q.query(filters, *(filter or []), **(params or {}))


@description('Provides access to the alert emitter configuration')
class AlertEmitterProvider(Provider):
    @query('AlertEmitter')
    @generator
    def query(self, filter=None, params=None):
        def collect():
            for p in list(self.dispatcher.plugins.values()):
                if p.metadata and p.metadata.get('type') == 'alert_emitter':
                    config = self.dispatcher.call_sync('alert.emitter.{0}.get_config'.format(p.metadata['name']))
                    yield {
                        'id': p.metadata['id'],
                        'name': p.metadata['name'],
                        'config': config
                    }

        return q.query(collect(), *(filter or []), **(params or {}))


@description("Creates an Alert Filter")
@accepts(h.all_of(
    h.ref('AlertFilter'),
    h.forbidden('id'),
    h.required('emitter', 'parameters')
))
class AlertFilterCreateTask(Task):
    @classmethod
    def early_describe(cls):
        return 'Creating alert filter'

    def describe(self, alertfilter):
        return TaskDescription('Creating alert filter')

    def verify(self, alertfilter):
        return ['system']

    def run(self, alertfilter):
        normalize(alertfilter, {
            'clazz': None,
            'predicates': []
        })

        order = self.configstore.get('alert.filter.order')
        index = alertfilter.pop('index', len(order))
        id = self.datastore.insert('alert.filters', alertfilter)
        order.insert(index, id)
        self.configstore.set('alert.filter.order', order)

        self.dispatcher.dispatch_event('alert.filter.changed', {
            'operation': 'create',
            'ids': [id]
        })

        self.dispatcher.dispatch_event('alert.filter.changed', {
            'operation': 'update',
            'ids': list(set(order) - {id})
        })

        return id


@description("Deletes the specified Alert Filter")
@accepts(str)
class AlertFilterDeleteTask(Task):
    @classmethod
    def early_describe(cls):
        return 'Deleting alert filter'

    def describe(self, id):
        return TaskDescription('Deleting alert filter')

    def verify(self, id):
        return ['system']

    def run(self, id):
        alertfilter = self.datastore.get_by_id('alert.filters', id)
        if not alertfilter:
            raise RpcException(errno.ENOENT, 'Alert filter doesn\'t exist')

        try:
            order = self.configstore.get('alert.filter.order')
            order.remove(id)
            self.datastore.delete('alert.filters', id)
            self.configstore.set('alert.filter.order', order)
        except DatastoreException as e:
            raise TaskException(
                errno.EBADMSG,
                'Cannot delete alert filter: {0}'.format(str(e))
            )

        self.dispatcher.dispatch_event('alert.filter.changed', {
            'operation': 'delete',
            'ids': [id]
        })

        self.dispatcher.dispatch_event('alert.filter.changed', {
            'operation': 'update',
            'ids': list(set(order) - {id})
        })


@description("Updates the specified Alert Filter")
@accepts(str, h.ref('AlertFilter'))
class AlertFilterUpdateTask(Task):
    @classmethod
    def early_describe(cls):
        return 'Updating alert filter'

    def describe(self, id, updated_fields):
        return TaskDescription('Updating alert filter')

    def verify(self, id, updated_fields):
        return ['system']

    def run(self, id, updated_fields):
        alertfilter = self.datastore.get_by_id('alert.filters', id)
        order = self.configstore.get('alert.filter.order')
        if not alertfilter:
            raise RpcException(errno.ENOENT, 'Alert filter doesn\'t exist')

        if 'id' in updated_fields and updated_fields['id'] != alertfilter['id']:
            raise TaskException(errno.EINVAL, 'Cannot change alert filter id')

        try:
            if 'index' in updated_fields:
                index = updated_fields.pop('index')
                order.remove(id)
                order.insert(index, id)
                self.configstore.set('alert.filter.order', order)

            alertfilter.update(updated_fields)
            self.datastore.update('alert.filters', id, alertfilter)
        except DatastoreException as e:
            raise TaskException(
                errno.EBADMSG,
                'Cannot update alert filter: {0}'.format(str(e))
            )

        self.dispatcher.dispatch_event('alert.filter.changed', {
            'operation': 'update',
            'ids': order,
        })


@accepts(str, h.ref('AlertEmitter'))
@description('Configures global parameters of an alert emitter')
class AlertEmitterUpdateTask(Task):
    @classmethod
    def early_describe(cls):
        return 'Updating alert emitter configuration'

    def describe(self, id, updated_params):
        return

    def verify(self, id, updated_params):
        return ['system']

    def run(self, id, updated_params):
        emitter = self.dispatcher.call_sync('alert.emitter.query', [('id', '=', id)], {'single': True})
        if not emitter:
            raise TaskException(errno.ENOENT, 'Emitter not found')

        if 'config' in updated_params:
            self.run_subtask_sync('alert.emitter.{0}.update'.format(emitter['name']), updated_params['config'])

        self.dispatcher.emit_event('alert.emitter.changed', {
            'operation': 'update',
            'ids': [emitter['id']]
        })


@accepts(str, h.ref('AlertSeverity'))
@description('Sends user alerts')
class SendAlertTask(Task):
    @classmethod
    def early_describe(cls):
        return 'Sending user alert'

    def describe(self, message, priority=None):
        return TaskDescription('Sending user alert')

    def verify(self, message, priority=None):
        return []

    def run(self, message, priority=None):
        if not priority:
            priority = 'WARNING'

        return self.dispatcher.call_sync('alert.emit', {
            'clazz': 'UserMessage',
            'severity': priority,
            'title': 'Message from user {0}'.format(self.user),
            'description': message,
            'one_shot': True
        })


def collect_debug(dispatcher):
    yield AttachRPC('alert-filter-query', 'alert.filter.query')
    yield AttachRPC('alert-emitter-query', 'alert.emitter.query')


def _init(dispatcher, plugin):
    # Register providers
    plugin.register_provider('alert', AlertsProvider)
    plugin.register_provider('alert.filter', AlertFiltersProvider)
    plugin.register_provider('alert.emitter', AlertEmitterProvider)

    # Register task handlers
    plugin.register_task_handler('alert.send', SendAlertTask)
    plugin.register_task_handler('alert.filter.create', AlertFilterCreateTask)
    plugin.register_task_handler('alert.filter.delete', AlertFilterDeleteTask)
    plugin.register_task_handler('alert.filter.update', AlertFilterUpdateTask)
    plugin.register_task_handler('alert.emitter.update', AlertEmitterUpdateTask)

    def on_alertd_started(args):
        if args['service-name'] != 'alertd.alert':
            return

        while pending_alerts:
            id = pending_alerts[-1]
            try:
                dispatcher.call_sync('alertd.alert.emit', id)
            except RpcException:
                logger.warning('Failed to emit alert {0}'.format(id))
            else:
                pending_alerts.pop()

        while pending_cancels:
            id = pending_cancels[-1]
            try:
                dispatcher.call_sync('alertd.alert.cancel', id)
            except RpcException:
                logger.warning('Failed to cancel alert {0}'.format(id))
            else:
                pending_cancels.pop()

    plugin.register_event_handler('plugin.service_registered', on_alertd_started)

    # Register event types
    plugin.register_event_type('alert.changed')
    plugin.register_event_type('alert.filter.changed')
    plugin.register_event_type('alert.emitter.changed')

    plugin.register_debug_hook(collect_debug)
