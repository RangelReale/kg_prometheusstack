import unittest

from kubragen import KubraGen
from kubragen.jsonpatch import FilterJSONPatches_Apply, ObjectFilter, FilterJSONPatch
from kubragen.provider import Provider_Generic

from kg_prometheusstack import PrometheusStackBuilder, PrometheusStackOptions


class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.kg = KubraGen(provider=Provider_Generic())

    def test_empty(self):
        prometheusstack_config = PrometheusStackBuilder(kubragen=self.kg, options=PrometheusStackOptions({
            'config': {
                'prometheus': {
                    'prometheus_config': '',
                },
            },
            'kubernetes': {
                'volumes': {
                    'prometheus-data': {
                        'emptyDir': {},
                    }
                }
            }
        }))
        self.assertEqual(prometheusstack_config.object_name('prometheus-config'), 'prometheus-stack-prometheus-config')
        self.assertEqual(prometheusstack_config.object_name('prometheus-statefulset'), 'prometheus-stack-prometheus')

    def test_basedata(self):
        prometheusstack_config = PrometheusStackBuilder(kubragen=self.kg, options=PrometheusStackOptions({
            'namespace': 'myns',
            'basename': 'myprometheusstack',
            'config': {
                'prometheus': {
                    'prometheus_config': '',
                },
            },
            'kubernetes': {
                'volumes': {
                    'prometheus-data': {
                        'emptyDir': {},
                    }
                }
            }
        }))
        self.assertEqual(prometheusstack_config.object_name('prometheus-config'), 'myprometheusstack-prometheus-config')
        self.assertEqual(prometheusstack_config.object_name('prometheus-statefulset'), 'myprometheusstack-prometheus')

        FilterJSONPatches_Apply(items=prometheusstack_config.build(prometheusstack_config.BUILD_SERVICE), jsonpatches=[
            FilterJSONPatch(filters=ObjectFilter(names=[prometheusstack_config.BUILDITEM_PROMETHEUS_SERVICE]), patches=[
                {'op': 'check', 'path': '/metadata/name', 'cmp': 'equals', 'value': 'myprometheusstack-prometheus'},
                {'op': 'check', 'path': '/metadata/namespace', 'cmp': 'equals', 'value': 'myns'},
            ]),
        ])
