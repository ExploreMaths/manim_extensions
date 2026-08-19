# ── Stage 1: builder ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update -qq \
    && apt-get install --no-install-recommends -y \
        wget \
        tar \
        gzip \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY binder/texlive-profile.txt /tmp/
ENV PATH=/usr/local/texlive/bin/armhf-linux:/usr/local/texlive/bin/aarch64-linux:/usr/local/texlive/bin/x86_64-linux:$PATH
RUN wget -O /tmp/install-tl-unx.tar.gz https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
    && mkdir /tmp/install-tl \
    && tar -xzf /tmp/install-tl-unx.tar.gz -C /tmp/install-tl --strip-components=1 \
    && /tmp/install-tl/install-tl --profile=/tmp/texlive-profile.txt \
    && tlmgr install \
        amsmath babel-english cbfonts-fd cm-super count1to doublestroke dvisvgm everysel \
        fontspec frcursive fundus-calligra gnu-freefont jknapltx latex-bin \
        mathastext microtype multitoc physics prelim2e preview ragged2e relsize rsfs \
        setspace standalone tipa wasy wasysym xcolor xetex xkeyval \
    && rm -rf /tmp/install-tl /tmp/install-tl-unx.tar.gz

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim

RUN apt-get update -qq \
    && apt-get install --no-install-recommends -y \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libpangoft2-1.0-0 \
        libffi-dev \
        libegl1 \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxrender1 \
        libxext6 \
        libxi6 \
        libxrandr2 \
        chipmunk7 \
        libgomp1 \
        ghostscript \
        fonts-noto-core \
        fontconfig \
        librsvg2-utils \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# Copy TeX Live from builder
ENV PATH=/usr/local/texlive/bin/armhf-linux:/usr/local/texlive/bin/aarch64-linux:/usr/local/texlive/bin/x86_64-linux:$PATH
COPY --from=builder /usr/local/texlive /usr/local/texlive

# Create virtualenv and install Python deps
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install manim first (biggest dep), then other deps
RUN pip install --no-cache-dir \
        manim>=0.19.1 \
        notebook \
        pymunk \
        moderngl \
        moderngl-window \
        opencv-python-headless

# Install manim_extensions from repo, then replace opencv-python with headless version
COPY . /opt/manim_extensions
WORKDIR /opt/manim_extensions
RUN pip install --no-cache-dir . \
    && pip install --no-cache-dir --force-reinstall --no-deps opencv-python-headless

ARG NB_USER=manimuser
ARG NB_UID=1000
ENV USER=${NB_USER}
ENV NB_UID=${NB_UID}
ENV HOME=/manim

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

WORKDIR ${HOME}
RUN chown -R ${NB_USER}:${NB_USER} ${HOME} && chmod 777 ${HOME}
USER ${NB_USER}

COPY binder/postBuild /usr/local/bin/postBuild
COPY binder/start-notebook.sh /usr/local/bin/start-notebook.sh
USER root && chmod +x /usr/local/bin/postBuild /usr/local/bin/start-notebook.sh && USER ${NB_USER}

ENTRYPOINT ["/usr/local/bin/start-notebook.sh"]
CMD ["jupyter", "notebook", "--ip", "0.0.0.0", "--port", "8888"]