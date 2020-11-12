# KubraGen Builder: Prometheus Stack

[![PyPI version](https://img.shields.io/pypi/v/kg_prometheusstack.svg)](https://pypi.python.org/pypi/kg_prometheusstack/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/kg_prometheusstack.svg)](https://pypi.python.org/pypi/kg_prometheusstack/)

kg_prometheusstack is a builder for [KubraGen](https://github.com/RangelReale/kubragen) that deploys 
a [Prometheus](https://prometheus.io/) stack in Kubernetes.

The stack consist of Prometheus (required), Grafana, Kube-State-Metrics and Node Exporter. 

[KubraGen](https://github.com/RangelReale/kubragen) is a Kubernetes YAML generator library that makes it possible to generate
configurations using the full power of the Python programming language.

* Website: https://github.com/RangelReale/kg_prometheusstack
* Repository: https://github.com/RangelReale/kg_prometheusstack.git
* Documentation: https://kg_prometheusstack.readthedocs.org/
* PyPI: https://pypi.python.org/pypi/kg_prometheusstack

## Example

```python
from kg_prometheus import PrometheusConfigFile, PrometheusConfigFileOptions
from kubragen import KubraGen
from kubragen.consts import PROVIDER_GOOGLE, PROVIDERSVC_GOOGLE_GKE
from kubragen.object import Object
from kubragen.option import OptionRoot
from kubragen.options import Options
from kubragen.output import OutputProject, OD_FileTemplate, OutputFile_ShellScript, OutputFile_Kubernetes, \
    OutputDriver_Print
from kubragen.provider import Provider

from kg_prometheusstack import PrometheusStackBuilder, PrometheusStackOptions

kg = KubraGen(provider=Provider(PROVIDER_GOOGLE, PROVIDERSVC_GOOGLE_GKE), options=Options({
    'namespaces': {
        'mon': 'app-monitoring',
    },
}))

out = OutputProject(kg)

shell_script = OutputFile_ShellScript('create_gke.sh')
out.append(shell_script)

shell_script.append('set -e')

#
# OUTPUTFILE: app-namespace.yaml
#
file = OutputFile_Kubernetes('app-namespace.yaml')

file.append([
    Object({
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {
            'name': 'app-monitoring',
        },
    }, name='ns-monitoring', source='app', instance='app')
])

out.append(file)
shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

shell_script.append(f'kubectl config set-context --current --namespace=app-monitoring')

#
# SETUP: prometheusstack
#
pstack_config = PrometheusStackBuilder(kubragen=kg, options=PrometheusStackOptions({
    'namespace': OptionRoot('namespaces.mon'),
    'basename': 'mypstack',
    'config': {
        'prometheus_annotation': True,
        'prometheus': {
            'prometheus_config': PrometheusConfigFile(options=PrometheusConfigFileOptions({
                'scrape': {
                    'prometheus': {
                        'enabled': True,
                    }
                },
            })),
        },
        'grafana': {
            'provisioning': {
                'datasources': [{
                    'name': 'Prometheus',
                    'type': 'prometheus',
                    'access': 'proxy',
                    'url': 'http://{}:{}'.format('prometheus', 80),
                }]
            },
        }
    },
    'kubernetes': {
        'volumes': {
            'prometheus-data': {
                'persistentVolumeClaim': {
                    'claimName': 'prometheusstack-storage-claim'
                }
            }
        },
    },
})).object_names_change({
    'prometheus-service': 'prometheus',
})

pstack_config.ensure_build_names(pstack_config.BUILD_ACCESSCONTROL, pstack_config.BUILD_CONFIG,
                                 pstack_config.BUILD_SERVICE)

#
# OUTPUTFILE: prometheusstack-config.yaml
#
file = OutputFile_Kubernetes('prometheusstack-config.yaml')
out.append(file)

file.append(pstack_config.build(pstack_config.BUILD_ACCESSCONTROL, pstack_config.BUILD_CONFIG))

shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

#
# OUTPUTFILE: prometheusstack.yaml
#
file = OutputFile_Kubernetes('prometheusstack.yaml')
out.append(file)

file.append(pstack_config.build(pstack_config.BUILD_SERVICE))

shell_script.append(OD_FileTemplate(f'kubectl apply -f ${{FILE_{file.fileid}}}'))

#
# Write files
#
out.output(OutputDriver_Print())
# out.output(OutputDriver_Directory('/tmp/build-gke'))
```

Output:

```text
****** BEGIN FILE: 001-app-namespace.yaml ********
apiVersion: v1
kind: Namespace
metadata:
  name: app-monitoring

****** END FILE: 001-app-namespace.yaml ********
****** BEGIN FILE: 002-prometheusstack-config.yaml ********
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mypstack
  namespace: app-monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: mypstack-prometheus
rules:
- apiGroups: ['']
<...more...>
****** END FILE: 002-prometheusstack-config.yaml ********
****** BEGIN FILE: 003-prometheusstack.yaml ********
kind: Service
apiVersion: v1
metadata:
  name: mypstack-prometheus
  namespace: app-monitoring
spec:
  selector:
    app: mypstack-prometheus
  ports:
  - protocol: TCP
    port: 80
    targetPort: 9090
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mypstack-prometheus
  namespace: app-monitoring
<...more...>
****** END FILE: 003-prometheusstack.yaml ********
****** BEGIN FILE: create_gke.sh ********
#!/bin/bash

set -e
kubectl apply -f 001-app-namespace.yaml
kubectl config set-context --current --namespace=app-monitoring
kubectl apply -f 002-prometheusstack-config.yaml
kubectl apply -f 003-prometheusstack.yaml

****** END FILE: create_gke.sh ********
```

## Author

Rangel Reale (rangelreale@gmail.com)
