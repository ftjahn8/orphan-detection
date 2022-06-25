FROM python:3.10
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY ./requirements.txt /app/requirements.txt
COPY ./orphan_detection /app/orphan_detection
RUN mkdir /app/Data/

RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r /app/requirements.txt

WORKDIR /app/orphan_detection
ENTRYPOINT ["python", "main.py"]

