import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project): #function that instantiates instances object by passing in a project tag
    instances = []

    if project:
        filters = [{'Name':'tag:project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group() #main group called cli
def cli():
    """Shotty manages snapshots""" #triple quotes provides help text

@cli.group('snapshots') #volumes inside cli group
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list') #decorator command, allows click to use function
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
def list_snapshots(project):
    "List EC2 snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

    return

@cli.group('volumes') #volumes inside cli group
def volumes():
    """Commands for volumes"""

@volumes.command('list') #decorator command, allows click to use function
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrytped" or "Not Encrypted"
            )))

    return

@cli.group() #instances inside cli group
def instances():
        """Commands for instances"""

@instances.command('snapshot',
    help='Create snapshots of all volumes')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print('Creating snapshot of {0}'.format(v.id))
            v.create_snapshot(Description='Created by aws snapshot utility')

        print("Starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print('Job complete')

    return

@instances.command('list') #decorator command, allows click to use function
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
        i.id,
        i.instance_type,
        i.placement['AvailabilityZone'],
        i.state['Name'],
        i.public_dns_name,
        tags.get('project', '<no project>'))))

    return

@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances for project')
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print('Stopping {0}...'.format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}. ".format(i.id) + str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for project')
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print('Starting {0}...'.format(i.id))
            try:
                i.start()
            except botocore.exceptions.ClientError as e:
                print("Could not start {0}. ".format(i.id) + str(e))
                continue

    return

if __name__ == '__main__':
    cli()
