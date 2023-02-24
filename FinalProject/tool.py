import docker
import multiprocessing

# Define images to be used
t1 = "alpine"
t2 = "busybox"
t3 = "ubuntu"
def download_image(name='863444090/dexter:v.1.0'):
    """
    Downloads a Docker image using the Docker SDK for Python.

    :param name: Name of the Docker image to download (default is '863444090/dexter:v.1.0')
    :return: None
    """
    repository = name.split(':')[0]
    tag = name.split(':')[1]
    print(f"INFO: Image->{repository}:{tag} is downloading...")
    client = docker.from_env()
    client.images.pull(repository=repository, tag=tag)
    print(f"INFO: Image->{repository}:{tag} is downloaded")

def create_volume(num=2):
    """
    Create Docker volumes.

    :param num: number of volumes to be created
    :return:
    """
    client = docker.from_env()
    num_volumes = len(client.volumes.list())

    for i, j in enumerate(range(num), start=1):
        name = "v" + str(i+num_volumes)
        print("INFO: Volume", name, "is created", j)
        client.volumes.create(name)

def deleteall_volume():
    """
    Delete all Docker volumes.

    :return:
    """
    client = docker.from_env()
    volumes = client.volumes.list()
    for volume in volumes:
        volume.remove()

def create_container(num=1, type=[], type_same=False, volume=False, volume_same=False, volume_target=[], volume_source=[]):
    """
    Create Docker containers.

    :param num: number of containers to be created
    :param type: type of image to be used
    :param type_same: whether to use the same image for all containers
    :param volume: whether to create a volume or not
    :param volume_same: whether to use the same volume for all containers
    :param volume_target: the path of container for volume to be mounted
    :param volume_source: the name of the volume
    :return:
    """
    client = docker.from_env()

    num_container = len(client.containers.list(all=True))

    if type_same == True and num != 1:
        type = type*num

    if volume_same == True and num != 1:
        volume_target = volume_target * num
        volume_source = volume_source * num

    for i, j in enumerate(type, start=1):
        name = "c" + str(i+num_container)
        if volume == False:
            demo = client.containers.create(image=j, command="sh", tty=True, name=name, hostname=name)
            print("Container:", name, "created, Type ->", j)
        else:
            mount = docker.types.Mount(
                target=volume_target[i - 1],
                source=volume_source[i - 1],
                type='volume',
            )
            demo = client.containers.create(image=j, command="sh", tty=True, name=name, mounts=[mount], hostname=name)
            print("INFO: Container:", name, "is created; Type ->", j, "; Volume ->", volume_source[i - 1])

def delete_container(name):
    """
    Delete a Docker container.

    :param name: name of the container to be deleted
    :return:
    """
    client = docker.from_env()
    for i, j in enumerate(name, start=1):
        demo = client.containers.get(j)
        demo.remove(force=True)

def deleteall_container():
    """
    Delete all Docker containers.

    :return:
    """
    client = docker.from_env()
    for i in client.containers.list(all=True):
        i.remove(force=True)

def run_container(name=[], all=False):
    """
    Start a Docker container.

    :param name: name of the container to be started
    :param all: whether to start all containers
    :return:
    """
    client = docker.from_env()
    if all == False:
        for i,j in enumerate(name,start=1):
            demo = client.containers.get(j)
            demo.start()
    else:
        for demo in client.containers.list(all=True):
            demo.start()

def stop(name):
    """
    Stops the containers with the given names.

    :param name: A list of names of the containers to be stopped.
    :return: None
    """
    client = docker.from_env()
    for i,j in enumerate(name,start=1):
        demo = client.containers.get(j)
        demo.stop(timeout=0)

def written_container():
    """
    Writes information about all the containers to a file named "State of cluster.txt".

    :return: None
    """
    client = docker.from_env()
    with open("State of cluster.txt", 'w', encoding="utf-8") as f:
        for i in client.containers.list(all=True):
            print('INFO: Container ', i.name, "written to State of cluster.txt")
            f.write("Name: " + i.name + '\n')
            f.write("Id: " + i.id + '\n')
            t = i.logs(timestamps=True)
            f.write("Image: " + str(i.image.tags[0]) + '\n')
            f.write("Status: " + i.status + '\n')
            f.write("Timestamps: " + str(i.logs(timestamps=True) )+ '\n')
            f.write('\n')

def f_for_run_code_in(name, code):
    """
    Runs the given code in a container with the given name.

    :param name: The name of the container in which the code will be executed.
    :param code: The code to be executed.
    :return: None
    """
    client = docker.from_env()
    demo = client.containers.get(name)
    demo.exec_run(code)
    print(f"INFO: Container {demo.name} finished {code}.")
    written_container()

def run_code_in(name=["c1"], code=["echo hello world"], all_container=False, same_code=False, multiprocess=False):
    """
    Runs the given code in the containers with the given names.

    :param name: A list of names of the containers in which the code will be executed. Default is ["c1"].
    :param code: A list of codes to be executed. Default is ["echo hello world"].
    :param all_container: If True, runs the code in all the containers. Default is False.
    :param same_code: If True, runs the same code in all the containers. Default is False.
    :param multiprocess: If True, runs the code in multiple processes. Default is False.
    :return: None
    """
    client = docker.from_env()
    if all_container == True:
        num = len(client.containers.list())
        # print(num)
        # print("print_name()",client.containers.list()[0].name())
        name = list(map(lambda x:x.name, client.containers.list()))
    else:
        num = len(name)
        # print(num)
    if same_code == True:
        code = code * num

    if multiprocess == False:
        for i, j in enumerate(name, start=1):
            demo = client.containers.get(j)
            # a, b =demo.exec_run(code[i-1], detach=True)
            a, b =demo.exec_run(code[i-1])
            # print(a)
            print("INFO: return ->", b)
            print('INFO:', j, "executed ->",code[i-1])
    else:
        all_p = []
        for i, j in enumerate(name, start=1):
            p = multiprocessing.Process(target=f_for_run_code_in, args=(j, code[i-1],))
            p.start()
            all_p.append(p)

        for p in all_p:
            p.join()
            # print("Finished!")
        print("INFO: All containers finished code.")


def get_outputs_from_container(name='c1', scr='/root/project/out', dst='out.tar'):
    """
    This function retrieves files from a Docker container and saves them to the host.

    :param name: The name of the Docker container to retrieve files from.
    :param scr: The path to the files to retrieve within the container.
    :param dst: The path to save the retrieved files on the host.
    :return: None
    """
    # Create a Docker client.
    client = docker.from_env()
    # Get the specified Docker container by name.
    c1 = client.containers.get(name)

    # Open a file in write binary mode for writing the retrieved files.
    f = open(dst, 'wb')
    # Retrieve the files from the container as a tar archive and get its size.
    bits, stat = c1.get_archive(scr)
    # Write the tar archive chunk by chunk to the file.
    for chunk in bits:
        f.write(chunk)
    # Close the file.
    f.close()
    # Print a message indicating the data was saved to the host.
    print("INFO: Data saved to host.")

def upload_file_in_container(name='c1', scr='./', dst='/root/project'):
    """
    This function uploads files to a Docker container.

    :param name: The name of the Docker container to upload files to.
    :param scr: The path to the files to upload on the host.
    :param dst: The path to upload the files to within the container.
    :return: None
    """
    # Create a Docker client.
    client = docker.from_env()
    # Get the specified Docker container by name.
    demo = client.containers.get(name)

    # Set the local path to the files to upload.
    local_path = scr
    # Set the target path for the uploaded files within the container.
    target_path = dst

    # Create a tar archive from the local files to upload.
    tar_data = docker.utils.tar(local_path)

    # Upload the tar archive to the container at the target path.
    demo.put_archive(target_path, tar_data)
    # Print a message indicating the data was uploaded to the container.
    print("INFO: Data uploaded to container")

def remove_out_in_container(start=1, end=20):
    """
    This function removes output files from Docker containers.

    :param start: The starting number of the output files to remove.
    :param end: The ending number of the output files to remove.
    :return: None
    """
    # Iterate over the range of output files to remove.
    for i in range(start, end+1):
        # Construct a command to remove the output file with the current number.
        s = "rm /root/project/out_c"+ str(i) + ".png"
        # Execute the command in specified Docker container(s).
        run_code_in(name=["c1"], code=[s], all_container=False, same_code=False,mutiprocess=False)