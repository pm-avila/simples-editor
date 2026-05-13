FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        qemu-user-static \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 sandbox \
    && useradd --uid 10001 --gid sandbox --create-home --shell /usr/sbin/nologin sandbox \
    && mkdir -p /sandbox \
    && chown -R sandbox:sandbox /sandbox

WORKDIR /sandbox
USER sandbox

CMD ["/bin/sh"]
