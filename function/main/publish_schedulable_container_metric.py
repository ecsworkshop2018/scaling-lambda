import boto3
import datetime


def lambda_handler(event, context):
    """
    The entry function of the lambda
    """
    aws = AWS()
    all_clusters = list_all_clusters_arns(aws)
    cluster_schedulable_containers_map = get_schedulable_containers_for_all_clusters(all_clusters, aws)
    filtered_cluster_schedulable_container_map = filter(lambda clustermap: clustermap["schedulable_containers"] is not None, cluster_schedulable_containers_map)
    put_metrics_data(filtered_cluster_schedulable_container_map)


def list_all_clusters_arns(aws):
    cluster_list = aws.cluster_list()
    return cluster_list["clusterArns"]


def list_cluster_container_instance_arns(cluster_arn, aws):
    return aws.container_instances_for_cluster(cluster_arn)["containerInstanceArns"]


def get_instances_details(cluster_name, instance_arns, aws):
    if len(instance_arns) > 0:
        return aws.get_instance_details(cluster_name, instance_arns)["containerInstances"]
    else:
        return []


def get_cluster_tasks(cluster_arn, aws):
    task_arns = aws.list_cluster_tasks(cluster_arn)["taskArns"]
    if len(task_arns) > 0:
        return aws.get_task_details(cluster_arn, task_arns)["tasks"]
    else:
        return []

def get_max_task_cpu(tasks):
    return max(list(map(lambda task: int(task["cpu"]), tasks)))


def get_max_task_memory(tasks):
    return max(list(map(lambda task: int(task["memory"]), tasks)))


def get_instance_remaining_cpu(instance_details):
    return next(filter(lambda resource: resource["name"] == "CPU", instance_details["remainingResources"]))[
        "integerValue"]


def get_instance_remaining_memory(instance_details):
    return next(filter(lambda resource: resource["name"] == "MEMORY", instance_details["remainingResources"]))[
        "integerValue"]


def get_schedulable_containers_by_cpu_on_instance(instance_remaining_cpu, max_task_cpu):
    return int(instance_remaining_cpu / max_task_cpu)


def get_schedulable_containers_by_memory_on_instance(instance_remaining_memory, max_task_memory):
    return int(instance_remaining_memory / max_task_memory)


def get_instance_schedulable_containers(instance_details, max_task_cpu, max_task_memory):
    instance_remaining_cpu = get_instance_remaining_cpu(instance_details)
    instance_remaining_memory = get_instance_remaining_memory(instance_details)
    return min(get_schedulable_containers_by_cpu_on_instance(instance_remaining_cpu, max_task_cpu),
               get_schedulable_containers_by_memory_on_instance(instance_remaining_memory, max_task_memory))


def get_schedulable_containers_for_entire_cluster(instances_details, max_task_cpu, max_task_memory):
    return sum(map(
        lambda instance_details: get_instance_schedulable_containers(instance_details, max_task_cpu, max_task_memory),
        instances_details))


def get_schedulable_containers_for_all_clusters(cluster_arns, aws):
    return list(map(lambda cluster_name: {"cluster_name": cluster_name,
                                          "schedulable_containers": cluster_schedulable_containers(cluster_name, aws)},
                    get_cluster_names(cluster_arns)))


def get_cluster_names(cluster_arns):
    return list(map(lambda cluster_arn: cluster_arn.split("/")[1], cluster_arns))


def cluster_schedulable_containers(cluster_name, aws):
    instance_arns = list_cluster_container_instance_arns(cluster_name, aws)
    instances_details = get_instances_details(cluster_name, instance_arns, aws)
    tasks = get_cluster_tasks(cluster_name, aws)
    if(len(tasks) > 0):
        max_task_cpu = get_max_task_cpu(tasks)
        max_task_memory = get_max_task_memory(tasks)
        return get_schedulable_containers_for_entire_cluster(instances_details, max_task_cpu, max_task_memory)
    else:
        return None



def put_metrics_data(cluster_schedulable_containers_map):
    metric_data = list(map(
        lambda cluster_schedulable_containers_entry: metric_data_entry(cluster_schedulable_containers_entry),
        cluster_schedulable_containers_map))
    client = boto3.client('cloudwatch', region_name='us-east-1')
    client.put_metric_data(Namespace="CUSTOM/ECS",MetricData=metric_data)


def metric_data_entry(cluster_schedulable_containers_entry):
    return {
        'MetricName': 'SchedulableContainers',
        'Dimensions': [{
            'Name': 'ClusterName',
            'Value': cluster_schedulable_containers_entry["cluster_name"]
        }],
        'Timestamp': datetime.datetime.now(),
        'Value': cluster_schedulable_containers_entry["schedulable_containers"]
    }


class AWS:
    def __init__(self):
        self.ecs_client = boto3.client('ecs', region_name='us-east-1')

    def cluster_list(self):
        return self.ecs_client.list_clusters()

    def container_instances_for_cluster(self, cluster_arn):
        return self.ecs_client.list_container_instances(cluster=cluster_arn, status="ACTIVE")

    def list_cluster_tasks(self, cluster_arn):
        return self.ecs_client.list_tasks(cluster=cluster_arn)

    def get_task_details(self, cluster_arn, task_arns):
        return self.ecs_client.describe_tasks(cluster=cluster_arn, tasks=task_arns)

    def get_instance_details(self, cluster_name, instance_arns):
        return self.ecs_client.describe_container_instances(cluster=cluster_name, containerInstances=instance_arns)
