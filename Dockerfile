FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml README.md LICENSE ./
COPY apps ./apps
COPY packages ./packages
COPY policies ./policies
RUN pip install --no-cache-dir .
EXPOSE 8080
CMD ["uvicorn","dbxguard_api.main:app","--host","0.0.0.0","--port","8080"]
