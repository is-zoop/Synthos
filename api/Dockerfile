FROM python:3.11.9-slim

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_EXTRA_INDEX_URL=

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -n "$PIP_EXTRA_INDEX_URL" ]; then \
      pip install --no-cache-dir -r requirements.txt \
      --index-url "$PIP_INDEX_URL" \
      --extra-index-url "$PIP_EXTRA_INDEX_URL" \
      --retries 5 \
      --timeout 60; \
    else \
      pip install --no-cache-dir -r requirements.txt \
      --index-url "$PIP_INDEX_URL" \
      --retries 5 \
      --timeout 60; \
    fi

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
