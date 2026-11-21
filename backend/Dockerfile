FROM python:3.12-slim-bookworm AS build
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY requirements.txt .
RUN python -m venv --without-pip /opt/venv \
    && python -m pip --python /opt/venv install --no-cache-dir --no-compile -r requirements.txt

FROM python:3.12-slim-bookworm AS runtime
ENV PATH="/opt/venv/bin:${PATH}" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8000
ENV DATABASE_URL=sqlite:////data/app.db
RUN groupadd -g 10001 lantern \
    && useradd -M -u 10001 -g lantern lantern \
    && mkdir /data
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --chmod=0555 app ./app
COPY --chmod=755 entrypoint.sh /usr/local/bin/lantern-entrypoint
ENTRYPOINT ["lantern-entrypoint"]
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\" --workers 1 --no-access-log"]
