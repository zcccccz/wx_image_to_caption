# syntax=docker/dockerfile:1
# 写在最前面：强烈建议先阅读官方教程[Dockerfile最佳实践]（https://docs.docker.com/develop/develop-images/dockerfile_best-practices/）
# 选择构建用基础镜像（选择原则：在包含所有用到的依赖前提下尽可能提及小）。如需更换，请到[dockerhub官方仓库](https://hub.docker.com/_/python?tab=tags)自行选择后替换。

# 选择基础镜像
FROM python:3.8

# 拷贝当前项目到/app目录下
COPY . /app

# 设定当前的工作目录
WORKDIR /app

# 安装依赖到指定的/install文件夹
# 选用国内镜像源以提高下载速度
RUN pip config set global.index-url http://pypi.doubanio.com/simple \
&& pip config set global.trusted-host pypi.doubanio.com \
&& pip install --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt \
&& pip install opencv-python-headless \
&& pip3 install torch==1.11.0+cpu torchvision==0.12.0+cpu torchaudio==0.11.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html \
&& pip install en_core_web_sm-3.2.0.tar.gz \
&& pip install -U cos-python-sdk-v5

WORKDIR /app/bottom-up-attention.pytorch/detectron2
RUN pip install -e .
WORKDIR /app/bottom-up-attention.pytorch
RUN python setup.py build develop
WORKDIR /app

# 设定对外端口
EXPOSE 80

# 设定启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"]
