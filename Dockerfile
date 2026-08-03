FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

RUN addgroup --system servicemind \
    && adduser --system --ingroup servicemind servicemind

COPY --chown=servicemind:servicemind . .

RUN mkdir -p /app/data /app/logs \
    && chown -R servicemind:servicemind /app/data /app/logs

USER servicemind

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]