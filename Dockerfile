FROM python:3.9-slim

WORKDIR /app


RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


COPY requirements.txt /app/
RUN pip install -r requirements.txt


COPY . /app/


EXPOSE 5000


CMD ["/app/venv/bin/python", "app.py"]
# CMD ["flask", "run", "--host", "0.0.0.0"]
# CMD ["/app/venv/bin/python","app.py", "--host","0.0.0.0","--port","5000"]
