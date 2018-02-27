env.ANSIBLE_SSH_CONTROL_PATH = "%(directory)s/%%h-%%r"
env.ANSIBLE_HOST_KEY_CHECKING = false
env.ANSIBLE_FORCE_COLOR = true
env.PAAS_SLAVE = "paas-sig-ci-slave01"
env.BFS_PB = 'paas-ci/playbooks/openshift/bfs.yml'
env.CBS_PB = 'paas-ci/playbooks/openshift/cbs.yml'
env.TARGET_BASE_NAME = 'paas7-openshift-origin'
env.TARGET_SFX_NAME = 'el7'
env.PAAS_REPO = 'https://github.com/arilivigni/paas-sig-ci'
env.VENV = env.JOB_NAME + '-' + UUID.randomUUID().toString().substring(0,5)

properties(
        [
                buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '25', daysToKeepStr: '', numToKeepStr: '50')),
                disableConcurrentBuilds(),
                parameters(
                        [
                                string(defaultValue: 'v3.10.0-alpha.0', description: 'origin version', name: 'ORIGIN_VERSION'),
                                string(defaultValue: 'openshift-ansible-3.9.0-0.53.0', description: 'openshift-ansible version', name: 'OA_VERSION'),
                                string(defaultValue: '', description: 'target in the CBS build system', name: 'BUILD_TARGET'),
                                booleanParam(defaultValue: true, description: 'build in CBS as a scratch build', name: 'SCRATCH'),
                                booleanParam(defaultValue: true, description: 'build from the master branch', name: 'BE'),
                                booleanParam(defaultValue: true, description: 'build origin', name: 'BUILD_ORIGIN'),
                                booleanParam(defaultValue: true, description: 'build openshift-ansible', name: 'BUILD_OA'),
                        ],
                ),
                pipelineTriggers([cron('H */3 * * *')]),
        ]
)


node (env.PAAS_SLAVE) {
    def currentStage = ""

    ansiColor('xterm') {
        timestamps {
            try {
                deleteDir()
                // set branch vars
                if ("${env.BE}" == "true") {
                    ORIGIN_BRANCH = 'master'
                    OA_BRANCH = 'master'
                } else {
                    ORIGIN_BRANCH = "v${env.ORIGIN_VERSION}"
                    OA_BRANCH = "${env.OA_VERSION}"
                }

                if ("${env.BE}" == "true") {
                    env.BUILD_TARGET = 'paas7-openshift-future-el7'
                }

                currentStage = 'Provision-Node'
                stage(currentStage) {
                    // Checkout this SCM
                    dir('paas-ci') {
                        checkout poll: false,
                                    scm: [$class: 'GitSCM',
                                       branches: [[name: "master"]],
                                       doGenerateSubmoduleConfigurations: false,
                                       extensions: [],
                                       submoduleCfg: [],
                                       userRemoteConfigs: [
                                               [
                                                       refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                                       url: "${env.PAAS_REPO}"
                                               ]]]
                    }
                    duffyNode(currentStage, 'get')
                }
                currentStage = 'Build-Origin-SRPM'
                stage(currentStage){
                    if ("${env.BUILD_ORIGIN}" == "true") {
                        currentBuild.displayName = "origin - ${ORIGIN_BRANCH}"
                        bfs(currentStage, 'origin')
                    } else {
                        echo "NOT Building origin"
                        currentBuild.displayName = "NOT building origin"
                    }
                }
                currentStage = 'Build-Openshift-Ansbile-SRPM'
                stage(currentStage){
                    if ("${env.BUILD_OA}" == "true") {
                        currentBuild.displayName += " : openshift-ansible - ${OA_BRANCH}"
                        bfs(currentStage, 'openshift-ansible')
                    } else {
                        echo "NOT Building openshift-ansible"
                        currentBuild.displayName += " : NOT building openshift-ansible"
                    }
                }
                currentStage = 'cbs-origin'
                stage(currentStage){
                    if ("${env.BUILD_ORIGIN}" == "true") {
                        cbs(currentStage, 'origin')
                    } else {
                        echo "NOT Building origin"
                    }
                }
                currentStage = 'cbs-openshift-ansible'
                stage(currentStage){
                    if ("${env.BUILD_OA}" == "true") {
                        cbs(currentStage, 'openshift-ansible')
                    } else {
                        echo "NOT Building openshift-ansible"
                    }
                }
            } catch (e) {
                // Set build result
                currentBuild.result = 'FAILURE'

                // Report the exception
                echo "Error: Exception from " + currentStage + ":"
                echo e.getMessage()

                // Throw the error
                throw e
            } finally {
                currentStage = 'Return-Node'
                stage(currentStage) {
                    duffyNode(currentStage, 'done')
                }
                currentBuild.description = ''
                if( fileExists("cbs_taskid_origin.groovy") ) {
                    currentBuild.description = "<a href=\"https://cbs.centos.org/koji/taskinfo?taskID=${env.CBS_TASKID_origin}\">origin_taskID = ${env.CBS_TASKID_origin}</a> :"
                }
                if( fileExists("cbs_taskid_openshift-ansible.groovy") ) {
                    currentBuild.description += ": <a href=\"https://cbs.centos.org/koji/taskinfo?taskID=${env.CBS_TASKID_openshift_ansible}\">O-A_taskID = ${env.CBS_TASKID_openshift_ansible}</a>"
                }
                // Archive our artifacts
                step([$class: 'ArtifactArchiver', allowEmptyArchive: true, artifacts: '*.log,*.txt,*.groovy', fingerprint: true])
            }
        }
    }
}


/**
 * Method to get/release Duffy node
 * @param stage - Current stage
 * @param action - get or done
 * @return
 */
def duffyNode (String stage, String action) {

    echo "Currently in stage: ${stage}"
    env.ACTION = action

    sh '''
        #!/bin/bash
        set -xeuo pipefail
    
        if [ "${ACTION}" == "get" ]; then
            cico node get
            cico inventory -c hostname -c comment -f csv --quote none 2>/dev/null | tail -1 | awk -F',' '{print $1}' > ${WORKSPACE}/duffy_host.inventory
            cico inventory -c hostname -c comment -f csv --quote none 2>/dev/null | tail -1 | awk -F',' '{print $2}' > ${WORKSPACE}/duffy_ssid.inventory
            DUFFY_HOST=$( cat ${WORKSPACE}/duffy_host.inventory )
            sed -i "s/${DUFFY_HOST}//g" ~/.ssh/known_hosts    
        else
            DUFFY_SSID=$( cat ${WORKSPACE}/duffy_ssid.inventory )
            cico node done ${DUFFY_SSID} 
        fi
    '''
}


/**
 * Method to build origin or openshift-ansible from source
 * @param stage - Current stage
 * @param project - origin or openshift-ansible
 * @return
 */
def bfs (String stage, String project) {

    echo "Currently in stage: ${stage}"
    env.PROJECT = project ?: 'origin'

    bfsCommand = "ansible-playbook -u root -vv " +
            "-i ${env.WORKSPACE}/duffy_host.inventory  " +
            "${env.WORKSPACE}/${env.BFS_PB} " +
            "-e project=${project} " +
            "-e bleeding_edge=${env.BE} " +
            "-e clean=true "

    if (env.PROJECT == 'origin') {
        bfsCommand += "-e origin_version=${env.ORIGIN_VERSION}"
    } else if (env.PROJECT == 'openshift-ansible') {
        bfsCommand += "-e oa_version=${env.OA_VERSION} " +
                "-e origin_version=${env.ORIGIN_VERSION}"
    }

    env.BFS_COMMAND = bfsCommand

    sh '''
        #!/bin/bash
        set -xeuo pipefail
    
        # see what we have in terms of inventory
        ${BFS_COMMAND}
    '''
}


/**
 * Method to build origin or openshift-ansible in cbs
 * @param stage - Current stage
 * @param project - origin or openshift-ansible
 * @return
 */

def cbs (String stage, String project) {

    echo "Currently in stage: ${stage}"
    env.PROJECT = project ?: 'origin'

    sh '''
      #!/bin/bash
      set -xeo pipefail

      if [ "$BUILD_TARGET" == "" ]; then
        SHORT_VERSION=$( echo $ORIGIN_VERSION | awk -F'.' '{print $1$2}' | sed 's/v//' )
        BUILD_TARGET="${TARGET_BASE_NAME}${SHORT_VERSION}-${TARGET_SFX_NAME}"
      fi

      # see what we have in terms of inventory
      ansible-playbook -u root -vv \
      -i $WORKSPACE/duffy_host.inventory \
      $WORKSPACE/${CBS_PB} -e "project=${PROJECT}" \
      -e "scratch=${SCRATCH}" \
      -e "bleeding_edge=${BE}" \
      -e "cbs_target=${BUILD_TARGET}"
    '''
    if( fileExists("cbs_taskid_${env.PROJECT}.groovy") ) {
        load("cbs_taskid_${env.PROJECT}.groovy")
    }
}
