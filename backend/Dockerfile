FROM python:3.12-slim-bookworm AS build
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim-bookworm AS runtime
ENV PATH="/opt/venv/bin:${PATH}" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8000
RUN groupadd -g 10001 lantern \
    && useradd -M -u 10001 -g lantern lantern \
    && install -d -o lantern -g lantern /app /data \
    && touch /data/.lantern-volume \
    && chown lantern:lantern /data/.lantern-volume
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY app ./app
COPY --chmod=755 entrypoint.sh /usr/local/bin/lantern-entrypoint
ENTRYPOINT ["lantern-entrypoint"]
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\" --workers 1 --no-access-log"]
