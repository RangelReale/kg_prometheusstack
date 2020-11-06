from typing import Mapping, Sequence

from kubragen.configfile import ConfigFile
from kubragen.kdatahelper import KDataHelper_Volume
from kubragen.option import OptionDef, OptionDefFormat, OptionDefaultValue
from kubragen.options import Options


class PrometheusStackOptions(Options):
    """
    Options for the Prometheus Stack builder.

    .. list-table::
        :header-rows: 1

        * - option
          - description
          - allowed types
          - default value
        * - basename
          - object names prefix
          - str
          - ```prometheus-stack```
        * - namespace
          - namespace
          - str
          - ```monitoring```
        * - config |rarr| prometheus_annotation
          - add prometheus annotations
          - bool
          - ```False```
        * - config |rarr| prometheus_config
          - prometheus.yml file
          - str, :class:`kubragen.configfile.ConfigFile`
          - :class:`kg_prometheus.PrometheusConfigFile`
        * - config |rarr| prometheus_service_port
          - Prometheus service port
          - int
          - ```80```
        * - config |rarr| kubestatemetrics_node_selector
          - Kube State Metrics Kubernetes node selector
          - Mapping
          - ```{'kubernetes.io/os': 'linux'}```
        * - config |rarr| grafana_install_plugins
          - Grafana install plugins
          - Sequence
          - ```[]```
        * - config |rarr| grafana_service_port
          - Grafana service port
          - int
          - 80
        * - config |rarr| authorization |rarr| serviceaccount_create
          - whether to create a service account
          - bool
          - ```True```
        * - config |rarr| authorization |rarr| serviceaccount_use
          - service account to use if not creating
          - str
          -
        * - config |rarr| authorization |rarr| roles_create
          - whether create roles
          - bool
          - ```True```
        * - config |rarr| authorization |rarr| roles_bind
          - whether to bind roles to service account
          - bool
          - ```True```
        * - enable |rarr| kube-state-metrics
          - whether kube-state-metrics will be deployed
          - bool
          - ```True```
        * - enable |rarr| node-exporter
          - whether node-exporter will be deployed
          - bool
          - ```True```
        * - enable |rarr| grafana
          - whether grafana will be deployed
          - bool
          - ```True```
        * - container |rarr| prometheus-init-chown-data
          - Prometheus init-chown-data container image
          - str
          - ```debian:<version>```
        * - container |rarr| prometheus
          - Prometheus container image
          - str
          - ```prom/prometheus:<version>```
        * - container |rarr| kube-state-metrics
          - Kube-state-metrics container image
          - str
          - ```quay.io/coreos/kube-state-metrics:<version>```
        * - container |rarr| node-exporter
          - Node exporter container image
          - str
          - ```prom/node-exporter:<version>```
        * - container |rarr| grafana
          - Grafana container image
          - str
          - ```grafana/grafana:<version>```
        * - kubernetes |rarr| volumes |rarr| prometheus-data
          - Prometheus Kubernetes data volume
          - dict, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - kubernetes |rarr| volumes |rarr| grafana-data
          - Grafana Kubernetes data volume
          - Mapping, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          - ```{'emptyDir': {}}```
        * - kubernetes |rarr| resources |rarr| prometheus-statefulset
          - Prometheus Kubernetes StatefulSet resources
          - Mapping
          -
        * - kubernetes |rarr| resources |rarr| kube-state-metrics-deployment
          - Kube-state-metrics Kubernetes Deployment resources
          - Mapping
          -
        * - kubernetes |rarr| resources |rarr| node-exporterdaemonset
          - Node Exporter Kubernetes DaemonSet resources
          - Mapping
          -
        * - kubernetes |rarr| resources |rarr| grafana-deployment
          - Grafana Kubernetes Deployment resources
          - Mapping
          -
    """
    def define_options(self):
        """
        Declare the options for the Prometheus Stack builder.

        :return: The supported options
        """
        return {
            'basename': OptionDef(required=True, default_value='prometheus-stack', allowed_types=[str]),
            'namespace': OptionDef(required=True, default_value='monitoring', allowed_types=[str]),
            'config': {
                'prometheus_annotation': OptionDef(required=True, default_value=False, allowed_types=[bool]),
                'prometheus_config': OptionDef(required=True, allowed_types=[str, ConfigFile]),
                'prometheus_service_port': OptionDef(required=True, default_value=80, allowed_types=[int]),
                'kubestatemetrics_node_selector': OptionDef(default_value=OptionDefaultValue()),
                'grafana_service_port': OptionDef(required=True, default_value=80, allowed_types=[int]),
                'grafana_install_plugins': OptionDef(default_value=[], allowed_types=[Sequence]),
                'authorization': {
                    'serviceaccount_create': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                    'serviceaccount_use': OptionDef(allowed_types=[str]),
                    'roles_create': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                    'roles_bind': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                },
            },
            'enable': {
                'kube-state-metrics': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                'node-exporter': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                'grafana': OptionDef(required=True, default_value=True, allowed_types=[bool]),
            },
            'container': {
                'prometheus-init-chown-data': OptionDef(required=True, default_value='debian:9', allowed_types=[str]),
                'prometheus': OptionDef(required=True, default_value='prom/prometheus:v2.21.0', allowed_types=[str]),
                'kube-state-metrics': OptionDef(required=True,
                                                default_value='quay.io/coreos/kube-state-metrics:v2.0.0-alpha.1',
                                                allowed_types=[str]),
                'node-exporter': OptionDef(required=True, default_value='prom/node-exporter:v1.0.1',
                                           allowed_types=[str]),
                'grafana': OptionDef(required=True, default_value='grafana/grafana:7.2.0', allowed_types=[str]),
            },
            'kubernetes': {
                'volumes': {
                    'prometheus-data': OptionDef(required=True, format=OptionDefFormat.KDATA_VOLUME,
                                                 allowed_types=[Mapping, *KDataHelper_Volume.allowed_kdata()]),
                    'grafana-data': OptionDef(required=True, format=OptionDefFormat.KDATA_VOLUME,
                                              default_value={'emptyDir': {}},
                                              allowed_types=[Mapping, *KDataHelper_Volume.allowed_kdata()]),
                },
                'resources': {
                    'prometheus-statefulset': OptionDef(allowed_types=[Mapping]),
                    'kube-state-metrics-deployment': OptionDef(allowed_types=[Mapping]),
                    'node-exporter-daemonset': OptionDef(allowed_types=[Mapping]),
                    'grafana-deployment': OptionDef(allowed_types=[Mapping]),
                }
            },
        }
