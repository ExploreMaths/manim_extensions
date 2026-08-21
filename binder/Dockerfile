FROM manimcommunity/manim:v0.20.1

USER root

RUN pip install --no-cache-dir notebook jupyterlab ipykernel

ARG NB_USER=manimuser
ARG NB_UID=1000
ENV USER=${NB_USER}
ENV NB_UID=${NB_UID}
ENV HOME=/manim

WORKDIR ${HOME}
COPY --chown=${NB_USER}:${NB_USER} . ${HOME}
RUN pip install --no-cache-dir --user ${HOME}

USER ${NB_USER}

CMD ["jupyter", "notebook", "--ip", "0.0.0.0", "--port", "8888"]