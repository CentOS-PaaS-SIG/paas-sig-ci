env.ANSIBLE_SSH_CONTROL_PATH = "%(directory)s/%%h-%%r"
env.ANSIBLE_HOST_KEY_CHECKING = false
env.ANSIBLE_FORCE_COLOR = true
env.PAAS_SLAVE = "paas-sig-ci-slave01"
env.TOPOLOGY = "duffy_3node_cluster"
env.TOPOLOGY_PATH = "paas-ci/config/topologies/" + env.TOPOLOGY + ".yml"
env.INVENTORY_LAYOUT_FILE = "paas-ci/config/inv_layouts/openshift-3node-inventory.yml"
env.lpsha1 = "a950a170e0694f2b596431eb2e54f1ec38b873d1"
env.PROVISION_PB = "linch-pin/provision/site.yml"
env.PREP_PB = 'paas-ci/playbooks/openshift/setup.yml'
env.BFS_PB = 'paas-ci/playbooks/openshift/bfs.yml'
env.DEPLOY_AOSI_PB = 'paas-ci/playbooks/openshift/deploy_aosi.yml'
env.RUN_E2E_PB = 'paas-ci/playbooks/openshift/run_e2e_tests.yml'
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
                                string(defaultValue: '3.9.0-alpha.4', description: 'origin version', name: 'ORIGIN_VERSION'),
                                string(defaultValue: '3.9', description: 'openshift-ansible version', name: 'OA_VERSION'),
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

                def pypackages = ['ansible==2.1.0', 'jsonschema', 'functools32']
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
//                    if( !(fileExists("${env.VENV}")) ) {
//                        setupVenv(pypackages)
//                    }
//                    provisionDuffyLinchPin(currentStage)
                }
//                currentStage = 'Prep-Cluster'
//                stage(currentStage) {
//                    prepCluster(currentStage)
//                }
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
//                currentStage = 'deploy-openshift-cluster'
//                stage(currentStage){
//                    createAosi()
//                }
//                currentStage = 'run-e2e-conformance'
//                stage(currentStage){
//                    runE2eTests()
//                }
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
//                    if( !(fileExists("${env.VENV}")) ) {
//                        setupVenv(pypackages)
//                    }
//                    teardownDuffyLinchPin(currentStage)
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
 * Method for setting up Virtualenv
 * @param packages List of packages
 * @return
 */
def setupVenv(List packages) {
    env.PYPACKAGES = packages.join(' ')
    sh '''
        #!/bin/bash
        set -xeo pipefail
        
        virtualenv ${VENV}
        source ${VENV}/bin/activate
        pip install --upgrade pip setuptools
        pip install ${PYPACKAGES}
        cp -r /usr/lib64/python2.7/site-packages/selinux $VIRTUAL_ENV/lib/python2.7/site-packages
    '''
}

/**
 * Wrapper function to provision duffy resources using LinchPin
 * @param stage Current stage
 * @return
 */
def provisionDuffyLinchPin (String stage) {
    duffyLpOps = [stage:stage, action:'present']
    duffyLinchPin(duffyLpOps)
}


/**
 * Wrapper function to teardown duffy resources using LinchPin
 * @param stage Current stage
 * @return
 */
def teardownDuffyLinchPin (String stage) {
    duffyLpOps = [stage:stage, action:'absent']
    duffyLinchPin(duffyLpOps)
}

/**
 * Method for provisioning and tearing down duffy resources using https://github.com/CentOS-PaaS-SIG/linchpin
 * @param lpMap Default lpMap[stage:'duffyLinchPin-stage',
 *           action:'present',
 *           repoUrl:'https://github.com/CentOS-PaaS-SIG/linchpin']
 * @return
 */
def duffyLinchPin (Map lpMap) {

    lpMap.stage = "${lpMap.containsKey('stage') ? lpMap.stage : 'duffyLinchPin-stage'}"
    env.ACTION = "${lpMap.containsKey('action') ? lpMap.action : 'present'}"
    echo "Currently in stage: ${lpMap.stage} and make sure resource is ${env.ACTION}"


    dir('linch-pin') {
        checkout poll: false,
                scm: [$class: 'GitSCM',
                      branches: [[name: "${lpsha1}"]],
                      doGenerateSubmoduleConfigurations: false,
                      extensions: [],
                      submoduleCfg: [],
                      userRemoteConfigs: [
                              [
                                      refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                      url: 'https://github.com/CentOS-PaaS-SIG/linch-pin'
                              ]]]
    }
    dir('duffy-ansible-module') {
        checkout poll: false,
                scm: [$class: 'GitSCM',
                      branches: [[name: 'master']],
                      doGenerateSubmoduleConfigurations: false,
                      extensions: [],
                      submoduleCfg: [],
                      userRemoteConfigs: [
                              [
                                      refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                      url: 'https://github.com/CentOS-PaaS-SIG/duffy-ansible-module'
                              ]]]
    }

    sh '''
        #!/bin/bash
        set -xeo pipefail

        source ${VENV}/bin/activate

        # create ansible.cfg
        echo "[defaults]" > ansible.cfg
        echo "remote_user = root" >> ansible.cfg
        echo "library  = $WORKSPACE/linch-pin/library:$WORKSPACE/duffy-ansible-module/library" >> ansible.cfg        
        
        mkdir -p $WORKSPACE/inventory

        # provision cluster
        ansible-playbook ${PROVISION_PB} -u root -vv \
        -e "topology=$WORKSPACE/${TOPOLOGY_PATH}" \
        -e "inventory_layout_file=$WORKSPACE/${INVENTORY_LAYOUT_FILE}" \
        -e "inventory_outputs_path=$WORKSPACE/inventory" -e "state=${ACTION}"
        
        deactivate
    '''
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
 * Method to prep and Openshift cluster
 * @param stage - Current stage
 * @return
 */
def prepCluster (String stage) {

    echo "Currently in stage: ${stage}"

    sh '''
      #!/bin/bash
      set -xeuo pipefail

      # see what we have in terms of inventory
      ansible-playbook -u root -vv \
      -i $WORKSPACE/host.inventory \
      $WORKSPACE/${PREP_PB} -e "repo_from_source=true"
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
            "-i ${env.WORKSPACE}/host.inventory  " +
            "${env.WORKSPACE}/${env.BFS_PB} " +
            "-e project=${project} " +
            "-e bleeding_edge=${env.BE} "

    if (env.PROJECT == 'origin') {
        bfsCommand += "-e version=${env.ORIGIN_VERSION}"
    } else if (env.PROJECT == 'openshift-ansible') {
        bfsCommand += "-e version=${env.OA_VERSION} " +
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
 * Method to create an Openshift cluster
 * @return
 */
def createAosi () {

    sh '''
      #!/bin/bash
      set -xeuo pipefail

      # see what we have in terms of inventory
      ansible-playbook -u root -vv \
      -i $WORKSPACE/inventory/${TOPOLOGY}.inventory \
      $WORKSPACE/${DEPLOY_AOSI_PB} \
      -e "version=${ORIGIN_VERSION}"
    '''
}

/**
 * Method to run e2e tests
 * @return
 */
def runE2eTests () {

    sh '''
      #!/bin/bash
      set -xeuo pipefail

      # see what we have in terms of inventory
      ansible-playbook -u root -vv \
      -i $WORKSPACE/inventory/${TOPOLOGY}.inventory \
      $WORKSPACE/${RUN_E2E_PB}
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
        SHORT_VERSION=$( echo $ORIGIN_VERSION | awk -F'.' '{print $1$2}' )
        BUILD_TARGET="${TARGET_BASE_NAME}${SHORT_VERSION}-${TARGET_SFX_NAME}"
      fi

      # see what we have in terms of inventory
      ansible-playbook -u root -vv \
      -i $WORKSPACE/host.inventory \
      $WORKSPACE/${CBS_PB} -e "project=${PROJECT}" \
      -e "scratch=${SCRATCH}" \
      -e "bleeding_edge=${BE}" \
      -e "cbs_target=${BUILD_TARGET}"
    '''
    if( fileExists("cbs_taskid_${env.PROJECT}.groovy") ) {
        load("cbs_taskid_${env.PROJECT}.groovy")
    }
}
