from tool import *
import docker
import time
# used for testing
# t1 = "alpine"
# t2 = "busybox"
# t3 = "ubuntu"

if __name__ == "__main__":
    start = time.time()
    # Download an image from Docker Hub
    # download_image(name="863444090/dexter:v.1.0")

    # Delete all containers
    deleteall_container()
    # Delete all volumes
    deleteall_volume()

    # Create one volume
    create_volume(num=1)
    # Create three containers with the same image, volume and mount point
    create_container(num=9,
                     type=["863444090/dexter:v.1.0"],
                     type_same=True,
                     volume=True,
                     volume_same=True,
                     volume_source=["v1"],
                     volume_target=["/root/project"])

    # Run all containers
    run_container(all=True)

    # Upload a file to a container c1's volume path
    upload_file_in_container(name='c1', scr='./', dst='/root/project')

    # Write down the information of all containers
    written_container()

    # Run a code in every container(because all_container is True)
    # with multiprocessing(because mutiprocess is True)
    run_code_in(name=["c1", "c2"],
                code=["python3 root/project/demo.py"],
                all_container=True , same_code=True,
                multiprocess=False)

    # Get outputs from a container c1's path and save it as out.tar
    get_outputs_from_container(name='c1',
                               scr='/root/project/out',
                               dst='out.tar')

    # Delete all containers again
    deleteall_container()

    end = time.time()
    print(f"INFO : Consumed {end-start} seconds.")

    # used for testing
    # remove_out_in_container(start=1, end=20)
