# Installation

### Set up the python environment

It's prefered to do this before you start to install latest gcc and remove all nvidia related drivers and configurations:
```
sudo apt install --reinstall gcc
sudo apt-get --purge -y remove 'nvidia*' (run at your own risk)
```

1. Install Nvidia Driver
```
# Replace XXX with the suitable number, you can find possoble compatible drivers through `apt search nvidia-driver` or using Software & Update Tool in Ubuntu.

sudo apt install nvidia-driver-XXX
```

2. [Download and Install CUDA 10.0](https://developer.nvidia.com/cuda-10.0-download-archive) [Seclct 'No' at installing Nvidia Driver option]

Install by running:
```
sudo sh cuda_10.0.130_410.48_linux.run
```

```
After Installing CUDA 10.0, Please make sure that:
 -   PATH includes `/usr/local/cuda-10.0/bin` # Note: add cuda's path to bashrc to avoid adding it again.
 -   LD_LIBRARY_PATH includes `/usr/local/cuda-10.0/lib64`, or, add `/usr/local/cuda-10.0/lib64` to `/etc/ld.so.conf` and run `ldconfig` as root
```

3. Install Conda

4. Create virtual enviornment
```
conda create -n snake python=3.6
conda activate snake
```


5. Installing torch and other requirements
```
# make sure that the pytorch cuda is consistent with the system cuda
conda install pytorch==1.1.0 torchvision==0.3.0 cudatoolkit=10.0 -c pytorch

pip install Cython==0.28.2
pip install -r requirements.txt
pip install "pillow<7"
```

6. Installing apex

```
cd
git clone https://github.com/NVIDIA/apex.git
cd apex
git checkout 39e153a3159724432257a8fc118807b359f4d1c8
export CUDA_HOME="/usr/local/cuda-10.0"
python setup.py install --cuda_ext --cpp_ext
```

7. Compile cuda extensions under `lib/csrc`

```
ROOT=/path/to/snake
cd $ROOT/lib/csrc
export CUDA_HOME="/usr/local/cuda-10.0"
cd dcn_v2
python setup.py build_ext --inplace
cd ../extreme_utils
python setup.py build_ext --inplace
cd ../roi_align_layer
python setup.py build_ext --inplace
```

When compiling, run the following in case you get `#error -- unsupported GNU version! gcc versions later than 7 are not supported!`:
```
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-6 10
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 10
```


### Set up datasets

#### Cityscapes

1. Download the Cityscapes dataset (leftImg8bit\_trainvaltest.zip) from the official [website](https://www.cityscapes-dataset.com/downloads/).
2. Download the processed annotation file [cityscapes_anno.tar.gz](https://zjueducn-my.sharepoint.com/:u:/g/personal/pengsida_zju_edu_cn/EcaFL3ZLC5VOvR5HupOgHEMByzgiZ0iLpPW0rAb1i57Ytw?e=tocgyq).
3. Organize the dataset as the following structure:
    ```
    ├── /path/to/cityscapes
    │   ├── annotations
    │   ├── coco_ann
    │   ├── leftImg8bit
    │   ├── gtFine
    ```
3. Generate `coco_img`.
	```
	mkdir -p coco_img/train
	cp leftImg8bit/train/*/* coco_img/train
	cp leftImg8bit/val/*/* coco_img/val
	cp leftImg8bit/test/*/* coco_img/test
	```
4. Create a soft link:
    ```
    ROOT=/path/to/snake
    cd $ROOT/data
    ln -s /path/to/cityscapes cityscapes
    ```

#### Kitti

1. Download the Kitti dataset from the official [website](http://www.cvlibs.net/download.php?file=data_object_image_2.zip).
2. Download the annotation file `instances_train.json` and `instances_val.json` from [Kins](https://github.com/qqlu/Amodal-Instance-Segmentation-through-KINS-Dataset).
3. Organize the dataset as the following structure:
	```
    ├── /path/to/kitti
    │   ├── testing
    │   │   ├── image_2
    │   │   ├── instances_val.json
    │   ├── training
    │   │   ├── image_2
    │   │   ├── instances_train.json
    ```
4. Create a soft link:
    ```
    ROOT=/path/to/snake
    cd $ROOT/data
    ln -s /path/to/kitti kitti
    ```

#### Sbd

1. Download the Sbd dataset at [here](https://zjueducn-my.sharepoint.com/:u:/g/personal/pengsida_zju_edu_cn/EV2P-6J0s-hClwW8uZy1ZXYBPU0XwR7Ch7EBGOG2vfACGQ?e=wpyE2M).
2. Create a soft link:
    ```
    ROOT=/path/to/snake
    cd $ROOT/data
    ln -s /path/to/sbd sbd
    ```
