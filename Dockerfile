FROM python:3.10
RUN useradd --create-home --shell /bin/bash user
ENV PYTHONPATH "${PYTHONPATH}:/home/user/orphan-detection"

COPY ./requirements.txt /home/user/orphan-detection/requirements.txt
COPY Data/ /home/user/orphan-detection/Data
COPY orphan_detection/ /home/user/orphan-detection/orphan_detection

RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r /home/user/orphan-detection/requirements.txt

WORKDIR /home/user/orphan-detection/orphan_detection
ENTRYPOINT ["python", "main.py"]

