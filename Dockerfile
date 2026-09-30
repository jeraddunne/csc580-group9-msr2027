# Documented container: reproduce the P-01 results from a clean environment (issue #71).
# Python and every package version match results/ANALYSIS_MANIFEST.json, the environment that
# produced the committed results. Full instructions: docs/REPRODUCE.md.
#
#   docker build -t group9-p01 https://github.com/jeraddunne/csc580-group9-msr2027.git#main
#   docker run --rm -v group9-data:/app/data/samples group9-p01
#
# The run downloads the GitSkills sample (about 83 MB) into the named volume on first use, then runs
# lint, the tests, the analysis, a comparison with the committed results, and the spec checks.
# Nothing from the dataset is executed; the scanner reads text only.

FROM python:3.12.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg

WORKDIR /app

# Dependencies first, so editing the code does not reinstall them.
COPY docker/constraints.txt /tmp/constraints.txt
RUN pip install -r /tmp/constraints.txt

COPY . .
RUN pip install --no-deps -e . \
    && useradd --create-home --uid 1000 runner \
    && mkdir -p data/samples build \
    && chown -R runner:runner /app \
    && chmod -R u+rwX /app
# chmod: a build context copied from Windows (for example a OneDrive folder) can arrive with
# read-only folders, which would stop the sample download.

# Recorded in the check's report; pass it when building from a clone:
#   docker build --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) -t group9-p01 .
ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}

USER runner
CMD ["bash", "docker/check.sh"]
