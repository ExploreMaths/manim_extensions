FROM manimcommunity/manim:v0.20.1

USER root
RUN pip install notebook

ARG NB_USER=manimuser
USER ${NB_USER}

COPY --chown=manimuser:manimuser . /manim
RUN pip install --user /manim
