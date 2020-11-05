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
        * - services |rarr| prometheus |rarr| config |rarr| prometheus_config
          - prometheus.yml file
          - str, :class:`kubragen.configfile.ConfigFile`
          - :class:`kg_prometheus.PrometheusConfigFile`
        * - services |rarr| prometheus |rarr| config |rarr| service_port
          - service port
          - int
          - ```80```
        * - services |rarr| prometheus |rarr| container |rarr| init-chown-data
          - init-chown-data container image
          - str
          - ```debian:<version>```
        * - services |rarr| prometheus |rarr| container |rarr| prometheus
          - prometheus container image
          - str
          - ```prom/prometheus:<version>```
        * - services |rarr| prometheus |rarr| kubernetes |rarr| volumes |rarr| data
          - Kubernetes data volume
          - dict, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          -
        * - services |rarr| prometheus |rarr| kubernetes |rarr| resources |rarr| statefulset
          - Kubernetes StatefulSet resources
          - dict
          -
        * - services |rarr| kube-state-metrics |rarr| enabled
          - whether kube-state-metrics is deployed
          - bool
          - ```True```
        * - services |rarr| kube-state-metrics |rarr| config |rarr| node_selector
          - Kubernetes node selector
          - Mapping
          - ```{'kubernetes.io/os': 'linux'}```
        * - services |rarr| kube-state-metrics |rarr| container |rarr| kube-state-metrics
          - kube-state-metrics container image
          - str
          - ```quay.io/coreos/kube-state-metrics:<version>```
        * - services |rarr| kube-state-metrics |rarr| kubernetes |rarr| resources |rarr| deployment
          - Kubernetes Deployment resources
          - Mapping
          -
        * - services |rarr| node-exporter |rarr| enabled
          - whether node-exporter deployed
          - bool
          - ```True```
        * - services |rarr| node-exporter |rarr| container |rarr| node-exporter
          - node exporter container image
          - str
          - ```prom/node-exporter:<version>```
        * - services |rarr| node-exporter |rarr| kubernetes |rarr| resources |rarr| daemonset
          - Kubernetes DaemonSet resources
          - Mapping
          -
        * - services |rarr| grafana |rarr| enabled
          - whether grafana deployed
          - bool
          - ```True```
        * - services |rarr| grafana |rarr| config |rarr| install_plugins
          - install plugins
          - Sequence
          - ```[]```
        * - services |rarr| grafana |rarr| config |rarr| service_port
          - service port
          - int
          - 80
        * - services |rarr| grafana |rarr| container |rarr| grafana
          - grafana container image
          - str
          - ```grafana/grafana:<version>```
        * - services |rarr| grafana |rarr| kubernetes |rarr| volumes |rarr| data
          - Kubernetes data volume
          - Mapping, :class:`KData_Value`, :class:`KData_ConfigMap`, :class:`KData_Secret`
          - ```{'emptyDir': {}}```
        * - services |rarr| grafana |rarr| kubernetes |rarr| resources |rarr| deployment
          - Kubernetes Deployment resources
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
                'authorization': {
                    'serviceaccount_create': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                    'serviceaccount_use': OptionDef(allowed_types=[str]),
                    'roles_create': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                    'roles_bind': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                },
            },
            'services': {
                'prometheus': {
                    'config': {
                        'prometheus_config': OptionDef(required=True, allowed_types=[str, ConfigFile]),
                        'service_port': OptionDef(required=True, default_value=80, allowed_types=[int]),
                    },
                    'container': {
                        'init-chown-data': OptionDef(default_value=OptionDefaultValue()),
                        'prometheus': OptionDef(default_value=OptionDefaultValue()),
                    },
                    'kubernetes': {
                        'volumes': {
                            'data': OptionDef(required=True, format=OptionDefFormat.KDATA_VOLUME,
                                              allowed_types=[Mapping, *KDataHelper_Volume.allowed_kdata()]),
                        },
                        'resources': {
                            'statefulset': OptionDef(default_value=OptionDefaultValue()),
                        }
                    },
                },
                'kube-state-metrics': {
                    'enabled': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                    'config': {
                        'node_selector': OptionDef(default_value=OptionDefaultValue()),
                    },
                    'container': {
                        'kube-state-metrics': OptionDef(default_value=OptionDefaultValue()),
                    },
                    'kubernetes': {
                        'resources': {
                            'deployment': OptionDef(default_value=OptionDefaultValue()),
                        }
                    },
                },
                'node-exporter': {
                    'enabled': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                    'container': {
                        'node-exporter': OptionDef(default_value=OptionDefaultValue()),
                    },
                    'kubernetes': {
                        'resources': {
                            'daemonset': OptionDef(default_value=OptionDefaultValue()),
                        }
                    },
                },
                'grafana': {
                    'enabled': OptionDef(required=True, default_value=True, allowed_types=[bool]),
                    'config': {
                        'service_port': OptionDef(required=True, default_value=80, allowed_types=[int]),
                        'install_plugins': OptionDef(default_value=[], allowed_types=[Sequence]),
                    },
                    'container': {
                        'grafana': OptionDef(default_value=OptionDefaultValue()),
                    },
                    'kubernetes': {
                        'volumes': {
                            'data': OptionDef(required=True, format=OptionDefFormat.KDATA_VOLUME,
                                              default_value={'emptyDir': {}},
                                              allowed_types=[Mapping, *KDataHelper_Volume.allowed_kdata()]),
                        },
                        'resources': {
                            'deployment': OptionDef(default_value=OptionDefaultValue()),
                        }
                    },
                },
            },
        }
