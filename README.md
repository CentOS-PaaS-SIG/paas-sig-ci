# Continuous Integration for the CentOS PaaS SIG

This repository is designed for the tooling of Continuous Integration tests for
the CentOS Platform as a Service (PaaS) Special Interest Group (SIG).

The repository is broken up into several different components, as described below.
For the most part, this repository generally uses
[linch-pin*](https://github.com/CentOS-PaaS-SIG/linch-pin)
to provision hosts, calling the
[duffy-ansible-module](https://github.com/CentOS-PaaS-SIG/duffy-ansible-module),
which provisions [duffy](https://wiki.centos.org/QaWiki/CI/Duffy) hosts.

The paas-sig-ci repository is structured as such:

    pass-sig-ci/
    ├── config
    │   ├── inv_layouts
    │   └── topologies
    ├── jjb
    │   ├── duffy
    │   └── openshift
    └── playbooks
        ├── duffy
        └── openshift

## playbooks

The ansible playbooks needed to run continuous integration for a particular
application. At the moment, only openshift and duffy are available.

## jjb

The jenkins jobs which first provision a cluster (usually using linch-pin),
then use the above playbooks structure to run plays/tasks provided in a
particular order. Currently, the only playbooks are openshift and duffy.

## config

The configurations are broken up into two components, topologies and
inv_layouts (or inventory layouts).

### topologies

In the linch-pin tooling, there is the concept of a topology. This describes
a set of hosts on a particular set of clouds which to provision. This could
include tooling for networking, disk, etc. depending on the cloud provider.
Within CentOS CI, duffy is generally the only cloud provider used. 

### inv_layouts (Inventory Layouts)

When provisioning systems, it's common to not know the host ip addresses,
hostnames, or other facts about a system. However, many cluster technologies,
openshift for example, require knowledge about the hosts beyond knowing that
there are 3 nodes available. Linch-pin provides a filter after provisioning
that can generate static (for now) inventories for ansible. In this way,
the cluster can be provisioned, then an inventory is created to allow
follow-up playbooks to continue the configuration of a cluster.

To do this, linch-pin must know how to generate said inventory. Linch-pin
generates outputs from a cloud provider, which can then be mapped to the
inventory layout. After mapping, a set of inventory files are generated
in a predefined directory. Using the inventory directory, the cluster
tools can then configure a particular cluster structure dynamically.

## Notes

\* - Linch-pin is written as a set of ansible playbooks and configurations to
provision hosts across many different cloud providers at the same time.
It can also provide inventory files based upon predefined layouts for
provisioning large dynamic clusters. A good example is openshift origin
using the [openshift-ansible](https://github.com/openshift/openshift-ansible)
build your own (byo) playbooks.

