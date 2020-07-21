import sys
from run_process import main
from experiment import Experiment, ExperimentMatrix
from multiprocessing import Pool, Manager
from subprocess import Popen
from dir_structure import DirStructure
from bug_miner_reproducer import BugMinerReproducer
import os
from multiprocessing import Pool, Manager
from subprocess import Popen
from functools import partial
DIR_BASE_PATH = r"component_importance_data"
NUM_PROCCESSES = 1

def run_process(cmd_args):
    print "Running", cmd_args
    proc = Popen([sys.executable] + cmd_args)
    proc.communicate()

def exec_file(file_name, cmds):
    run_process([file_name] + cmds)

def exec_do_all(commit, dir_path, project_name):
    exec_file("bug_miner_reproducer.py", [dir_path, project_name, commit])

def exec_training_set(commit, dir_path, project_name):
    exec_file("bug_miner_reproducer.py", [dir_path, project_name, commit, 'training'])

def exec_experiment(commit, dir_path):
    exec_file("experiment.py", [dir_path, commit])


def experiment_execute(project, dir_path):
    ExperimentMatrix.experiment_classifiers(DirId(DirStructure(dir_path), project))


def execute(func, iter, num_processes=NUM_PROCCESSES):
    p = Pool(num_processes)
    p.map(func, iter)
    p.close()


def full_experiment(bug_miner_project_name, dir_base_path=DIR_BASE_PATH, num_processes=NUM_PROCCESSES):
    dir_path = os.path.join(dir_base_path, bug_miner_project_name)
    projects = BugMinerReproducer.read_bug_miner_csv(dir_path, bug_miner_project_name)
    git_path, jira_path = list(filter(lambda x: os.path.basename(x[1]) == bug_miner_project_name, projects_names.values()))[0]
    os.system("git clone {0} repo\\{1}".format(git_path, bug_miner_project_name))
    execute(partial(exec_do_all, dir_path=dir_path, project_name=bug_miner_project_name), projects.keys(), num_processes)
    execute(partial(exec_training_set, dir_path=dir_path, project_name=bug_miner_project_name), projects.keys(), num_processes)
    execute(partial(exec_experiment, dir_path=dir_path), projects.keys(), num_processes)
    Experiment(DirStructure(dir_path)).experiment()


projects_names = {'distributedlog': ('https://github.com/apache/distributedlog',
  'http:\\issues.apache.org\\jira\\projects\\DL'),
 'maven-indexer': ('https://github.com/apache/maven-indexer',
  'http:\\issues.apache.org\\jira\\projects\\MINDEXER'),
 'rampart': ('https://github.com/apache/rampart',
  'http:\\issues.apache.org\\jira\\projects\\RAMPART'),
 'commons-functor': ('https://github.com/apache/commons-functor',
  'http:\\issues.apache.org\\jira\\projects\\FUNCTOR'),
 'velocity-tools': ('https://github.com/apache/velocity-tools',
  'http:\\issues.apache.org\\jira\\projects\\VELTOOLS'),
 'commons-fileupload': ('https://github.com/apache/commons-fileupload',
  'http:\\issues.apache.org\\jira\\projects\\FILEUPLOAD'),
 'crunch': ('https://github.com/apache/crunch',
  'http:\\issues.apache.org\\jira\\projects\\CRUNCH'),
 'johnzon': ('https://github.com/apache/johnzon',
  'http:\\issues.apache.org\\jira\\projects\\JOHNZON'),
 'joshua': ('https://github.com/apache/joshua',
  'http:\\issues.apache.org\\jira\\projects\\JOSHUA'),
 'marmotta': ('https://github.com/apache/marmotta',
  'http:\\issues.apache.org\\jira\\projects\\MARMOTTA'),
 'qpid': ('https://github.com/apache/qpid',
  'http:\\issues.apache.org\\jira\\projects\\QPID'),
 'mnemonic': ('https://github.com/apache/mnemonic',
  'http:\\issues.apache.org\\jira\\projects\\MNEMONIC'),
 'james-jdkim': ('https://github.com/apache/james-jdkim',
  'http:\\issues.apache.org\\jira\\projects\\JDKIM'),
 'maven-patch-plugin': ('https://github.com/apache/maven-patch-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MPATCH'),
 'commons-dbcp': ('https://github.com/apache/commons-dbcp',
  'http:\\issues.apache.org\\jira\\projects\\DBCP'),
 'commons-crypto': ('https://github.com/apache/commons-crypto',
  'http:\\issues.apache.org\\jira\\projects\\CRYPTO'),
 'commons-jexl': ('https://github.com/apache/commons-jexl',
  'http:\\issues.apache.org\\jira\\projects\\JEXL'),
 'curator': ('https://github.com/apache/curator',
  'http:\\issues.apache.org\\jira\\projects\\CURATOR'),
 'maven-wagon': ('https://github.com/apache/maven-wagon',
  'http:\\issues.apache.org\\jira\\projects\\WAGON'),
 'maven-jlink-plugin': ('https://github.com/apache/maven-jlink-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MJLINK'),
 'commons-weaver': ('https://github.com/apache/commons-weaver',
  'http:\\issues.apache.org\\jira\\projects\\WEAVER'),
 'qpid-jms': ('https://github.com/apache/qpid-jms',
  'http:\\issues.apache.org\\jira\\projects\\QPIDJMS'),
 'pulsar': ('https://github.com/apache/pulsar',
  'http:\\issues.apache.org\\jira\\projects\\PULSAR'),
 'directmemory': ('https://github.com/apache/directmemory',
  'http:\\issues.apache.org\\jira\\projects\\DIRECTMEMORY'),
 'nifi': ('https://github.com/apache/nifi',
  'http:\\issues.apache.org\\jira\\projects\\NIFI'),
 'commons-email': ('https://github.com/apache/commons-email',
  'http:\\issues.apache.org\\jira\\projects\\EMAIL'),
 'activemq-openwire': ('https://github.com/apache/activemq-openwire',
  'http:\\issues.apache.org\\jira\\projects\\OPENWIRE'),
 'maven-javadoc-plugin': ('https://github.com/apache/maven-javadoc-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MJAVADOC'),
 'mina': ('https://github.com/apache/mina',
  'http:\\issues.apache.org\\jira\\projects\\DIRMINA'),
 'juneau': ('https://github.com/apache/juneau',
  'http:\\issues.apache.org\\jira\\projects\\JUNEAU'),
 'maven-resolver': ('https://github.com/apache/maven-resolver',
  'http:\\issues.apache.org\\jira\\projects\\MRESOLVER'),
 'jackrabbit-oak': ('https://github.com/apache/jackrabbit-oak',
  'http:\\issues.apache.org\\jira\\projects\\OAK'),
 'commons-validator': ('https://github.com/apache/commons-validator',
  'http:\\issues.apache.org\\jira\\projects\\VALIDATOR'),
 'james-jspf': ('https://github.com/apache/james-jspf',
  'http:\\issues.apache.org\\jira\\projects\\JSPF'),
 'tiles': ('https://github.com/apache/tiles',
  'http:\\issues.apache.org\\jira\\projects\\TILES'),
 'maven-dependency-plugin': ('https://github.com/apache/maven-dependency-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MDEP'),
 'zookeeper': ('https://github.com/apache/zookeeper',
  'http:\\issues.apache.org\\jira\\projects\\ZOOKEEPER'),
 'airavata': ('https://github.com/apache/airavata',
  'http:\\issues.apache.org\\jira\\projects\\AIRAVATA'),
 'maven-rar-plugin': ('https://github.com/apache/maven-rar-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MRAR'),
 'rocketmq': ('https://github.com/apache/rocketmq',
  'http:\\issues.apache.org\\jira\\projects\\ROCKETMQ'),
 'openejb': ('https://github.com/apache/openejb',
  'http:\\issues.apache.org\\jira\\projects\\OPENEJB'),
 'submarine': ('https://github.com/apache/submarine',
  'http:\\issues.apache.org\\jira\\projects\\SUBMARINE'),
 'stanbol': ('https://github.com/apache/stanbol',
  'http:\\issues.apache.org\\jira\\projects\\STANBOL'),
 'nifi-registry': ('https://github.com/apache/nifi-registry',
  'http:\\issues.apache.org\\jira\\projects\\NIFIREG'),
 'maven-remote-resources-plugin': ('https://github.com/apache/maven-remote-resources-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MRRESOURCES'),
 'hadoop-common': ('https://github.com/apache/hadoop-common',
  'http:\\issues.apache.org\\jira\\projects\\HADOOP'),
 'openjpa': ('https://github.com/apache/openjpa',
  'http:\\issues.apache.org\\jira\\projects\\OPENJPA'),
 'syncope': ('https://github.com/apache/syncope',
  'http:\\issues.apache.org\\jira\\projects\\SYNCOPE'),
 'servicemix': ('https://github.com/apache/servicemix',
  'http:\\issues.apache.org\\jira\\projects\\SM'),
 'phoenix-omid': ('https://github.com/apache/phoenix-omid',
  'http:\\issues.apache.org\\jira\\projects\\OMID'),
 'phoenix-tephra': ('https://github.com/apache/phoenix-tephra',
  'http:\\issues.apache.org\\jira\\projects\\TEPHRA'),
 'myfaces-trinidad': ('https://github.com/apache/myfaces-trinidad',
  'http:\\issues.apache.org\\jira\\projects\\TRINIDAD'),
 'jena': ('https://github.com/apache/jena',
  'http:\\issues.apache.org\\jira\\projects\\JENA'),
 'commons-logging': ('https://github.com/apache/commons-logging',
  'http:\\issues.apache.org\\jira\\projects\\LOGGING'),
 'maven-pdf-plugin': ('https://github.com/apache/maven-pdf-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MPDF'),
 'maven-archetype': ('https://github.com/apache/maven-archetype',
  'http:\\issues.apache.org\\jira\\projects\\ARCHETYPE'),
 'hama': ('https://github.com/apache/hama',
  'http:\\issues.apache.org\\jira\\projects\\HAMA'),
 'archiva': ('https://github.com/apache/archiva',
  'http:\\issues.apache.org\\jira\\projects\\MRM'),
 'commons-pool': ('https://github.com/apache/commons-pool',
  'http:\\issues.apache.org\\jira\\projects\\POOL'),
 'plc4x': ('https://github.com/apache/plc4x',
  'http:\\issues.apache.org\\jira\\projects\\PLC4X'),
 'oltu': ('https://github.com/apache/oltu',
  'http:\\issues.apache.org\\jira\\projects\\OLTU'),
 'ftpserver': ('https://github.com/apache/ftpserver',
  'http:\\issues.apache.org\\jira\\projects\\FTPSERVER'),
 'cloudstack': ('https://github.com/apache/cloudstack',
  'http:\\issues.apache.org\\jira\\projects\\CLOUDSTACK'),
 'maven-verifier-plugin': ('https://github.com/apache/maven-verifier-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MVERIFIER'),
 'metron': ('https://github.com/apache/metron',
  'http:\\issues.apache.org\\jira\\projects\\METRON'),
 'wicket': ('https://github.com/apache/wicket',
  'http:\\issues.apache.org\\jira\\projects\\WICKET'),
 'aries': ('https://github.com/apache/aries',
  'http:\\issues.apache.org\\jira\\projects\\ARIES'),
 'accumulo': ('https://github.com/apache/accumulo',
  'http:\\issues.apache.org\\jira\\projects\\ACCUMULO'),
 'maven-shade-plugin': ('https://github.com/apache/maven-shade-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MSHADE'),
 'unomi': ('https://github.com/apache/unomi',
  'http:\\issues.apache.org\\jira\\projects\\UNOMI'),
 'maven-gpg-plugin': ('https://github.com/apache/maven-gpg-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MGPG'),
 'maven-toolchains-plugin': ('https://github.com/apache/maven-toolchains-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MTOOLCHAINS'),
 'maven-jdeprscan-plugin': ('https://github.com/apache/maven-jdeprscan-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MJDEPRSCAN'),
 'flink': ('https://github.com/apache/flink',
  'http:\\issues.apache.org\\jira\\projects\\FLINK'),
 'commons-lang': ('https://github.com/apache/commons-lang',
  'http:\\issues.apache.org\\jira\\projects\\LANG'),
 'mahout': ('https://github.com/apache/mahout',
  'http:\\issues.apache.org\\jira\\projects\\MAHOUT'),
 'metamodel': ('https://github.com/apache/metamodel',
  'http:\\issues.apache.org\\jira\\projects\\METAMODEL'),
 'eagle': ('https://github.com/apache/eagle',
  'http:\\issues.apache.org\\jira\\projects\\EAGLE'),
 'maven-help-plugin': ('https://github.com/apache/maven-help-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MPH'),
 'tika': ('https://github.com/apache/tika',
  'http:\\issues.apache.org\\jira\\projects\\TIKA'),
 'ambari': ('https://github.com/apache/ambari',
  'http:\\issues.apache.org\\jira\\projects\\AMBARI'),
 'vxquery': ('https://github.com/apache/vxquery',
  'http:\\issues.apache.org\\jira\\projects\\VXQUERY'),
 'maven-jdeps-plugin': ('https://github.com/apache/maven-jdeps-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MJDEPS'),
 'commons-rng': ('https://github.com/apache/commons-rng',
  'http:\\issues.apache.org\\jira\\projects\\RNG'),
 'helix': ('https://github.com/apache/helix',
  'http:\\issues.apache.org\\jira\\projects\\HELIX'),
 'tinkerpop': ('https://github.com/apache/tinkerpop',
  'http:\\issues.apache.org\\jira\\projects\\TINKERPOP'),
 'isis': ('https://github.com/apache/isis',
  'http:\\issues.apache.org\\jira\\projects\\ISIS'),
 'synapse': ('https://github.com/apache/synapse',
  'http:\\issues.apache.org\\jira\\projects\\SYNAPSE'),
 'hcatalog': ('https://github.com/apache/hcatalog',
  'http:\\issues.apache.org\\jira\\projects\\HCATALOG'),
 'asterixdb': ('https://github.com/apache/asterixdb',
  'http:\\issues.apache.org\\jira\\projects\\ASTERIXDB'),
 'commons-proxy': ('https://github.com/apache/commons-proxy',
  'http:\\issues.apache.org\\jira\\projects\\PROXY'),
 'sandesha': ('https://github.com/apache/sandesha',
  'http:\\issues.apache.org\\jira\\projects\\SAND'),
 'shindig': ('https://github.com/apache/shindig',
  'http:\\issues.apache.org\\jira\\projects\\SHINDIG'),
 'commons-imaging': ('https://github.com/apache/commons-imaging',
  'http:\\issues.apache.org\\jira\\projects\\IMAGING'),
 'openwebbeans': ('https://github.com/apache/openwebbeans',
  'http:\\issues.apache.org\\jira\\projects\\OWB'),
 'maven-plugin-testing': ('https://github.com/apache/maven-plugin-testing',
  'http:\\issues.apache.org\\jira\\projects\\MPLUGINTESTING'),
 'tomee': ('https://github.com/apache/tomee',
  'http:\\issues.apache.org\\jira\\projects\\TOMEE'),
 'activemq-cli-tools': ('https://github.com/apache/activemq-cli-tools',
  'http:\\issues.apache.org\\jira\\projects\\AMQCLI'),
 'geronimo': ('https://github.com/apache/geronimo',
  'http:\\issues.apache.org\\jira\\projects\\GERONIMO'),
 'juddi': ('https://github.com/apache/juddi',
  'http:\\issues.apache.org\\jira\\projects\\JUDDI'),
 'maven-project-info-reports-plugin': ('https://github.com/apache/maven-project-info-reports-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MPIR'),
 'commons-net': ('https://github.com/apache/commons-net',
  'http:\\issues.apache.org\\jira\\projects\\NET'),
 'odftoolkit': ('https://github.com/apache/odftoolkit',
  'http:\\issues.apache.org\\jira\\projects\\ODFTOOLKIT'),
 'maven-changelog-plugin': ('https://github.com/apache/maven-changelog-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MCHANGELOG'),
 'bval': ('https://github.com/apache/bval',
  'http:\\issues.apache.org\\jira\\projects\\BVAL'),
 'cayenne': ('https://github.com/apache/cayenne',
  'http:\\issues.apache.org\\jira\\projects\\CAY'),
 'chainsaw': ('https://github.com/apache/chainsaw',
  'http:\\issues.apache.org\\jira\\projects\\CHAINSAW'),
 'cxf-fediz': ('https://github.com/apache/cxf-fediz',
  'http:\\issues.apache.org\\jira\\projects\\FEDIZ'),
 'commons-beanutils': ('https://github.com/apache/commons-beanutils',
  'http:\\issues.apache.org\\jira\\projects\\BEANUTILS'),
 'commons-ognl': ('https://github.com/apache/commons-ognl',
  'http:\\issues.apache.org\\jira\\projects\\OGNL'),
 'tajo': ('https://github.com/apache/tajo',
  'http:\\issues.apache.org\\jira\\projects\\TAJO'),
 'cxf': ('https://github.com/apache/cxf',
  'http:\\issues.apache.org\\jira\\projects\\CXF'),
 'james-jsieve': ('https://github.com/apache/james-jsieve',
  'http:\\issues.apache.org\\jira\\projects\\JSIEVE'),
 'phoenix': ('https://github.com/apache/phoenix',
  'http:\\issues.apache.org\\jira\\projects\\PHOENIX'),
 'pivot': ('https://github.com/apache/pivot',
  'http:\\issues.apache.org\\jira\\projects\\PIVOT'),
 'maven-resources-plugin': ('https://github.com/apache/maven-resources-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MRESOURCES'),
 'gora': ('https://github.com/apache/gora',
  'http:\\issues.apache.org\\jira\\projects\\GORA'),
 'commons-io': ('https://github.com/apache/commons-io',
  'http:\\issues.apache.org\\jira\\projects\\IO'),
 'activemq': ('https://github.com/apache/activemq',
  'http:\\issues.apache.org\\jira\\projects\\AMQ'),
 'maven-jar-plugin': ('https://github.com/apache/maven-jar-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MJAR'),
 'commons-collections': ('https://github.com/apache/commons-collections',
  'http:\\issues.apache.org\\jira\\projects\\COLLECTIONS'),
 'manifoldcf': ('https://github.com/apache/manifoldcf',
  'http:\\issues.apache.org\\jira\\projects\\CONNECTORS'),
 'griffin': ('https://github.com/apache/griffin',
  'http:\\issues.apache.org\\jira\\projects\\GRIFFIN'),
 'chukwa': ('https://github.com/apache/chukwa',
  'http:\\issues.apache.org\\jira\\projects\\CHUKWA'),
 'oodt': ('https://github.com/apache/oodt',
  'http:\\issues.apache.org\\jira\\projects\\OODT'),
 'kalumet': ('https://github.com/apache/kalumet',
  'http:\\issues.apache.org\\jira\\projects\\KALUMET'),
 'tez': ('https://github.com/apache/tez',
  'http:\\issues.apache.org\\jira\\projects\\TEZ'),
 'maven-ejb-plugin': ('https://github.com/apache/maven-ejb-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MEJB'),
 'deltaspike': ('https://github.com/apache/deltaspike',
  'http:\\issues.apache.org\\jira\\projects\\DELTASPIKE'),
 'commons-jelly': ('https://github.com/apache/commons-jelly',
  'http:\\issues.apache.org\\jira\\projects\\JELLY'),
 'jclouds': ('https://github.com/apache/jclouds',
  'http:\\issues.apache.org\\jira\\projects\\JCLOUDS'),
 'ranger': ('https://github.com/apache/ranger',
  'http:\\issues.apache.org\\jira\\projects\\RANGER'),
 'activemq-artemis': ('https://github.com/apache/activemq-artemis',
  'http:\\issues.apache.org\\jira\\projects\\ARTEMIS'),
 'sentry': ('https://github.com/apache/sentry',
  'http:\\issues.apache.org\\jira\\projects\\SENTRY'),
 'activemq-apollo': ('https://github.com/apache/activemq-apollo',
  'http:\\issues.apache.org\\jira\\projects\\APLO'),
 'rya': ('https://github.com/apache/rya',
  'http:\\issues.apache.org\\jira\\projects\\RYA'),
 'commons-codec': ('https://github.com/apache/commons-codec',
  'http:\\issues.apache.org\\jira\\projects\\CODEC'),
 'ddlutils': ('https://github.com/apache/ddlutils',
  'http:\\issues.apache.org\\jira\\projects\\DDLUTILS'),
 'commons-text': ('https://github.com/apache/commons-text',
  'http:\\issues.apache.org\\jira\\projects\\TEXT'),
 'giraph': ('https://github.com/apache/giraph',
  'http:\\issues.apache.org\\jira\\projects\\GIRAPH'),
 'bigtop': ('https://github.com/apache/bigtop',
  'http:\\issues.apache.org\\jira\\projects\\BIGTOP'),
 'commons-configuration': ('https://github.com/apache/commons-configuration',
  'http:\\issues.apache.org\\jira\\projects\\CONFIGURATION'),
 'james-mime4j': ('https://github.com/apache/james-mime4j',
  'http:\\issues.apache.org\\jira\\projects\\MIME4J'),
 'maven-site-plugin': ('https://github.com/apache/maven-site-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MSITE'),
 'opennlp': ('https://github.com/apache/opennlp',
  'http:\\issues.apache.org\\jira\\projects\\OPENNLP'),
 'storm': ('https://github.com/apache/storm',
  'http:\\issues.apache.org\\jira\\projects\\STORM'),
 'zeppelin': ('https://github.com/apache/zeppelin',
  'http:\\issues.apache.org\\jira\\projects\\ZEPPELIN'),
 'maven-doap-plugin': ('https://github.com/apache/maven-doap-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MDOAP'),
 'maven-changes-plugin': ('https://github.com/apache/maven-changes-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MCHANGES'),
 'maven-doxia': ('https://github.com/apache/maven-doxia',
  'http:\\issues.apache.org\\jira\\projects\\DOXIA'),
 'maven-surefire': ('https://github.com/apache/maven-surefire',
  'http:\\issues.apache.org\\jira\\projects\\SUREFIRE'),
 'myfaces-test': ('https://github.com/apache/myfaces-test',
  'http:\\issues.apache.org\\jira\\projects\\MYFACESTEST'),
 'twill': ('https://github.com/apache/twill',
  'http:\\issues.apache.org\\jira\\projects\\TWILL'),
 'continuum': ('https://github.com/apache/continuum',
  'http:\\issues.apache.org\\jira\\projects\\CONTINUUM'),
 'maven-clean-plugin': ('https://github.com/apache/maven-clean-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MCLEAN'),
 'kylin': ('https://github.com/apache/kylin',
  'http:\\issues.apache.org\\jira\\projects\\KYLIN'),
 'maven-doxia-tools': ('https://github.com/apache/maven-doxia-tools',
  'http:\\issues.apache.org\\jira\\projects\\DOXIATOOLS'),
 'jsecurity': ('https://github.com/apache/jsecurity',
  'http:\\issues.apache.org\\jira\\projects\\JSEC'),
 'maven-deploy-plugin': ('https://github.com/apache/maven-deploy-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MDEPLOY'),
 'tiles-autotag': ('https://github.com/apache/tiles-autotag',
  'http:\\issues.apache.org\\jira\\projects\\AUTOTAG'),
 'mina-sshd': ('https://github.com/apache/mina-sshd',
  'http:\\issues.apache.org\\jira\\projects\\SSHD'),
 'maven-compiler-plugin': ('https://github.com/apache/maven-compiler-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MCOMPILER'),
 'maven-install-plugin': ('https://github.com/apache/maven-install-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MINSTALL'),
 'sanselan': ('https://github.com/apache/sanselan',
  'http:\\issues.apache.org\\jira\\projects\\SANSELAN'),
 'avro': ('https://github.com/apache/avro',
  'http:\\issues.apache.org\\jira\\projects\\AVRO'),
 'commons-compress': ('https://github.com/apache/commons-compress',
  'http:\\issues.apache.org\\jira\\projects\\COMPRESS'),
 'hadoop': ('https://github.com/apache/hadoop',
  'http:\\issues.apache.org\\jira\\projects\\HADOOP'),
 'shiro': ('https://github.com/apache/shiro',
  'http:\\issues.apache.org\\jira\\projects\\SHIRO'),
 'empire-db': ('https://github.com/apache/empire-db',
  'http:\\issues.apache.org\\jira\\projects\\EMPIREDB'),
 'commons-bsf': ('https://github.com/apache/commons-bsf',
  'http:\\issues.apache.org\\jira\\projects\\BSF'),
 'chemistry': ('https://github.com/apache/chemistry',
  'http:\\issues.apache.org\\jira\\projects\\CMIS'),
 'commons-digester': ('https://github.com/apache/commons-digester',
  'http:\\issues.apache.org\\jira\\projects\\DIGESTER'),
 'directory-studio': ('https://github.com/apache/directory-studio',
  'http:\\issues.apache.org\\jira\\projects\\DIRSTUDIO'),
 'falcon': ('https://github.com/apache/falcon',
  'http:\\issues.apache.org\\jira\\projects\\FALCON'),
 'myfaces-tobago': ('https://github.com/apache/myfaces-tobago',
  'http:\\issues.apache.org\\jira\\projects\\TOBAGO'),
 'maven-assembly-plugin': ('https://github.com/apache/maven-assembly-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MASSEMBLY'),
 'openmeetings': ('https://github.com/apache/openmeetings',
  'http:\\issues.apache.org\\jira\\projects\\OPENMEETINGS'),
 'savan': ('https://github.com/apache/savan',
  'http:\\issues.apache.org\\jira\\projects\\SAVAN'),
 'maven-invoker-plugin': ('https://github.com/apache/maven-invoker-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MINVOKER'),
 'pdfbox': ('https://github.com/apache/pdfbox',
  'http:\\issues.apache.org\\jira\\projects\\PDFBOX'),
 'maven-jxr': ('https://github.com/apache/maven-jxr',
  'http:\\issues.apache.org\\jira\\projects\\JXR'),
 'reef': ('https://github.com/apache/reef',
  'http:\\issues.apache.org\\jira\\projects\\REEF'),
 'maven-checkstyle-plugin': ('https://github.com/apache/maven-checkstyle-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MCHECKSTYLE'),
 'maven-war-plugin': ('https://github.com/apache/maven-war-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MWAR'),
 'maven-jmod-plugin': ('https://github.com/apache/maven-jmod-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MJMOD'),
 'commons-dbutils': ('https://github.com/apache/commons-dbutils',
  'http:\\issues.apache.org\\jira\\projects\\DBUTILS'),
 'lens': ('https://github.com/apache/lens',
  'http:\\issues.apache.org\\jira\\projects\\LENS'),
 'abdera': ('https://github.com/apache/abdera',
  'http:\\issues.apache.org\\jira\\projects\\ABDERA'),
 'maven-stage-plugin': ('https://github.com/apache/maven-stage-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MSTAGE'),
 'maven-source-plugin': ('https://github.com/apache/maven-source-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MSOURCES'),
 'atlas': ('https://github.com/apache/atlas',
  'http:\\issues.apache.org\\jira\\projects\\ATLAS'),
 'hive': ('https://github.com/apache/hive',
  'http:\\issues.apache.org\\jira\\projects\\HIVE'),
 'maven-plugin-tools': ('https://github.com/apache/maven-plugin-tools',
  'http:\\issues.apache.org\\jira\\projects\\MPLUGIN'),
 'cxf-xjc-utils': ('https://github.com/apache/cxf-xjc-utils',
  'http:\\issues.apache.org\\jira\\projects\\CXFXJC'),
 'commons-numbers': ('https://github.com/apache/commons-numbers',
  'http:\\issues.apache.org\\jira\\projects\\NUMBERS'),
 'bookkeeper': ('https://github.com/apache/bookkeeper',
  'http:\\issues.apache.org\\jira\\projects\\BOOKKEEPER'),
 'karaf': ('https://github.com/apache/karaf',
  'http:\\issues.apache.org\\jira\\projects\\KARAF'),
 'maven-doxia-sitetools': ('https://github.com/apache/maven-doxia-sitetools',
  'http:\\issues.apache.org\\jira\\projects\\DOXIASITETOOLS'),
 'drill': ('https://github.com/apache/drill',
  'http:\\issues.apache.org\\jira\\projects\\DRILL'),
 'maven-pmd-plugin': ('https://github.com/apache/maven-pmd-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MPMD'),
 'sis': ('https://github.com/apache/sis',
  'http:\\issues.apache.org\\jira\\projects\\SIS'),
 'tiles-request': ('https://github.com/apache/tiles-request',
  'http:\\issues.apache.org\\jira\\projects\\TREQ'),
 'commons-chain': ('https://github.com/apache/commons-chain',
  'http:\\issues.apache.org\\jira\\projects\\CHAIN'),
 'systemml': ('https://github.com/apache/systemml',
  'http:\\issues.apache.org\\jira\\projects\\SYSTEMML'),
 'ignite': ('https://github.com/apache/ignite',
  'http:\\issues.apache.org\\jira\\projects\\IGNITE'),
 'commons-csv': ('https://github.com/apache/commons-csv',
  'http:\\issues.apache.org\\jira\\projects\\CSV'),
 'hbase': ('https://github.com/apache/hbase',
  'http:\\issues.apache.org\\jira\\projects\\HBASE'),
 'maven-antrun-plugin': ('https://github.com/apache/maven-antrun-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MANTRUN'),
 'usergrid': ('https://github.com/apache/usergrid',
  'http:\\issues.apache.org\\jira\\projects\\USERGRID'),
 'commons-jxpath': ('https://github.com/apache/commons-jxpath',
  'http:\\issues.apache.org\\jira\\projects\\JXPATH'),
 'cocoon': ('https://github.com/apache/cocoon',
  'http:\\issues.apache.org\\jira\\projects\\COCOON'),
 'wookie': ('https://github.com/apache/wookie',
  'http:\\issues.apache.org\\jira\\projects\\WOOKIE'),
 'maven-scm': ('https://github.com/apache/maven-scm',
  'http:\\issues.apache.org\\jira\\projects\\SCM'),
 'commons-jci': ('https://github.com/apache/commons-jci',
  'http:\\issues.apache.org\\jira\\projects\\JCI'),
 'commons-jcs': ('https://github.com/apache/commons-jcs',
  'http:\\issues.apache.org\\jira\\projects\\JCS'),
 'flume': ('https://github.com/apache/flume',
  'http:\\issues.apache.org\\jira\\projects\\FLUME'),
 'nuvem': ('https://github.com/apache/nuvem',
  'http:\\issues.apache.org\\jira\\projects\\NUVEM'),
 'dubbo': ('https://github.com/apache/dubbo',
  'http:\\issues.apache.org\\jira\\projects\\DUBBO'),
 'oozie': ('https://github.com/apache/oozie',
  'http:\\issues.apache.org\\jira\\projects\\OOZIE'),
 'jackrabbit-filevault': ('https://github.com/apache/jackrabbit-filevault',
  'http:\\issues.apache.org\\jira\\projects\\JCRVLT'),
 'ctakes': ('https://github.com/apache/ctakes',
  'http:\\issues.apache.org\\jira\\projects\\CTAKES'),
 'clerezza': ('https://github.com/apache/clerezza',
  'http:\\issues.apache.org\\jira\\projects\\CLEREZZA'),
 'streams': ('https://github.com/apache/streams',
  'http:\\issues.apache.org\\jira\\projects\\STREAMS'),
 'commons-cli': ('https://github.com/apache/commons-cli',
  'http:\\issues.apache.org\\jira\\projects\\CLI'),
 'commons-math': ('https://github.com/apache/commons-math',
  'http:\\issues.apache.org\\jira\\projects\\MATH'),
 'myfaces': ('https://github.com/apache/myfaces',
  'http:\\issues.apache.org\\jira\\projects\\MYFACES'),
 'jspwiki': ('https://github.com/apache/jspwiki',
  'http:\\issues.apache.org\\jira\\projects\\JSPWIKI'),
 'servicemix-components': ('https://github.com/apache/servicemix-components',
  'http:\\issues.apache.org\\jira\\projects\\SMXCOMP'),
 'camel': ('https://github.com/apache/camel',
  'http:\\issues.apache.org\\jira\\projects\\CAMEL'),
 'james-hupa': ('https://github.com/apache/james-hupa',
  'http:\\issues.apache.org\\jira\\projects\\HUPA'),
 'commons-vfs': ('https://github.com/apache/commons-vfs',
  'http:\\issues.apache.org\\jira\\projects\\VFS'),
 'hadoop-hdfs': ('https://github.com/apache/hadoop-hdfs',
  'http:\\issues.apache.org\\jira\\projects\\HDFS'),
 'maven-scm-publish-plugin': ('https://github.com/apache/maven-scm-publish-plugin',
  'http:\\issues.apache.org\\jira\\projects\\MSCMPUB'),
 'geronimo-devtools': ('https://github.com/apache/geronimo-devtools',
  'http:\\issues.apache.org\\jira\\projects\\GERONIMODEVTOOLS'),
 'knox': ('https://github.com/apache/knox',
  'http:\\issues.apache.org\\jira\\projects\\KNOX'),
 'maven': ('https://github.com/apache/maven',
  'http:\\issues.apache.org\\jira\\projects\\MNG'),
 'commons-scxml': ('https://github.com/apache/commons-scxml',
  'http:\\issues.apache.org\\jira\\projects\\SCXML'),
 'james-postage': ('https://github.com/apache/james-postage',
  'http:\\issues.apache.org\\jira\\projects\\POSTAGE'),
 'jackrabbit-ocm': ('https://github.com/apache/jackrabbit-ocm',
  'http:\\issues.apache.org\\jira\\projects\\OCM'),
 'commons-exec': ('https://github.com/apache/commons-exec',
  'http:\\issues.apache.org\\jira\\projects\\EXEC'),
 'commons-bcel': ('https://github.com/apache/commons-bcel',
  'http:\\issues.apache.org\\jira\\projects\\BCEL')}


if __name__ == "__main__":
    full_experiment(*sys.argv[1:])