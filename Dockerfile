FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY decisionpilot ./decisionpilot
COPY agentcore_main.py ./
RUN pip install --no-cache-dir '.[aws]' && useradd --uid 10001 --create-home pilot && mkdir /data && chown pilot:pilot /data
USER pilot
ENV HOST=0.0.0.0 PORT=8080 DECISIONPILOT_DB=/data/workflows-v2.db DECISIONPILOT_MODE=offline
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"
CMD ["python", "-m", "decisionpilot.server"]
