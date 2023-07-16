FROM python:3.9-slim as django
ENV PYTHONUNBUFFERED=1

WORKDIR /src
COPY requirements.txt ./

ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID dev  &&  \
    useradd -m -u $UID -g $GID dev && \
    pip install -r requirements.txt

COPY ./ /src
USER dev
# CMD ["bash"]
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0:8000"]
