import copy
from typing import List, Optional, Sequence, Mapping

from kg_grafana import GrafanaBuilder, GrafanaOptions
from kg_kubestatemetrics import KubeStateMetricsBuilder, KubeStateMetricsOptions
from kg_nodeexporter import NodeExporterBuilder, NodeExporterOptions
from kg_prometheus import PrometheusBuilder, PrometheusOptions
from kubragen import KubraGen
from kubragen.builder import Builder
from kubragen.exception import InvalidNameError, OptionError
from kubragen.object import ObjectItem, Object
from kubragen.types import TBuild, TBuildItem

from .option import PrometheusStackOptions


class PrometheusStackBuilder(Builder):
    """
    Prometheus Stack builder.

    .. list-table::
        :header-rows: 1

        * - build
          - description
        * - BUILD_ACCESSCONTROL
          - creates service account, roles, and roles bindings
        * - BUILD_CONFIG
          - creates ConfigMap
        * - BUILD_SERVICE
          - creates deployments and services

    .. list-table::
        :header-rows: 1

        * - build item
          - description
        * - BUILDITEM_SERVICE_ACCOUNT
          - ServiceAccount
        * - BUILDITEM_PROMETHEUS_CONFIG
          - Prometheus ConfigMap
        * - BUILDITEM_PROMETHEUS_CLUSTER_ROLE
          - Prometheus ClusterRole
        * - BUILDITEM_PROMETHEUS_CLUSTER_ROLE_BINDING
          - Prometheus ClusterRoleBinding
        * - BUILDITEM_PROMETHEUS_STATEFULSET
          - Prometheus StatefulSet
        * - BUILDITEM_PROMETHEUS_SERVICE
          - Prometheus Service
        * - BUILDITEM_KUBESTATEMETRICS_CLUSTER_ROLE
          - Kube State Metrics ClusterRole
        * - BUILDITEM_KUBESTATEMETRICS_CLUSTER_ROLE_BINDING
          - Kube State Metrics ClusterRoleBinding
        * - BUILDITEM_KUBESTATEMETRICS_DEPLOYMENT
          - Kube State Metrics Deployment
        * - BUILDITEM_KUBESTATEMETRICS_SERVICE
          - Kube State Metrics Service
        * - BUILDITEM_GRAFANA_DEPLOYMENT
          - Grafana Deployment
        * - BUILDITEM_GRAFANA_SERVICE
          - Grafana Service
        * - BUILDITEM_NODEEXPORTER_DAEMONSET
          - Node Exporeter DaemonSet

    .. list-table::
        :header-rows: 1

        * - object name
          - description
          - default value
        * - service-account
          - ServiceAccount
          - ```<basename>```
        * - prometheus-config
          - Prometheus ConfigMap
          - ```<basename>-prometheus-config```
        * - prometheus-service
          - Prometheus Service
          - ```<basename>-prometheus```
        * - prometheus-cluster-role
          - Prometheus ClusterRole
          - ```<basename>-prometheus```
        * - prometheus-cluster-role-binding
          - Prometheus ClusterRoleBinding
          - ```<basename>-prometheus```
        * - prometheus-statefulset
          - Prometheus StatefulSet
          - ```<basename>-prometheus```
        * - kube-state-metrics-service
          - Kube State Metrics Service
          - ```<basename>-kube-state-metrics```
        * - kube-state-metrics-cluster-role
          - Kube State Metrics ClusterRole
          - ```<basename>-kube-state-metrics```
        * - kube-state-metrics-cluster-role-binding
          - Kube State Metrics ClusterRoleBinding
          - ```<basename>-kube-state-metrics```
        * - kube-state-metrics-deployment
          - Kube State Metrics Deployment
          - ```<basename>-kube-state-metrics```
        * - node-exporter-daemonset
          - Node Exporter DaemonSet
          - ```<basename>-node-exporter```
        * - grafana-service
          - Grafana Service
          - ```<basename>-grafana```
        * - grafana-deployment
          - Grafana Deployment
          - ```<basename>-grafana```
    """
    options: PrometheusStackOptions
    _namespace: str
    _default_object_names: Mapping[str, str]

    SOURCE_NAME = 'kg_prometheusstack'

    BUILD_ACCESSCONTROL: TBuild = 'accesscontrol'
    BUILD_CONFIG: TBuild = 'config'
    BUILD_SERVICE: TBuild = 'service'

    BUILDITEM_SERVICE_ACCOUNT: TBuildItem = 'service-account'
    BUILDITEM_PROMETHEUS_CONFIG: TBuildItem = 'prometheus-config'
    BUILDITEM_PROMETHEUS_CLUSTER_ROLE: TBuildItem = 'prometheus-cluster-role'
    BUILDITEM_PROMETHEUS_CLUSTER_ROLE_BINDING: TBuildItem = 'prometheus-cluster-role-binding'
    BUILDITEM_PROMETHEUS_STATEFULSET: TBuildItem = 'prometheus-statefulset'
    BUILDITEM_PROMETHEUS_SERVICE: TBuildItem = 'prometheus-service'
    BUILDITEM_KUBESTATEMETRICS_CLUSTER_ROLE: TBuildItem = 'kubestatemetrics-cluster-role'
    BUILDITEM_KUBESTATEMETRICS_CLUSTER_ROLE_BINDING: TBuildItem = 'kubestatemetrics-cluster-role-binding'
    BUILDITEM_KUBESTATEMETRICS_DEPLOYMENT: TBuildItem = 'kube-state-metrics-deployment'
    BUILDITEM_KUBESTATEMETRICS_SERVICE: TBuildItem = 'kube-state-metrics-service'
    BUILDITEM_GRAFANA_DEPLOYMENT: TBuildItem = 'grafana-deployment'
    BUILDITEM_GRAFANA_SERVICE: TBuildItem = 'grafana-service'
    BUILDITEM_NODEEXPORTER_DAEMONSET: TBuildItem = 'node-exporter-daemonset'

    def __init__(self, kubragen: KubraGen, options: Optional[PrometheusStackOptions] = None):
        super().__init__(kubragen)
        if options is None:
            options = PrometheusStackOptions()
        self.options = options
        self._default_object_names = {}

        self._namespace = self.option_get('namespace')

        if self.option_get('config.authorization.serviceaccount_create') is not False:
            serviceaccount_name = self.basename()
        else:
            serviceaccount_name = self.option_get('config.authorization.serviceaccount_use')
            if serviceaccount_name == '':
                serviceaccount_name = None

        self.object_names_init({
            'service-account': serviceaccount_name,
        })

        prometheus_config = self._create_prometheus_config()
        prometheus_config.ensure_build_names(prometheus_config.BUILD_ACCESSCONTROL, prometheus_config.BUILD_CONFIG,
                                             prometheus_config.BUILD_SERVICE)

        self.object_names_init({
            'prometheus-config': prometheus_config.object_name('config'),
            'prometheus-cluster-role': prometheus_config.object_name('cluster-role'),
            'prometheus-cluster-role-binding': prometheus_config.object_name('cluster-role-binding'),
            'prometheus-statefulset': prometheus_config.object_name('statefulset'),
            'prometheus-service': prometheus_config.object_name('service'),
        })

        if self.option_get('enable.kube-state-metrics') is not False:
            kubestatemetrics_config = self._create_kubestatemetrics_config()
            kubestatemetrics_config.ensure_build_names(kubestatemetrics_config.BUILD_ACCESSCONTROL,
                                                       kubestatemetrics_config.BUILD_SERVICE)
            self.object_names_init({
                'kube-state-metrics-cluster-role': kubestatemetrics_config.object_name('cluster-role'),
                'kube-state-metrics-role-binding': kubestatemetrics_config.object_name('cluster-role-binding'),
                'kube-state-metrics-deployment': kubestatemetrics_config.object_name('deployment'),
                'kube-state-metrics-service': kubestatemetrics_config.object_name('service'),
            })

        if self.option_get('enable.node-exporter') is not False:
            nodeexporter_config = self._create_nodeexporter_config()
            nodeexporter_config.ensure_build_names(nodeexporter_config.BUILD_SERVICE)

            self.object_names_init({
                'node-exporter-daemonset': nodeexporter_config.object_name('daemonset'),
            })

        if self.option_get('enable.grafana') is not False:
            granana_config = self._create_granana_config()
            granana_config.ensure_build_names(granana_config.BUILD_SERVICE)

            self.object_names_init({
                'grafana-deployment': granana_config.object_name('deployment'),
                'grafana-service': granana_config.object_name('service'),
            })

        self._default_object_names = copy.deepcopy(self.object_names())

    def option_get(self, name: str):
        return self.kubragen.option_root_get(self.options, name)

    def basename(self, suffix: str = ''):
        return '{}{}'.format(self.option_get('basename'), suffix)

    def namespace(self):
        return self._namespace

    def build_names(self) -> List[TBuild]:
        return [self.BUILD_ACCESSCONTROL, self.BUILD_CONFIG, self.BUILD_SERVICE]

    def build_names_required(self) -> List[TBuild]:
        ret = [self.BUILD_CONFIG, self.BUILD_SERVICE]
        if self.option_get('config.authorization.serviceaccount_create') is not False or \
                self.option_get('config.authorization.roles_create') is not False:
            ret.append(self.BUILD_ACCESSCONTROL)
        return ret

    def builditem_names(self) -> List[TBuildItem]:
        return [
            self.BUILDITEM_SERVICE_ACCOUNT,
            self.BUILDITEM_CONFIG,
            self.BUILDITEM_PROMETHEUS_CLUSTER_ROLE,
            self.BUILDITEM_PROMETHEUS_CLUSTER_ROLE_BINDING,
            self.BUILDITEM_PROMETHEUS_STATEFULSET,
            self.BUILDITEM_PROMETHEUS_SERVICE,
            self.BUILDITEM_KUBESTATEMETRICS_CLUSTER_ROLE,
            self.BUILDITEM_KUBESTATEMETRICS_CLUSTER_ROLE_BINDING,
            self.BUILDITEM_KUBESTATEMETRICS_DEPLOYMENT,
            self.BUILDITEM_KUBESTATEMETRICS_SERVICE,
            self.BUILDITEM_GRAFANA_DEPLOYMENT,
            self.BUILDITEM_GRAFANA_SERVICE,
            self.BUILDITEM_NODEEXPORTER_DAEMONSET,
        ]

    def internal_build(self, buildname: TBuild) -> Sequence[ObjectItem]:
        if buildname == self.BUILD_ACCESSCONTROL:
            return self.internal_build_accesscontrol()
        elif buildname == self.BUILD_CONFIG:
            return self.internal_build_config()
        elif buildname == self.BUILD_SERVICE:
            return self.internal_build_service()
        else:
            raise InvalidNameError('Invalid build name: "{}"'.format(buildname))

    def internal_build_accesscontrol(self) -> Sequence[ObjectItem]:
        ret = []

        if self.option_get('config.authorization.serviceaccount_create') is not False:
            ret.extend([
                Object({
                    'apiVersion': 'v1',
                    'kind': 'ServiceAccount',
                    'metadata': {
                        'name': self.object_name('service-account'),
                        'namespace': self.namespace(),
                    }
                }, name=self.BUILDITEM_SERVICE_ACCOUNT, source=self.SOURCE_NAME, instance=self.basename()),
            ])

        ret.extend(self._build_result_change(
            self._create_prometheus_config().build(PrometheusBuilder.BUILD_ACCESSCONTROL), 'prometheus'))

        if self.option_get('enable.kube-state-metrics') is not False:
            ret.extend(self._build_result_change(
                self._create_kubestatemetrics_config().build(KubeStateMetricsBuilder.BUILD_ACCESSCONTROL), 'kube-state-metrics'))

        return ret

    def internal_build_config(self) -> Sequence[ObjectItem]:
        ret = []

        ret.extend(self._build_result_change(
            self._create_prometheus_config().build(PrometheusBuilder.BUILD_CONFIG), 'prometheus'))

        return ret

    def internal_build_service(self) -> Sequence[ObjectItem]:
        ret = []

        ret.extend(self._build_result_change(
            self._create_prometheus_config().build(PrometheusBuilder.BUILD_SERVICE), 'prometheus'))
        if self.option_get('enable.kube-state-metrics') is not False:
            ret.extend(self._build_result_change(
                self._create_kubestatemetrics_config().build(KubeStateMetricsBuilder.BUILD_SERVICE), 'kube-state-metrics'))
        if self.option_get('enable.node-exporter') is not False:
            ret.extend(self._build_result_change(
                self._create_nodeexporter_config().build(NodeExporterBuilder.BUILD_SERVICE), 'node-exporter'))
        if self.option_get('enable.grafana') is not False:
            ret.extend(self._build_result_change(
                self._create_granana_config().build(GrafanaBuilder.BUILD_SERVICE), 'grafana'))

        return ret

    def _build_result_change(self, items: Sequence[ObjectItem], name_prefix: str) -> Sequence[ObjectItem]:
        for o in items:
            if isinstance(o, Object):
                o.name = '{}-{}'.format(name_prefix, o.name)
                o.source = self.SOURCE_NAME
                o.instance = self.basename()
        return items

    def _object_names_changed(self, prefix: str) -> Mapping[str, str]:
        ret = {}
        for dname, dvalue in self.object_names().items():
            if dname.startswith(prefix) and dname in self._default_object_names:
                if self._default_object_names[dname] != dvalue:
                    ret[dname[len(prefix):]] = dvalue
        return ret

    def _create_prometheus_config(self) -> PrometheusBuilder:
        try:
            ret = PrometheusBuilder(kubragen=self.kubragen, options=PrometheusOptions({
                    'basename': self.basename('-prometheus'),
                    'namespace': self.namespace(),
                    'config': {
                        'prometheus_config': self.option_get('config.prometheus_config'),
                        'service_port': self.option_get('config.prometheus_service_port'),
                        'authorization': {
                            'serviceaccount_create': False,
                            'serviceaccount_use': self.object_name('service-account'),
                            'roles_create': self.option_get('config.authorization.roles_create'),
                            'roles_bind': self.option_get('config.authorization.roles_bind'),
                        },
                    },
                    'container': {
                        'init-chown-data': self.option_get('container.prometheus-init-chown-data'),
                        'prometheus': self.option_get('container.prometheus'),
                    },
                    'kubernetes': {
                        'volumes': {
                            'data': self.option_get('kubernetes.volumes.prometheus-data'),
                        },
                        'resources': {
                            'statefulset': self.option_get('kubernetes.resources.prometheus-statefulset'),
                        },
                    },
                }))
            ret.object_names_change(self._object_names_changed('prometheus-'))
            return ret
        except OptionError as e:
            raise OptionError('Prometheus option error: {}'.format(str(e))) from e
        except TypeError as e:
            raise OptionError('Prometheus type error: {}'.format(str(e))) from e

    def _create_kubestatemetrics_config(self) -> Optional[KubeStateMetricsBuilder]:
        if self.option_get('enable.kube-state-metrics') is not False:
            try:
                ret = KubeStateMetricsBuilder(kubragen=self.kubragen, options=KubeStateMetricsOptions({
                        'basename': self.basename('-kube-state-metrics'),
                        'namespace': self.namespace(),
                        'config': {
                            'prometheus_annotation': self.option_get('config.prometheus_annotation'),
                            'node_selector': self.option_get('config.kubestatemetrics_node_selector'),
                            'authorization': {
                                'serviceaccount_create': False,
                                'serviceaccount_use': self.object_name('service-account'),
                                'roles_create': self.option_get('config.authorization.roles_create'),
                                'roles_bind': self.option_get('config.authorization.roles_bind'),
                            },
                        },
                        'container': {
                            'kube-state-metrics': self.option_get('container.kube-state-metrics'),
                        },
                        'kubernetes': {
                            'resources': {
                                'deployment': self.option_get('kubernetes.resources.kube-state-metrics-deployment'),
                            },
                        },
                    }))
                ret.object_names_change(self._object_names_changed('kube-state-metrics-'))
                return ret
            except OptionError as e:
                raise OptionError('Kube state metrics option error: {}'.format(str(e))) from e
            except TypeError as e:
                raise OptionError('Kube state metrics type error: {}'.format(str(e))) from e
        else:
            return None

    def _create_nodeexporter_config(self) -> Optional[NodeExporterBuilder]:
        if self.option_get('enable.node-exporter') is not False:
            try:
                ret = NodeExporterBuilder(kubragen=self.kubragen, options=NodeExporterOptions({
                        'basename': self.basename('-node-exporter'),
                        'namespace': self.namespace(),
                        'config': {
                            'prometheus_annotation': self.option_get('config.prometheus_annotation'),
                        },
                        'container': {
                            'node-exporter': self.option_get('container.node-exporter'),
                        },
                        'kubernetes': {
                            'resources': {
                                'daemonset': self.option_get('kubernetes.resources.node-exporter-daemonset'),
                            },
                        },
                    }))
                ret.object_names_change(self._object_names_changed('kube-state-metrics-'))
                return ret
            except OptionError as e:
                raise OptionError('Node exporter option error: {}'.format(str(e))) from e
            except TypeError as e:
                raise OptionError('Node exporter type error: {}'.format(str(e))) from e
        else:
            return None

    def _create_granana_config(self) -> Optional[GrafanaBuilder]:
        if self.option_get('enable.grafana') is not False:
            try:
                ret = GrafanaBuilder(kubragen=self.kubragen, options=GrafanaOptions({
                    'basename': self.basename('-grafana'),
                    'namespace': self.namespace(),
                    'config': {
                        'install_plugins': self.option_get('config.grafana_install_plugins'),
                        'service_port': self.option_get('config.grafana_service_port'),
                        'provisioning': {
                            'datasources': self.option_get('config.grafana_provisioning.datasources'),
                            'plugins': self.option_get('config.grafana_provisioning.plugins'),
                            'dashboards': self.option_get('config.grafana_provisioning.dashboards'),
                        },
                    },
                    'kubernetes': {
                        'volumes': {
                            'data': self.option_get('kubernetes.volumes.grafana-data'),
                        },
                        'resources': {
                            'deployment': self.option_get('kubernetes.resources.grafana-deployment'),
                        },
                    },
                }))
                ret.object_names_change(self._object_names_changed('grafana-'))
                return ret
            except OptionError as e:
                raise OptionError('Grafana option error: {}'.format(str(e))) from e
            except TypeError as e:
                raise OptionError('Grafana type error: {}'.format(str(e))) from e
        else:
            return None
