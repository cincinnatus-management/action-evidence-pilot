# Offline evidence-export demo. Python standard library only. No network is needed at run time.
# Not Docker-certified, not a Docker partner image, not production software.
FROM python:3.12-slim
LABEL org.opencontainers.image.title="action-evidence-export-demo" \
      org.opencontainers.image.source="https://github.com/cincinnatus-management/action-evidence-pilot" \
      org.opencontainers.image.description="Offline demo: verify an action-evidence record chain and export it to a Global Relay-style payload. Operated by AI agents. Not certified, not production."
RUN useradd --create-home --uid 10001 runner
WORKDIR /opt/demo
COPY action_evidence.py ./
COPY connectors/global-relay-export/export_archive.py connectors/global-relay-export/make_fixture.py ./
COPY sample-run-output ./sample-run-output
COPY container/run_demo.sh ./run_demo.sh
RUN chmod 0755 run_demo.sh
USER runner
WORKDIR /home/runner
ENTRYPOINT ["bash", "/opt/demo/run_demo.sh"]
