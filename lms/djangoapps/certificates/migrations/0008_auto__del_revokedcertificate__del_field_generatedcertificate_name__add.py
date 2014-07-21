# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'RevokedCertificate'
        db.delete_table('certificates_revokedcertificate')

        # Deleting field 'GeneratedCertificate.name'
        db.delete_column('certificates_generatedcertificate', 'name')

        # Adding field 'GeneratedCertificate.course_id'
        db.add_column('certificates_generatedcertificate', 'course_id',
                      self.gf('django.db.models.fields.CharField')(default=False, max_length=255),
                      keep_default=False)

        # Adding field 'GeneratedCertificate.key'
        db.add_column('certificates_generatedcertificate', 'key',
                      self.gf('django.db.models.fields.CharField')(default=False, max_length=32),
                      keep_default=False)


        # Changing field 'GeneratedCertificate.grade'
        db.alter_column('certificates_generatedcertificate', 'grade', self.gf('django.db.models.fields.CharField')(max_length=5))

        # Changing field 'GeneratedCertificate.certificate_id'
        db.alter_column('certificates_generatedcertificate', 'certificate_id', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'GeneratedCertificate.download_url'
        db.alter_column('certificates_generatedcertificate', 'download_url', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'GeneratedCertificate.graded_download_url'
        db.alter_column('certificates_generatedcertificate', 'graded_download_url', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'GeneratedCertificate.graded_certificate_id'
        db.alter_column('certificates_generatedcertificate', 'graded_certificate_id', self.gf('django.db.models.fields.CharField')(max_length=32))

    def backwards(self, orm):
        # Adding model 'RevokedCertificate'
        db.create_table('certificates_revokedcertificate', (
            ('grade', self.gf('django.db.models.fields.CharField')(max_length=5, null=True)),
            ('certificate_id', self.gf('django.db.models.fields.CharField')(default=None, max_length=32, null=True)),
            ('explanation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('graded_download_url', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('download_url', self.gf('django.db.models.fields.CharField')(max_length=128, null=True)),
            ('graded_certificate_id', self.gf('django.db.models.fields.CharField')(default=None, max_length=32, null=True)),
        ))
        db.send_create_signal('certificates', ['RevokedCertificate'])

        # Adding field 'GeneratedCertificate.name'
        db.add_column('certificates_generatedcertificate', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Deleting field 'GeneratedCertificate.course_id'
        db.delete_column('certificates_generatedcertificate', 'course_id')

        # Deleting field 'GeneratedCertificate.key'
        db.delete_column('certificates_generatedcertificate', 'key')


        # Changing field 'GeneratedCertificate.grade'
        db.alter_column('certificates_generatedcertificate', 'grade', self.gf('django.db.models.fields.CharField')(max_length=5, null=True))

        # Changing field 'GeneratedCertificate.certificate_id'
        db.alter_column('certificates_generatedcertificate', 'certificate_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True))

        # Changing field 'GeneratedCertificate.download_url'
        db.alter_column('certificates_generatedcertificate', 'download_url', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'GeneratedCertificate.graded_download_url'
        db.alter_column('certificates_generatedcertificate', 'graded_download_url', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'GeneratedCertificate.graded_certificate_id'
        db.alter_column('certificates_generatedcertificate', 'graded_certificate_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'about': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'avatar_type': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'bronze': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'consecutive_days_visit_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'display_tag_filter_strategy': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_isvalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_key': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'email_tag_filter_strategy': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gold': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'gravatar': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignored_tags': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'interesting_tags': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'new_response_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'questions_per_page': ('django.db.models.fields.SmallIntegerField', [], {'default': '10'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'reputation': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'seen_response_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_country': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'silver': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'w'", 'max_length': '2'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'certificates.generatedcertificate': {
            'Meta': {'object_name': 'GeneratedCertificate'},
            'certificate_id': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '32'}),
            'course_id': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '255'}),
            'download_url': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '128'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'grade': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '5'}),
            'graded_certificate_id': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '32'}),
            'graded_download_url': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['certificates']
