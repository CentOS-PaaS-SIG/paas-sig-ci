# Continuous Integration for the CentOS PaaS SIG

This repository is designed for the tooling of Continuous Integration of
the CentOS Platform as a Service (PaaS) Special Interest Group (SIG).

## Project Structure
The paas-sig-ci repository is structured as such:

    pass-sig-ci/
    ├── archived (old way of integration)
    ├── Jenkinsfile
    ├── JenkinsfileTrigger
    ├── playbooks
    │   └── openshift
    │       ├── bfs.yml
    │       ├── cbs.yml
    │       ├── group_vars
    │       │   └── all
    │       │       └── global.yml
    │       └── roles
    │           ├── bfs
    │           │   ├── defaults
    │           │   │   └── main.yml
    │           │   ├── meta
    │           │   │   └── main.yml
    │           │   └── tasks
    │           │       ├── build_openshift-ansible_srpm.yml
    │           │       ├── build_openshift_srpm.yml
    │           │       ├── cleanup_bfs.yml
    │           │       ├── clone_from_github.yml
    │           │       └── main.yml
    │           ├── cbs
    │           │   ├── defaults
    │           │   │   └── main.yml
    │           │   ├── meta
    │           │   │   └── main.yml
    │           │   └── tasks
    │           │       ├── cbs_build_srpms.yml
    │           │       ├── copy_cbs_certs.yml
    │           │       ├── install_cbs_pkgs.yml
    │           │       └── main.yml
    │           └── common
    │               ├── defaults
    │               │   └── main.yml
    │               ├── handlers
    │               │   └── main.yml
    │               ├── tasks
    │               │   ├── enable_centos_extras.yml
    │               │   ├── enable_epel.yml
    │               │   ├── install_required_pkgs.yml
    │               │   └── main.yml
    │               └── templates
    │                   ├── centos7-extras-repo.j2
    │                   └── epel-repo.j2
    └── README.md
        

## playbooks

These playbooks build source RPMs for Openshift origin and openshift-ansible
from a known good release tag in those repos.  

### bfs role
The bfs role creates the source RPM for each project origin and openshift-ansible

### cbs role
The cbs role takes the source RPM and builds it against the appropriate build target
in CentOS Koji (CentOS Build System - CBS).

## Jenkins 2.0 Pipelines

### JenkinsTrigger
This is a trigger pipeline that checks the latest tag for Openshift origin and
openshift-ansible.  If there is a new one then it triggers the Jenkinsfile below
to build an official version of origin and openshift-ansible against the appropriate
target.
 
### Jenkinsfile
This is a pipeline to build the source RPMs for both being triggered from the
JenkinsTrigger to build official releases of origin and openshift-ansible.  
Otherwise it builds every hour of the master of both origin and openshift-ansible
to the paas7-openshift-future-el7 target.

## Notes

Everything in the archived directory is what used to be used to build, test and deliver.
Since Openshift already creates clusters and runs e2e conformance tests it would be redundant<br>
do it again so now we build source RPMs from the release tag and create an official build
