#!/bin/bash

set -e

echo "Updating system and installing build dependencies..."
sudo apt-get update -y
sudo apt-get install -y gcc-12 g++-12 libnuma-dev cmake libdnnl-dev
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 10 --slave /usr/bin/g++ g++ /usr/bin/g++-12

echo "Python version:"
python --version

echo "Python executable location:"
which python

echo "Installing Python build dependencies..."
python -m pip install --upgrade pip
python -m pip install wheel packaging ninja "setuptools>=49.4.0" numpy setuptools-scm

echo "Cloning 'vllm-project/vllm' GitHub repository..."
git clone https://github.com/vllm-project/vllm.git
cd vllm || exit

git fetch --tags
latest_tag=$(git describe --tags "$(git rev-list --tags --max-count=1)")

echo "Checking out to '$latest_tag' tag..."
git checkout "$latest_tag"

requirements_file=""
for candidate in requirements-cpu.txt requirements/cpu.txt requirements.txt; do
    if [ -f "$candidate" ]; then
        requirements_file="$candidate"
        break
    fi
done
if [ -z "$requirements_file" ]; then
    echo "No vLLM requirements file found for CPU install."
    exit 1
fi

echo "Installing vLLM requirements from ${requirements_file}..."
python -m pip install -r "$requirements_file" --extra-index-url https://download.pytorch.org/whl/cpu

echo "Installing vLLM for CPU..."
export CMAKE_ARGS="-DPYTHON_EXECUTABLE=$(which python) -DPYTHON_INCLUDE_DIR=$(python -c "from sysconfig import get_path; print(get_path('include'))") -DPYTHON_LIBRARY=$(python -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")"
echo "CMake args: $CMAKE_ARGS"
VLLM_TARGET_DEVICE=cpu python setup.py install

echo "Installation complete!"
