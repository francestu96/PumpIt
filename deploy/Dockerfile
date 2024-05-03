FROM python:alpine3.19

WORKDIR /pump_it

COPY ./pump_it.py ./channels_config.py ./requirements.txt .
COPY ./classes ./classes

RUN pip install -r requirements.txt

CMD [ "python", "pump_it.py" ]