FROM python:3

RUN pwd
COPY requirements-docker.txt ./
COPY tolaat tolaat
RUN pip install --no-cache-dir -r requirements-docker.txt

EXPOSE 5000
CMD ["python3", "tolaat/zappa_entry_main_docker.py"]