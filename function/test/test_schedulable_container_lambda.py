from ..main.publish_schedulable_container_metric import list_all_clusters_arns
from ..main.publish_schedulable_container_metric import AWS
from ..main.publish_schedulable_container_metric import list_cluster_container_instance_arns
from ..main.publish_schedulable_container_metric import get_cluster_tasks
from ..main.publish_schedulable_container_metric import get_max_task_cpu
from ..main.publish_schedulable_container_metric import get_max_task_memory
from ..main.publish_schedulable_container_metric import get_instances_details
from ..main.publish_schedulable_container_metric import get_instance_remaining_cpu
from ..main.publish_schedulable_container_metric import get_instance_remaining_memory
from ..main.publish_schedulable_container_metric import get_schedulable_containers_by_cpu_on_instance
from ..main.publish_schedulable_container_metric import get_schedulable_containers_by_memory_on_instance
from ..main.publish_schedulable_container_metric import get_instance_schedulable_containers
from ..main.publish_schedulable_container_metric import get_schedulable_containers_for_entire_cluster
from ..main.publish_schedulable_container_metric import get_schedulable_containers_for_all_clusters


# TODO - Add tests around empty tasks and empty cluster (with no instances)

def test_list_all_clusters_arns():
    # Given
    expected_arns = [
        'arn:aws:ecs:us-east-1:<aws_account_id>:cluster/test',
        'arn:aws:ecs:us-east-1:<aws_account_id>:cluster/default',
    ]

    aws = Stub_Aws()
    # when
    cluster_arns = list_all_clusters_arns(aws)
    # then
    assert cluster_arns == expected_arns


def test_get_cluster_instances():
    # Given
    expected_container_instance_arns = [
        'arn:aws:ecs:us-east-1:<aws_account_id>:container-instance/f6bbb147-5370-4ace-8c73-c7181ded911f',
        'arn:aws:ecs:us-east-1:<aws_account_id>:container-instance/ffe3d344-77e2-476c-a4d0-bf560ad50acb',
    ]
    aws = Stub_Aws()
    # When
    container_instance_arns = list_cluster_container_instance_arns("some_cluster", aws)
    # then
    assert container_instance_arns == expected_container_instance_arns


def test_get_cluster_tasks():
    cluster_arn = "some_cluster"
    aws = Stub_Aws()
    tasks = get_cluster_tasks(cluster_arn, aws)
    assert tasks == aws.tasks


def test_get_max_task_cpu():
    tasks = [{"cpu": "300"}, {"cpu": "500"}, {"cpu": "200"}, {"cpu": "1024"}]
    max_cpu = get_max_task_cpu(tasks)
    assert max_cpu == 1024


def test_get_max_task_memory():
    tasks = [{"memory": "300"}, {"memory": "500"}, {"memory": "200"}, {"memory": "1024"}]
    max_cpu = get_max_task_memory(tasks)
    assert max_cpu == 1024


def test_get_instance_details():
    aws = Stub_Aws()
    cluster_name = "some_cluster"
    instances_details = get_instances_details(cluster_name, aws.instance_arns, aws)
    assert instances_details == aws.instances_details


def test_get_instance_remaining_cpu():
    aws = Stub_Aws()
    remaining_cpu = get_instance_remaining_cpu(aws.instances_details[0])
    assert remaining_cpu == aws.cpu


def test_get_instance_remaining_memory():
    aws = Stub_Aws()
    remaining_memory = get_instance_remaining_memory(aws.instances_details[0])
    assert remaining_memory == aws.memory


def test_get_schedulable_containers_by_cpu_on_instance():
    instance_remaining_cpu = 1948
    max_task_cpu = 256
    assert get_schedulable_containers_by_cpu_on_instance(instance_remaining_cpu, max_task_cpu) == int(1948 / 256)


def test_get_schedulable_containers_by_memory_on_instance():
    instance_remaining_memory = 3668
    max_task_memory = 768
    assert get_schedulable_containers_by_memory_on_instance(instance_remaining_memory, max_task_memory) == int(
        instance_remaining_memory / max_task_memory)


def test_get_schedulable_containers_for_an_instance():
    max_task_cpu = 256
    max_task_memory = 768
    assert 4 == get_instance_schedulable_containers(Stub_Aws().instances_details[0], max_task_cpu, max_task_memory)


def test_get_schedulable_containers_for_entire_cluster():
    cluster_instances = Stub_Aws().instances_details
    max_task_cpu = 256
    max_task_memory = 768
    schedulable_containers = get_schedulable_containers_for_entire_cluster(cluster_instances, max_task_cpu,
                                                                           max_task_memory)
    assert schedulable_containers == 4


def test_get_schedulable_containers_for_all_clusters():
    cluster_arns = [
        'arn:aws:ecs:us-east-1:<aws_account_id>:cluster/test',
        'arn:aws:ecs:us-east-1:<aws_account_id>:cluster/default',
    ]
    aws = Stub_Aws()
    expected_cluster_schedulable_containers_map = [{"cluster_name": "test", "schedulable_containers": 4}, {"cluster_name": "default", "schedulable_containers": 4}]
    cluster_schedulable_containers_map = get_schedulable_containers_for_all_clusters(cluster_arns, aws)
    assert cluster_schedulable_containers_map == expected_cluster_schedulable_containers_map


class Stub_Aws(AWS):
    task_arns = [
        'arn:aws:ecs:us-east-1:012345678910:task/0cc43cdb-3bee-4407-9c26-c0e6ea5bee84',
        'arn:aws:ecs:us-east-1:012345678910:task/6b809ef6-c67e-4467-921f-ee261c15a0a1',
    ]

    instance_arns = [
        'arn:aws:ecs:us-east-1:<aws_account_id>:container-instance/f6bbb147-5370-4ace-8c73-c7181ded911f',
        'arn:aws:ecs:us-east-1:<aws_account_id>:container-instance/ffe3d344-77e2-476c-a4d0-bf560ad50acb',
    ]

    tasks = [
        {
            'clusterArn': 'arn:aws:ecs:<region>:<aws_account_id>:cluster/default',
            'containerInstanceArn': 'arn:aws:ecs:<region>:<aws_account_id>:container-instance/18f9eda5-27d7-4c19-b133-45adc516e8fb',
            'cpu': '256',
            'memory': '768',
            'containers': [
                {
                    'name': 'ecs-demo',
                    'containerArn': 'arn:aws:ecs:<region>:<aws_account_id>:container/7c01765b-c588-45b3-8290-4ba38bd6c5a6',
                    'lastStatus': 'RUNNING',
                    'networkBindings': [
                        {
                            'bindIP': '0.0.0.0',
                            'containerPort': 80,
                            'hostPort': 80,
                        },
                    ],
                    'taskArn': 'arn:aws:ecs:<region>:<aws_account_id>:task/c5cba4eb-5dad-405e-96db-71ef8eefe6a8',
                },
            ],
            'desiredStatus': 'RUNNING',
            'lastStatus': 'RUNNING',
            'overrides': {
                'containerOverrides': [
                    {
                        'name': 'ecs-demo',
                    },
                ],
            },
            'startedBy': 'ecs-svc/9223370608528463088',
            'taskArn': 'arn:aws:ecs:<region>:<aws_account_id>:task/c5cba4eb-5dad-405e-96db-71ef8eefe6a8',
            'taskDefinitionArn': 'arn:aws:ecs:<region>:<aws_account_id>:task-definition/amazon-ecs-sample:1',
        },
    ]

    cpu = 1948
    memory = 3668

    instances_details = [
        {
            'containerInstanceArn': 'string',
            'ec2InstanceId': 'string',
            'version': 123,
            'versionInfo': {
                'agentVersion': 'string',
                'agentHash': 'string',
                'dockerVersion': 'string'
            },
            'remainingResources': [
                {
                    'name': 'CPU',
                    'type': 'INTEGER',
                    'doubleValue': 0.0,
                    'integerValue': cpu,
                    'longValue': 0,
                },
                {
                    'name': 'MEMORY',
                    'type': 'INTEGER',
                    'doubleValue': 0.0,
                    'integerValue': memory,
                    'longValue': 0,
                },
                {
                    'name': 'PORTS',
                    'type': 'STRINGSET',
                    'doubleValue': 0.0,
                    'integerValue': 0,
                    'longValue': 0,
                    'stringSetValue': [
                        '2376',
                        '22',
                        '80',
                        '51678',
                        '2375',
                    ],
                },
            ],
            'registeredResources': [
                {
                    'name': 'string',
                    'type': 'string',
                    'doubleValue': 123.0,
                    'longValue': 123,
                    'integerValue': 123,
                    'stringSetValue': [
                        'string',
                    ]
                },
            ],
            'status': 'string',
            'agentConnected': True | False,
            'runningTasksCount': 123,
            'pendingTasksCount': 123,
            'agentUpdateStatus': 'PENDING',
            'attributes': [
                {
                    'name': 'string',
                    'value': 'string',
                    'targetType': 'container-instance',
                    'targetId': 'string'
                },
            ],
            'registeredAt': "",
            'attachments': [
                {
                    'id': 'string',
                    'type': 'string',
                    'status': 'string',
                    'details': [
                        {
                            'name': 'string',
                            'value': 'string'
                        },
                    ]
                },
            ],
            'tags': [
                {
                    'key': 'string',
                    'value': 'string'
                },
            ]
        },
    ]

    def cluster_list(self):
        return {
            'clusterArns': [
                'arn:aws:ecs:us-east-1:<aws_account_id>:cluster/test',
                'arn:aws:ecs:us-east-1:<aws_account_id>:cluster/default',
            ],
            'ResponseMetadata': {
            },
        }

    def container_instances_for_cluster(self, cluster_arn):
        return {
            'containerInstanceArns': [
                'arn:aws:ecs:us-east-1:<aws_account_id>:container-instance/f6bbb147-5370-4ace-8c73-c7181ded911f',
                'arn:aws:ecs:us-east-1:<aws_account_id>:container-instance/ffe3d344-77e2-476c-a4d0-bf560ad50acb',
            ],
            'ResponseMetadata': {
            },
        }

    def list_cluster_tasks(self, cluster_arn):
        return {
            'taskArns': self.task_arns,
            'ResponseMetadata': {
            }
        }

    def get_task_details(self, cluster_arn, task_arns):
        assert task_arns == self.task_arns
        return {
            'failures': [
            ],
            'tasks': self.tasks,
            'ResponseMetadata': {
            }
        }

    def get_instance_details(self, cluster_name, instance_arns):
        assert instance_arns == self.instance_arns
        return {
            'containerInstances': self.instances_details,
            'failures': [
                {
                    'arn': 'string',
                    'reason': 'string'
                },
            ]
        }
