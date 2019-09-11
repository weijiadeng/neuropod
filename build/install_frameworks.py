#
# Uber, Inc. (c) 2019
#

# Installs the appropriate pip packages depending on the following env variables
# NEUROPODS_IS_GPU
# NEUROPODS_TORCH_VERSION
# NEUROPODS_TENSORFLOW_VERSION
import os
import platform
import subprocess
import sys

# The `or` pattern below handles empty strings and unset env variables
# Using a default value only handles unset env variables
REQUESTED_TF_VERSION = os.getenv("NEUROPODS_TENSORFLOW_VERSION") or "1.12.0"
REQUESTED_TORCH_VERSION = os.getenv("NEUROPODS_TORCH_VERSION") or "1.1.0"
IS_GPU = (os.getenv("NEUROPODS_IS_GPU") or None) is not None
CUDA_VERSION = os.getenv("NEUROPODS_CUDA_VERSION") or "10.0"
IS_MAC = platform.system() == "Darwin"

def pip_install(args):
    cmd = [sys.executable, "-m", "pip", "install"] + args
    print("Running pip command: {}".format(cmd))
    subprocess.check_call(cmd)

def install_pytorch(version):
    """
    :param  version:    The version of torch. This can be something like "1.2.0" or
                        "1.1.0.dev20190601"
    """
    pip_args = []

    # Get the torch cuda string (e.g. cpu, cu90, cu92, cu100)
    torch_cuda_string = "cu{}".format(CUDA_VERSION.replace(".", "")) if IS_GPU else "cpu"

    # The base version of torch (e.g. 1.2.0)
    version_base = None

    # If this is a nightly build, what's the date (e.g. 20190809)
    version_date = None

    # Get the version info
    if "dev" in version:
        version_base, version_date = version.split(".dev")
    else:
        version_base = version

    if version_date != None:
        # This is a nightly build
        pip_args += ["-f", "https://download.pytorch.org/whl/nightly/" + torch_cuda_string + "/torch_nightly.html"]
    else:
        # This is a stable build
        pip_args += ["-f", "https://download.pytorch.org/whl/torch_stable.html"]

    # Mac builds do not have the cuda string as part of the version
    if not IS_MAC:
        # If this is the 1.2.0 stable release or it's a nightly build after they started adding the cuda string to the packages
        if (version_base == "1.2.0" and version_date is None) or (version_date != None and int(version_date) > 20190723):
            # For CUDA 10 builds, they don't add `cu100` to the version string
            if torch_cuda_string != "cu100":
                version += "+" + torch_cuda_string

    if version_date != None:
        if int(version_date) >= 20190802:
            pip_args += ["torch==" + version]
        else:
            pip_args += ["torch_nightly==" + version]
    else:
        if IS_GPU and version_base == "1.1.0":
            # Figure out the correct platform to use
            package_version_map = {
                (2,7): "cp27-cp27mu",
                (3,5): "cp35-cp35m",
                (3,6): "cp36-cp36m",
                (3,7): "cp37-cp37m",
            }
            platform_version = package_version_map[(sys.version_info.major, sys.version_info.minor)]

            pip_args += ["https://download.pytorch.org/whl/" + torch_cuda_string + "/torch-" + version + "-" + platform_version + "-linux_x86_64.whl"]
        else:
            pip_args += ["torch==" + version]

    pip_install(pip_args)


def install_tensorflow(version):
    if "dev" in version:
        package = "tf-nightly"
    else:
        package = "tensorflow"

    if IS_GPU:
        package += "-gpu"

    pip_install([package + "==" + version])

if __name__ == '__main__':
    print("Installing tensorflow", REQUESTED_TF_VERSION, "and torch", REQUESTED_TORCH_VERSION)
    install_tensorflow(REQUESTED_TF_VERSION)
    install_pytorch(REQUESTED_TORCH_VERSION)