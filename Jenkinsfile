env.ANSIBLE_SSH_CONTROL_PATH = "%(directory)s/%%h-%%r"
env.ANSIBLE_HOST_KEY_CHECKING = false
env.ANSIBLE_FORCE_COLOR = true
env.PAAS_SLAVE = "paas-sig-ci-slave01"
env.TOPOLOGY = "duffy_3node_cluster"
env.INVENTORY_LAYOUT_FILE = "openshift-3node-inventory.yml"
env.lpsha1 = "a950a170e0694f2b596431eb2e54f1ec38b873d1"
env.PREP_PB = 'paas-ci/playbooks/openshift/setup.yml'
env.BFS_PB = 'paas-ci/playbooks/openshift/bfs.yml'
env.DEPLOY_AOSI_PB = 'paas-ci/playbooks/openshift/deploy_aosi.yml'
env.RUN_E2E_PB = 'paas-ci/playbooks/openshift/run_e2e_tests.yml'
env.CBS_PB = 'paas-ci/playbooks/openshift/cbs.yml'

properties(
        [
                buildDiscarder(logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '25', daysToKeepStr: '', numToKeepStr: '50')),
                disableConcurrentBuilds(),
                parameters(
                        [
                                string(defaultValue: '3.7.0-alpha.1', description: 'origin version', name: 'ORIGIN_VERSION'),
                                string(defaultValue: '3.7', description: 'openshift-ansible version', name: 'OA_VERSION'),
                                booleanParam(defaultValue: true, description: 'build in CBS as a scratch build', name: 'SCRATCH'),
                                booleanParam(defaultValue: true, description: 'build from the master branch', name: 'BE'),
                        ],
                pipelineTriggers([pollSCM('H */3 * * *')])
                ),

        ]
)

if (env.BE) {
    ORIGIN_BRANCH = 'master'
} else {
    ORIGIN_BRANCH = "refs/tags/v${env.ORIGIN_VERSION}"
    OA_BRANCH = "refs/tags/v${env.OA_VERSION}"
}

node (env.PAAS_SLAVE) {
    def currentStage = ""

    ansiColor('xterm') {
        timestamps {
            try {
                deleteDir()

                // Set our current stage value
                currentStage = 'Provision-Cluster'
                stage(currentStage) {
                    // SCM Checkout for origin and ansbile
                    dir( 'origin') {
                        checkout([$class                           : 'GitSCM', branches: [[name: "${ORIGIN_BRANCH}"]],
                                  doGenerateSubmoduleConfigurations: false,
                                  extensions                       : [],
                                  submoduleCfg                     : [],
                                  userRemoteConfigs                : [
                                          [refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                           url    : 'https://github.com/openshift/origin'
                                          ]
                                  ]])
                    }
                    dir('openshift-ansible') {
                        checkout([$class                           : 'GitSCM', branches: [[name: "${OA_BRANCH}"]],
                                  doGenerateSubmoduleConfigurations: false,
                                  extensions                       : [],
                                  submoduleCfg                     : [],
                                  userRemoteConfigs                : [
                                          [refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                           url    : 'https://github.com/openshift/openshift_ansible'
                                          ]
                                  ]])
                    }
                    dir('paas-ci') {
                        checkout poll: false([$class                           : 'GitSCM', branches: [[name: "master"]],
                                              doGenerateSubmoduleConfigurations: false,
                                              extensions                       : [],
                                              submoduleCfg                     : [],
                                              userRemoteConfigs                : [
                                                      [refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                                       url    : 'https://github.com/CentOS-PaaS-SIG/paas-sig-ci'
                                                      ]
                                              ]])
                    }
                    provisionDuffyLinchPin(currentStage)
                }
                currentStage = 'Prep-Cluster'
                stage(currentStage) {
                    prepCluster(currentStage)
                }
                currentStage = 'Build-Origin'
                stage(currentStage){
                    bfs(currentStage, 'origin')
                }
                currentStage = 'Build-Openshift-Ansbile'
                stage(currentStage){
                    bfs(currentStage, 'openshift-ansible')
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
                    cbs(currentStage, 'origin')
                }
                currentStage = 'cbs-openshift-ansible'
                stage(currentStage){
                    cbs(currentStage, 'openshift-ansible')
                }
                currentStage = 'Teardown-Cluster'
                teardownDuffyLinchPin(currentStage)
            } catch (e) {
                // Set build result
                currentBuild.result = 'FAILURE'

                // Report the exception
                echo "Error: Exception from " + currentStage + ":"
                echo e.getMessage()

                // Throw the error
                throw e
            } finally {

            }
        }
    }

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
        checkout poll: false([$class                           : 'GitSCM', branches: [[name: "${lpsha1}"]],
                              doGenerateSubmoduleConfigurations: false,
                              extensions                       : [],
                              submoduleCfg                     : [],
                              userRemoteConfigs                : [
                                      [refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                       url    : 'https://github.com/CentOS-PaaS-SIG/linch-pin'
                                      ]
                              ]])
    }
    dir('duffy-ansible-module') {
        checkout poll: false([$class                           : 'GitSCM', branches: [[name: "master"]],
                              doGenerateSubmoduleConfigurations: false,
                              extensions                       : [],
                              submoduleCfg                     : [],
                              userRemoteConfigs                : [
                                      [refspec: '+refs/tags/*:refs/remotes/origin/tags/* +refs/heads/master:refs/remotes/origin/master',
                                       url    : 'https://github.com/CentOS-PaaS-SIG/duffy-ansible-module'
                                      ]
                              ]])
    }

    sh '''
        #!/bin/bash
        set -xeuo pipefail

        UUID=$( uuidgen | cut -d '-' -f1 )
        virtualenv ${JOB_NAME}-${UUID}
        source ${JOB_NAME}-${UUID}/bin/activate
        pip install --upgrade ansible>=2.1.0
        pip install jsonschema functools32

        # create ansible.cfg
        echo "[defaults]" > ansible.cfg
        echo "remote_user = root" >> ansible.cfg
        echo "library  = $WORKSPACE/linch-pin/library:$WORKSPACE/duffy-ansible-module/library" >> ansible.cfg        
        
        mkdir -p $WORKSPACE/inventory

        # provision cluster
        ansible-playbook {provision-pb} -u root -vv \
        -e "topology=$WORKSPACE/paas-ci/config/topologies/${TOPOLOGY}.yml" \
        -e "inventory_layout_file=$WORKSPACE/paas-ci/config/inv_layouts/${INVENTORY_LAYOUT_FILE}" \
        -e "inventory_outputs_path=$WORKSPACE/inventory" -e "state=${ACTION}"
        
        deactivate
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
      -i $WORKSPACE/inventory/${TOPOLOGY}.inventory \
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

    env.bfsCommand = "ansible-playbook -u root -vv " +
            "-i ${env.WORKSPACE}/inventory/${env.TOPOLOGY}.inventory " +
            "${env.WORKSPACE}/${env.BFS_PB} -e repo_from_source=true" +
            "-e project=${project} " +
            "-e bleeding_edge=${env.BE} "

    if (project == 'origin') {
        bfsCommand += "-e version=${env.ORIGIN_VERSION}"
    } else if (project == 'openshift-ansible') {
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
      set -xeuo pipefail

      # see what we have in terms of inventory
      ansible-playbook -u root -vv \
      -i $WORKSPACE/inventory/${TOPOLOGY}.inventory \
      $WORKSPACE/${CBS_PB} -e "project=${PROJECT}" \
      -e "scratch=${SCRATCH}" \
      -e "bleeding_edge=${BE}"
    '''
}
