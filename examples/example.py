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
        'prometheus_config': PrometheusConfigFile(options=PrometheusConfigFileOptions({
            'scrape': {
                'prometheus': {
                    'enabled': True,
                }
            },
        })),
        'grafana_provisioning': {
            'datasources': [{
                'name': 'Prometheus',
                'type': 'prometheus',
                'access': 'proxy',
                'url': 'http://{}:{}'.format('prometheus', 80),
            }]
        },
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
