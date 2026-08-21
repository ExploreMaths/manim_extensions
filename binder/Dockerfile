FROM manimcommunity/manim:v0.20.1

USER root

RUN apt-get update -qq \
    && apt-get install --no-install-recommends -y xvfb mesa-utils libgl1-mesa-dri libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir notebook jupyterlab ipykernel

ARG NB_USER=manimuser
ARG NB_UID=1000
ENV USER=${NB_USER}
ENV NB_UID=${NB_UID}
ENV HOME=/manim

WORKDIR ${HOME}
COPY --chown=${NB_USER}:${NB_USER} . ${HOME}
RUN pip install --no-cache-dir --user ${HOME}

COPY binder/postBuild /usr/local/bin/postBuild
COPY binder/start-notebook.sh /usr/local/bin/start-notebook.sh
RUN chmod +x /usr/local/bin/postBuild /usr/local/bin/start-notebook.sh

USER ${NB_USER}

ENTRYPOINT ["/usr/local/bin/start-notebook.sh"]
CMD ["jupyter", "notebook", "--ip", "0.0.0.0", "--port", "8888"]