# -*- coding: utf-8 -*-
import os
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'idmap_rfc2307'
        db.create_table(u'directoryservice_idmap_rfc2307', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_rfc2307_range_low', self.gf('django.db.models.fields.IntegerField')(default=10000)),
            ('idmap_rfc2307_range_high', self.gf('django.db.models.fields.IntegerField')(default=90000000)),
            ('idmap_rfc2307_ldap_server', self.gf('django.db.models.fields.CharField')(default='ad', max_length=120)),
            ('idmap_rfc2307_bind_path_user', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('idmap_rfc2307_bind_path_group', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('idmap_rfc2307_user_cn', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('idmap_rfc2307_cn_realm', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('idmap_rfc2307_ldap_domain', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('idmap_rfc2307_ldap_url', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('idmap_rfc2307_ldap_user_dn', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('idmap_rfc2307_ldap_realm', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_rfc2307'])

        # Adding model 'idmap_ldap'
        db.create_table(u'directoryservice_idmap_ldap', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_ldap_range_low', self.gf('django.db.models.fields.IntegerField')(default=10000)),
            ('idmap_ldap_range_high', self.gf('django.db.models.fields.IntegerField')(default=90000000)),
            ('idmap_ldap_ldap_base_dn', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('idmap_ldap_ldap_user_dn', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('idmap_ldap_ldap_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_ldap'])

        # Adding model 'idmap_nss'
        db.create_table(u'directoryservice_idmap_nss', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_nss_range_low', self.gf('django.db.models.fields.IntegerField')(default=10000)),
            ('idmap_nss_range_high', self.gf('django.db.models.fields.IntegerField')(default=90000000)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_nss'])

        # Adding model 'idmap_tdb2'
        db.create_table(u'directoryservice_idmap_tdb2', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_tdb2_range_low', self.gf('django.db.models.fields.IntegerField')(default=90000001)),
            ('idmap_tdb2_range_high', self.gf('django.db.models.fields.IntegerField')(default=100000000)),
            ('idmap_tdb2_script', self.gf('freenasUI.freeadmin.models.fields.PathField')(max_length=255)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_tdb2'])

        # Adding model 'idmap_ad'
        db.create_table(u'directoryservice_idmap_ad', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_ad_range_low', self.gf('django.db.models.fields.IntegerField')(default=10000)),
            ('idmap_ad_range_high', self.gf('django.db.models.fields.IntegerField')(default=90000000)),
            ('idmap_ad_schema_mode', self.gf('django.db.models.fields.CharField')(default='rfc2307', max_length=120)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_ad'])

        if 'FREENAS_INSTALL' in os.environ:
            idmap_rid_range_low = 20000
        else:
            idmap_rid_range_low = 10000

        # Adding model 'idmap_rid'
        db.create_table(u'directoryservice_idmap_rid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_rid_range_low', self.gf('django.db.models.fields.IntegerField')(default=idmap_rid_range_low)),
            ('idmap_rid_range_high', self.gf('django.db.models.fields.IntegerField')(default=90000000)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_rid'])

        # Adding model 'idmap_hash'
        db.create_table(u'directoryservice_idmap_hash', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_hash_range_low', self.gf('django.db.models.fields.IntegerField')(default=90000001)),
            ('idmap_hash_range_high', self.gf('django.db.models.fields.IntegerField')(default=100000000)),
            ('idmap_hash_range_name_map', self.gf('freenasUI.freeadmin.models.fields.PathField')(max_length=255)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_hash'])

        # Adding model 'idmap_tdb'
        db.create_table(u'directoryservice_idmap_tdb', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_tdb_range_low', self.gf('django.db.models.fields.IntegerField')(default=90000001)),
            ('idmap_tdb_range_high', self.gf('django.db.models.fields.IntegerField')(default=100000000)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_tdb'])

        # Adding model 'idmap_autorid'
        db.create_table(u'directoryservice_idmap_autorid', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('idmap_autorid_range_low', self.gf('django.db.models.fields.IntegerField')(default=10000)),
            ('idmap_autorid_range_high', self.gf('django.db.models.fields.IntegerField')(default=90000000)),
            ('idmap_autorid_rangesize', self.gf('django.db.models.fields.IntegerField')(default=100000)),
            ('idmap_autorid_readonly', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('idmap_autorid_ignore_builtin', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'directoryservice', ['idmap_autorid'])

        # Adding model 'directoryservice_idmap'
        db.create_table(u'directoryservice_directoryservice_idmap', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dsi_idmap_ad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_ad'], null=True)),
            ('dsi_idmap_autorid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_autorid'], null=True)),
            ('dsi_idmap_hash', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_hash'], null=True)),
            ('dsi_idmap_ldap', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_ldap'], null=True)),
            ('dsi_idmap_nss', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_nss'], null=True)),
            ('dsi_idmap_rfc2307', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_rfc2307'], null=True)),
            ('dsi_idmap_rid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_rid'], null=True)),
            ('dsi_idmap_tdb', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_tdb'], null=True)),
            ('dsi_idmap_tdb2', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.idmap_tdb2'], null=True)),
        ))
        db.send_create_signal(u'directoryservice', ['directoryservice_idmap'])

        # Adding field 'NT4.nt4_idmap_backend'
        db.add_column(u'directoryservice_nt4', 'nt4_idmap_backend',
                      self.gf('django.db.models.fields.CharField')(default='idmap_rid', max_length=120),
                      keep_default=False)

        # Adding field 'NT4.nt4_idmap_backend_type'
        db.add_column(u'directoryservice_nt4', 'nt4_idmap_backend_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.directoryservice_idmap'], null=True),
                      keep_default=False)

        # Adding field 'ActiveDirectory.ad_idmap_backend'
        db.add_column(u'directoryservice_activedirectory', 'ad_idmap_backend',
                      self.gf('django.db.models.fields.CharField')(default='idmap_ad', max_length=120),
                      keep_default=False)

        # Adding field 'ActiveDirectory.ad_idmap_backend_type'
        db.add_column(u'directoryservice_activedirectory', 'ad_idmap_backend_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.directoryservice_idmap'], null=True),
                      keep_default=False)

        # Adding field 'LDAP.ldap_idmap_backend'
        db.add_column(u'directoryservice_ldap', 'ldap_idmap_backend',
                      self.gf('django.db.models.fields.CharField')(default='idmap_ldap', max_length=120),
                      keep_default=False)

        # Adding field 'LDAP.ldap_idmap_backend_type'
        db.add_column(u'directoryservice_ldap', 'ldap_idmap_backend_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directoryservice.directoryservice_idmap'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'idmap_rfc2307'
        db.delete_table(u'directoryservice_idmap_rfc2307')

        # Deleting model 'idmap_ldap'
        db.delete_table(u'directoryservice_idmap_ldap')

        # Deleting model 'idmap_nss'
        db.delete_table(u'directoryservice_idmap_nss')

        # Deleting model 'idmap_tdb2'
        db.delete_table(u'directoryservice_idmap_tdb2')

        # Deleting model 'idmap_ad'
        db.delete_table(u'directoryservice_idmap_ad')

        # Deleting model 'idmap_rid'
        db.delete_table(u'directoryservice_idmap_rid')

        # Deleting model 'idmap_hash'
        db.delete_table(u'directoryservice_idmap_hash')

        # Deleting model 'idmap_tdb'
        db.delete_table(u'directoryservice_idmap_tdb')

        # Deleting model 'idmap_autorid'
        db.delete_table(u'directoryservice_idmap_autorid')

        # Deleting model 'directoryservice_idmap'
        db.delete_table(u'directoryservice_directoryservice_idmap')

        # Deleting field 'NT4.nt4_idmap_backend'
        db.delete_column(u'directoryservice_nt4', 'nt4_idmap_backend')

        # Deleting field 'NT4.nt4_idmap_backend_type'
        db.delete_column(u'directoryservice_nt4', 'nt4_idmap_backend_type_id')

        # Deleting field 'ActiveDirectory.ad_idmap_backend'
        db.delete_column(u'directoryservice_activedirectory', 'ad_idmap_backend')

        # Deleting field 'ActiveDirectory.ad_idmap_backend_type'
        db.delete_column(u'directoryservice_activedirectory', 'ad_idmap_backend_type_id')

        # Deleting field 'LDAP.ldap_idmap_backend'
        db.delete_column(u'directoryservice_ldap', 'ldap_idmap_backend')

        # Deleting field 'LDAP.ldap_idmap_backend_type'
        db.delete_column(u'directoryservice_ldap', 'ldap_idmap_backend_type_id')


    models = {
        u'directoryservice.activedirectory': {
            'Meta': {'object_name': 'ActiveDirectory'},
            'ad_allow_trusted_doms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ad_bindname': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'ad_bindpw': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'ad_certfile': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ad_dcname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ad_dns_timeout': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'ad_domainname': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'ad_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ad_gcname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ad_idmap_backend': ('django.db.models.fields.CharField', [], {'default': "'idmap_ad'", 'max_length': '120'}),
            'ad_idmap_backend_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.directoryservice_idmap']", 'null': 'True'}),
            'ad_keytab': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ad_kpwdname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ad_krbname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ad_netbiosname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ad_ssl': ('django.db.models.fields.CharField', [], {'default': "'off'", 'max_length': '120'}),
            'ad_timeout': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'ad_unix_extensions': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ad_use_default_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ad_use_keytab': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ad_verbose_logging': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'directoryservice.directoryservice_idmap': {
            'Meta': {'object_name': 'directoryservice_idmap'},
            'dsi_idmap_ad': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_ad']", 'null': 'True'}),
            'dsi_idmap_autorid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_autorid']", 'null': 'True'}),
            'dsi_idmap_hash': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_hash']", 'null': 'True'}),
            'dsi_idmap_ldap': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_ldap']", 'null': 'True'}),
            'dsi_idmap_nss': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_nss']", 'null': 'True'}),
            'dsi_idmap_rfc2307': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_rfc2307']", 'null': 'True'}),
            'dsi_idmap_rid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_rid']", 'null': 'True'}),
            'dsi_idmap_tdb': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_tdb']", 'null': 'True'}),
            'dsi_idmap_tdb2': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.idmap_tdb2']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'directoryservice.idmap_ad': {
            'Meta': {'object_name': 'idmap_ad'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_ad_range_high': ('django.db.models.fields.IntegerField', [], {'default': '90000000'}),
            'idmap_ad_range_low': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'idmap_ad_schema_mode': ('django.db.models.fields.CharField', [], {'default': "'rfc2307'", 'max_length': '120'})
        },
        u'directoryservice.idmap_autorid': {
            'Meta': {'object_name': 'idmap_autorid'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_autorid_ignore_builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'idmap_autorid_range_high': ('django.db.models.fields.IntegerField', [], {'default': '90000000'}),
            'idmap_autorid_range_low': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'idmap_autorid_rangesize': ('django.db.models.fields.IntegerField', [], {'default': '100000'}),
            'idmap_autorid_readonly': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'directoryservice.idmap_hash': {
            'Meta': {'object_name': 'idmap_hash'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_hash_range_high': ('django.db.models.fields.IntegerField', [], {'default': '100000000'}),
            'idmap_hash_range_low': ('django.db.models.fields.IntegerField', [], {'default': '90000001'}),
            'idmap_hash_range_name_map': ('freenasUI.freeadmin.models.fields.PathField', [], {'max_length': '255'})
        },
        u'directoryservice.idmap_ldap': {
            'Meta': {'object_name': 'idmap_ldap'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_ldap_ldap_base_dn': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'idmap_ldap_ldap_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'idmap_ldap_ldap_user_dn': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'idmap_ldap_range_high': ('django.db.models.fields.IntegerField', [], {'default': '90000000'}),
            'idmap_ldap_range_low': ('django.db.models.fields.IntegerField', [], {'default': '10000'})
        },
        u'directoryservice.idmap_nss': {
            'Meta': {'object_name': 'idmap_nss'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_nss_range_high': ('django.db.models.fields.IntegerField', [], {'default': '90000000'}),
            'idmap_nss_range_low': ('django.db.models.fields.IntegerField', [], {'default': '10000'})
        },
        u'directoryservice.idmap_rfc2307': {
            'Meta': {'object_name': 'idmap_rfc2307'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_rfc2307_bind_path_group': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'idmap_rfc2307_bind_path_user': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'idmap_rfc2307_cn_realm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'idmap_rfc2307_ldap_domain': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'idmap_rfc2307_ldap_realm': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'idmap_rfc2307_ldap_server': ('django.db.models.fields.CharField', [], {'default': "'ad'", 'max_length': '120'}),
            'idmap_rfc2307_ldap_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'idmap_rfc2307_ldap_user_dn': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'idmap_rfc2307_range_high': ('django.db.models.fields.IntegerField', [], {'default': '90000000'}),
            'idmap_rfc2307_range_low': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'idmap_rfc2307_user_cn': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'directoryservice.idmap_rid': {
            'Meta': {'object_name': 'idmap_rid'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_rid_range_high': ('django.db.models.fields.IntegerField', [], {'default': '90000000'}),
            'idmap_rid_range_low': ('django.db.models.fields.IntegerField', [], {'default': '10000'})
        },
        u'directoryservice.idmap_tdb': {
            'Meta': {'object_name': 'idmap_tdb'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_tdb_range_high': ('django.db.models.fields.IntegerField', [], {'default': '100000000'}),
            'idmap_tdb_range_low': ('django.db.models.fields.IntegerField', [], {'default': '90000001'})
        },
        u'directoryservice.idmap_tdb2': {
            'Meta': {'object_name': 'idmap_tdb2'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idmap_tdb2_range_high': ('django.db.models.fields.IntegerField', [], {'default': '100000000'}),
            'idmap_tdb2_range_low': ('django.db.models.fields.IntegerField', [], {'default': '90000001'}),
            'idmap_tdb2_script': ('freenasUI.freeadmin.models.fields.PathField', [], {'max_length': '255'})
        },
        u'directoryservice.ldap': {
            'Meta': {'object_name': 'LDAP'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ldap_anonbind': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ldap_basedn': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ldap_binddn': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ldap_bindpw': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ldap_certfile': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'ldap_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ldap_groupsuffix': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ldap_hostname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ldap_idmap_backend': ('django.db.models.fields.CharField', [], {'default': "'idmap_ldap'", 'max_length': '120'}),
            'ldap_idmap_backend_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.directoryservice_idmap']", 'null': 'True'}),
            'ldap_machinesuffix': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ldap_passwordsuffix': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ldap_ssl': ('django.db.models.fields.CharField', [], {'default': "'off'", 'max_length': '120'}),
            'ldap_use_default_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ldap_usersuffix': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'})
        },
        u'directoryservice.nis': {
            'Meta': {'object_name': 'NIS'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nis_domain': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'nis_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nis_manycast': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nis_secure_mode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nis_servers': ('django.db.models.fields.CharField', [], {'max_length': '8192', 'blank': 'True'})
        },
        u'directoryservice.nt4': {
            'Meta': {'object_name': 'NT4'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nt4_adminname': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'nt4_adminpw': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'nt4_dcname': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'nt4_enable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nt4_idmap_backend': ('django.db.models.fields.CharField', [], {'default': "'idmap_rid'", 'max_length': '120'}),
            'nt4_idmap_backend_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directoryservice.directoryservice_idmap']", 'null': 'True'}),
            'nt4_netbiosname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'nt4_use_default_domain': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nt4_workgroup': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        }
    }

    complete_apps = ['directoryservice']
