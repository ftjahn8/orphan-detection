FROM python:3.10

COPY ./orphan_detection /app/orphan_detection
COPY ./main.py /app/main.py

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r /app/requirements.txt

RUN mkdir /app/Data/
WORKDIR /app
ENTRYPOINT ["python", "main.py"]

