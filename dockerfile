FROM python:3.10-bookworm
# RUN apk update
# RUN apk add py-pip
# RUN apk add --no-cache python3-dev 
RUN pip install --upgrade pip
WORKDIR /pv-power-api
COPY . /pv-power-api
RUN python3 -m pip --no-cache-dir install -r requirements.txt
CMD ["python3", "api.py"]


# FROM alpine:latest
# RUN apk update
# RUN apk add py-pip
# RUN apk add --no-cache python3-dev 
# RUN pip install --upgrade pip
# WORKDIR /app
# COPY . /app
# RUN pip --no-cache-dir install -r requirements.txt
# CMD ["python3", "api.py"]