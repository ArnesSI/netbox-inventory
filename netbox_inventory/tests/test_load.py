import os
from django.apps import apps
from django.test import TestCase, override_settings


class PluginLoadTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        override_settings(PLUGINS=['netbox_inventory',])

    def test_version_match(self):
        """ Make sure version of plugin matches string in setup.py """
        plugin = apps.get_app_config('netbox_inventory')
        import netbox_inventory
        setup_path = os.path.join(os.path.dirname(os.path.dirname(netbox_inventory.__file__)), 'setup.py')
        setup_lines = open(setup_path).readlines()
        version_lines = list(filter(lambda l: 'version=' in l, setup_lines))
        self.assertGreater(len(version_lines), 0)
        self.assertTrue(all([lambda l: plugin.version in l for l in version_lines]))
