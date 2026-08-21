FROM manimcommunity/manim:v0.20.1

USER root

RUN apt-get update -qq \
    && apt-get install --no-install-recommends -y xvfb libgl1-mesa-dri libgl1-mesa-glx libegl1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir notebook jupyterlab ipykernel

ARG NB_USER=manimuser
ARG NB_UID=1000

RUN if ! id -u "${NB_USER}" >/dev/null 2>&1; then \
      if id -u "${NB_UID}" >/dev/null 2>&1; then \
        existing=$(id -un "${NB_UID}"); \
        usermod -l "${NB_USER}" "${existing}"; \
        groupmod -n "${NB_USER}" "${existing}"; \
      else \
        useradd -m -s /bin/bash -N -u "${NB_UID}" "${NB_USER}"; \
      fi; \
    fi

COPY --chown=${NB_USER}:${NB_USER} . /manim

RUN pip install --no-cache-dir /manim

USER ${NB_USER}

CMD ["xvfb-run", "--auto-servernum", "jupyter", "notebook", "--ip", "0.0.0.0", "--port", "8888"]