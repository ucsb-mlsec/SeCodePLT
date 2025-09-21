FROM python:3.11-alpine

WORKDIR /root

RUN pip install pydantic
RUN python -m venv venv
COPY code_template.py run_test.py ./
CMD ["tail", "-f", "/dev/null"]
