# Pinned AMD64 build tools; the official ERPNext runtime image intentionally
# does not include Node.js or Yarn.
FROM node@sha256:5cbc7caba8c2c0f0bca675d1b61b9f2857e1cf1853c6164ee9dd409501a936e7 AS node-tools

# MMold Hub Production application image for the confirmed QNAP amd64 target.
FROM frappe/erpnext@sha256:9ed12ab3e685e896637aa3598dd9acc653b84db9e00b59520ba7960dec35a450

COPY --from=node-tools /usr/local/bin/node /usr/local/bin/node
COPY --from=node-tools /usr/local/bin/corepack /usr/local/bin/corepack
COPY --from=node-tools /usr/local/lib/node_modules/corepack /usr/local/lib/node_modules/corepack

USER root

RUN corepack enable

# Pin Debian package metadata to the snapshot date recorded by the official
# amd64 base image. Fetch the immutable package from Debian CDN and verify it
# against the SHA256 in the signed Snapshot Packages index.
RUN printf '%s\n' \
      'Types: deb' \
      'URIs: https://snapshot.debian.org/archive/debian/20260918T000000Z' \
      'Suites: bookworm bookworm-updates' \
      'Components: main' \
      'Check-Valid-Until: no' \
      'Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg' \
      '' \
      'Types: deb' \
      'URIs: https://snapshot.debian.org/archive/debian-security/20260918T000000Z' \
      'Suites: bookworm-security' \
      'Components: main' \
      'Check-Valid-Until: no' \
      'Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg' \
      > /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && curl -fL --retry 3 \
      https://deb.debian.org/debian/pool/main/f/fonts-noto-cjk/fonts-noto-cjk_20220127+repack1-1_all.deb \
      -o /tmp/fonts-noto-cjk.deb \
    && echo '4a2515eb6db3978b897fef9709ed0d2b1f4c6c4df4d83d6c4ef65f71f1b1f502  /tmp/fonts-noto-cjk.deb' | sha256sum -c - \
    && dpkg -i /tmp/fonts-noto-cjk.deb \
    && fc-cache -f \
    && rm -f /tmp/fonts-noto-cjk.deb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/frappe/frappe-bench

COPY --chown=frappe:frappe pyproject.toml MANIFEST.in README.md license.txt /home/frappe/frappe-bench/apps/mmold_hub/
COPY --chown=frappe:frappe mmold_hub /home/frappe/frappe-bench/apps/mmold_hub/mmold_hub
COPY --chown=frappe:frappe reference_apps/print_designer /home/frappe/frappe-bench/apps/print_designer
COPY --chown=frappe:frappe docker/production/python-dependencies.lock /home/frappe/frappe-bench/python-dependencies.lock

# Keep generated bundles in the immutable Bench assets directory; the
# upstream entrypoint links this directory into the runtime sites volume.
RUN rm -rf /home/frappe/frappe-bench/sites/assets \
    && ln -s /home/frappe/frappe-bench/assets /home/frappe/frappe-bench/sites/assets \
    && chown -h frappe:frappe /home/frappe/frappe-bench/sites/assets

USER frappe
ENV COREPACK_HOME=/home/frappe/.cache/node/corepack

# Python dependencies and Print Designer frontend dependencies are installed
# from checked-in lockfiles. PDF on Submit is intentionally not copied or installed.
RUN ./env/bin/pip install --no-deps -r python-dependencies.lock \
    && node --version | grep -Fx 'v24.21.0' \
    && corepack prepare yarn@1.22.22 --activate \
    && yarn --version | grep -Fx '1.22.22' \
    && ./env/bin/pip install --no-deps --editable apps/mmold_hub apps/print_designer \
    && yarn --cwd apps/print_designer install --frozen-lockfile --non-interactive \
    && printf '%s\n' frappe erpnext mmold_hub print_designer > sites/apps.txt \
    && bench build --app mmold_hub \
    && bench build --app print_designer

USER root
RUN ln -sfn /home/frappe/frappe-bench/apps/mmold_hub/mmold_hub/public /home/frappe/frappe-bench/assets/mmold_hub \
    && mkdir -p /home/frappe/frappe-bench/chromium/chrome-linux \
    && ln -sfn /usr/bin/chromium-headless-shell /home/frappe/frappe-bench/chromium/chrome-linux/headless_shell \
    && chown -R frappe:frappe /home/frappe/frappe-bench/chromium \
    && test -x /home/frappe/frappe-bench/chromium/chrome-linux/headless_shell \
    && command -v chromium-headless-shell \
    && chromium-headless-shell --version | grep -Fx 'Chromium 154.0.8037.57'

USER frappe
