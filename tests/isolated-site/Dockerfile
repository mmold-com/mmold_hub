FROM frappe/erpnext@sha256:b5fc6acc237dbd2e9afc7ebe484fe01889c40d01c69a057f9494f1358e9eda34

USER root

# Debian 12 package version is pinned; it supplies Noto Sans/Serif CJK TC.
RUN sed -i '/^URIs: http:\/\/deb.debian.org\/debian$/s|http://deb.debian.org/debian|http://ftp.tw.debian.org/debian|' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends fonts-noto-cjk=1:20220127+repack1-1 \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/frappe/frappe-bench/apps/mmold_hub

COPY --chown=frappe:frappe pyproject.toml MANIFEST.in README.md license.txt \
    /home/frappe/frappe-bench/apps/mmold_hub/
COPY --chown=frappe:frappe mmold_hub \
    /home/frappe/frappe-bench/apps/mmold_hub/mmold_hub
COPY --chown=frappe:frappe reference_apps/print_designer \
    /home/frappe/frappe-bench/apps/print_designer
COPY --chown=frappe:frappe tests/isolated-site/python-dependencies.lock \
    /home/frappe/frappe-bench/python-dependencies.lock

USER frappe
WORKDIR /home/frappe/frappe-bench

# The upstream image has a separate immutable assets directory, while the
# isolated stack mounts the whole sites directory as a volume. Point
# sites/assets at the immutable directory before building so app bundles and
# assets.json survive that volume mount and are served by the frontend.
USER root
RUN rm -rf /home/frappe/frappe-bench/sites/assets \
    && ln -s /home/frappe/frappe-bench/assets /home/frappe/frappe-bench/sites/assets \
    && chown -h frappe:frappe /home/frappe/frappe-bench/sites/assets
USER frappe

# Frappe discovers App packages from the Bench apps directory. Build once so
# this disposable image exercises the same asset discovery path as deployment.
RUN ./env/bin/pip install --no-deps -r python-dependencies.lock \
    && ./env/bin/pip install --no-deps --editable apps/mmold_hub apps/print_designer \
    && yarn --cwd apps/print_designer install --frozen-lockfile --non-interactive \
    && printf '%s\n' frappe erpnext mmold_hub print_designer > sites/apps.txt \
    && bench build --app mmold_hub \
    && bench build --app print_designer

# Frontend nginx serves /assets from the immutable Bench assets directory.
USER root
RUN ln -sfn /home/frappe/frappe-bench/apps/mmold_hub/mmold_hub/public \
    /home/frappe/frappe-bench/assets/mmold_hub
USER frappe
