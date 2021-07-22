FROM python:3

RUN pwd
COPY requirements-docker.txt ./
COPY website/ website
COPY instance/ instance
RUN pip install --no-cache-dir -r requirements-docker.txt
COPY zappa_entry_main_docker.py ./

EXPOSE 5000
CMD ["python3", "zappa_entry_main_docker.py"]