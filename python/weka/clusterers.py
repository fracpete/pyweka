# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# clusterers.py
# Copyright (C) 2014 Fracpete (fracpete at gmail dot com)

import javabridge
import logging
import os
import sys
import getopt
import weka.core.jvm as jvm
import weka.core.utils as utils
from weka.core.classes import JavaObject
from weka.core.classes import OptionHandler
from weka.core.classes import Capabilities

# logging setup
logger = logging.getLogger("weka.clusterers")


class Clusterer(OptionHandler):
    """
    Wrapper class for clusterers.
    """

    def __init__(self, classname=None, jobject=None):
        """
        Initializes the specified clusterer using either the classname or the supplied JB_Object.
        :param classname: the classname of the clusterer
        :param jobject: the JB_Object to use
        """
        if jobject is None:
            jobject = Clusterer.new_instance(classname)
        if classname is None:
            classname = utils.get_classname(jobject)
        self.classname = classname
        self.enforce_type(jobject, "weka.clusterers.Clusterer")
        super(Clusterer, self).__init__(jobject)

    def get_capabilities(self):
        """
        Returns the capabilities of the clusterer.
        :rtype: Capabilities
        """
        return Capabilities(javabridge.call(self.jobject, "getCapabilities", "()Lweka/core/Capabilities;"))

    def build_clusterer(self, data):
        """
        Builds the clusterer with the data.
        :param data: the data to use for training the clusterer
        """
        javabridge.call(self.jobject, "buildClusterer", "(Lweka/core/Instances;)V", data.jobject)

    def cluster_instance(self, inst):
        """
        Peforms a prediction.
        :param inst: the instance to determine the cluster for
        """
        return javabridge.call(self.jobject, "clusterInstance", "(Lweka/core/Instance;)D", inst.jobject)


class ClusterEvaluation(JavaObject):
    """
    Evaluation class for clusterers.
    """

    def __init__(self):
        """ Initializes a ClusterEvaluation object. """
        super(ClusterEvaluation, self).__init__(ClusterEvaluation.new_instance("weka.clusterers.ClusterEvaluation"))

    def set_model(self, clusterer):
        """ Sets the built clusterer to evaluate.
        :param clusterer: the clusterer to evaluate
        """
        javabridge.call(self.jobject, "setClusterer", "(Lweka/clusterers/Clusterer;)V", clusterer.jobject)

    def evaluate_model(self, test):
        """ Evaluates the currently set clusterer on the test set.
        :param test: the test set to use for evaluating
        """
        javabridge.call(self.jobject, "evaluateClusterer", "(Lweka/core/Instances;)V", test.jobject)

    def get_cluster_results(self):
        """ The cluster results as string. 
        :rtype : str
        """
        return javabridge.call(self.jobject, "clusterResultsToString", "()Ljava/lang/String;")

    @classmethod
    def evaluate_clusterer(cls, clusterer, args):
        """ Evaluates the clusterer with the given options.
        :rtype : str
        :param clusterer: the clusterer instance to evaluate
        :param args: the command-line arguments
        """
        return javabridge.static_call(
            "Lweka/clusterers/ClusterEvaluation;", "evaluateClusterer",
            "(Lweka/clusterers/Clusterer;[Ljava/lang/String;)Ljava/lang/String;",
            clusterer.jobject, args)


def main(args):
    """
    Runs a clusterer from the command-line. Calls JVM start/stop automatically.
    Options:
        -j jar1[:jar2...]
        -t train
        [-T test]
        [-d output model file]
        [-l input model file]
        [-p attribute range]
        [-x num folds]
        [-s seed]
        [-c classindex]
        [-g graph file]
        clusterer classname
        [clusterer options]
    """

    usage = "Usage: weka.clusterers -l jar1[" + os.pathsep + "jar2...] " \
            + "-t train [-T test] [-d output model file] [-l input model file] " \
            + "[-p attribute range] [-x num folds] [-s seed] [-c classindex] " \
            + "[-g graph file] clusterer classname [clusterer options]"

    optlist, optargs = getopt.getopt(args, "j:t:T:d:l:p:x:s:c:g:")
    if len(optargs) == 0:
        raise Exception("No clusterer classname provided!\n" + usage)
    for opt in optlist:
        if opt[0] == "-h":
            print(usage)
            return

    jars   = []
    params = []
    train  = None
    for opt in optlist:
        if opt[0] == "-j":
            jars = opt[1].split(os.pathsep)
        elif opt[0] == "-t":
            params.append(opt[0])
            params.append(opt[1])
            train = opt[1]
        elif opt[0] == "-T":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-d":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-l":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-p":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-x":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-s":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-c":
            params.append(opt[0])
            params.append(opt[1])
        elif opt[0] == "-g":
            params.append(opt[0])
            params.append(opt[1])

    # check parameters
    if train is None:
        raise Exception("No train file provided ('-t ...')!")

    jvm.start(jars)

    logger.debug("Commandline: " + utils.join_options(args))

    try:
        clusterer = Clusterer(classname=optargs[0])
        optargs = optargs[1:]
        if len(optargs) > 0:
            clusterer.set_options(optargs)
        print(ClusterEvaluation.evaluate_clusterer(clusterer, params))
    except Exception, ex:
        print(ex)
    finally:
        jvm.stop()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception, e:
        print(e)
