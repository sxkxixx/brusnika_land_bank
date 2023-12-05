FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR land_bank/

COPY . .

RUN python3 -m pip install --upgrade pip
RUN pip install poetry && \
       poetry config virtualenvs.create false && \
       poetry install --no-interaction --no-ansi

RUN chmod a+x ./run_application.sh

ENTRYPOINT ["./run_application.sh"]
