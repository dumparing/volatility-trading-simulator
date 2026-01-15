FROM public.ecr.aws/lambda/python:3.9

COPY requirements.txt .
RUN pip install -r requirements.txt --target "/var/task"

COPY lambda_handler.py feature_utils.py dynamodb_helper.py /var/task/

RUN chmod 755 /var/task/*.py

CMD ["lambda_handler.lambda_handler"]
