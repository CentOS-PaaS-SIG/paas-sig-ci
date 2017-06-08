FROM registry.fedoraproject.org/fedora:25
RUN dnf update -y
RUN dnf -y install \
    git \
    python-pip \
    libselinux-python \
    python-devel \
    python2-dnf \
    libffi-devel \
    redhat-rpm-config \
    openssl-devel
RUN dnf -y groupinstall "Development Tools"
RUN pip install ansible==2.2.0
RUN git clone https://github.com/samvarankashyap/paas-sig-ci
WORKDIR "/paas-sig-ci"
RUN echo "$PWD"
