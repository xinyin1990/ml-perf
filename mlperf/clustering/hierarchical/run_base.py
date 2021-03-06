#
# Author: Vincenzo Musco (http://www.vmusco.com)

import csv
import os
import re
import subprocess

from mlperf.clustering.tools import dumpDataOnCleanCsv
from mlperf.tools.config import MATLAB_EXE, TEMPFOLDER, JAVA_EXE, R_BIN
from mlperf.tools.static import datasetOutFile, MATLAB_ALGO, matlabRedirectTempFolder, WEKA_ALGO, JAVA_CLASSPATH, \
    SKLEARN_ALGO, R_ALGO, SHOGUN_ALGO, R_SCRIPT_BASE_DIR


def matlabProcess(clustersNumber, dataLessTarget, datasetName, runinfo = None):
    outputFile = datasetOutFile(datasetName, MATLAB_ALGO, runinfo=runinfo)

    if os.path.exists(outputFile):
        print("matlab skipped")
        return

    tempFile = dumpDataOnCleanCsv(dataLessTarget)

    matlabCommand = "cluster(linkage(csvread('{}'), 'ward'),'Maxclust',{})".format(tempFile, str(clustersNumber))
    command_parts = [MATLAB_EXE, "-nodisplay", "-nosplash", "-nodesktop", "-r \"rng('shuffle'); {}idx = {}; disp(idx); exit;\"   ".format(matlabRedirectTempFolder(TEMPFOLDER), matlabCommand)]
    print(" ".join(command_parts))
    result = subprocess.run(command_parts, stdout=subprocess.PIPE)
    res = result.stdout

    lines = res.decode().split("\n")
    print(len(lines))
    i = 0
    resultFile = open(outputFile, 'w')
    for line in lines:
        matches = re.fullmatch("     ?([0-9]+)", line)

        if matches is not None:
            resultFile.write("{},{}\n".format(i, matches.group(1)))
            i += 1

    resultFile.close()
    os.unlink(tempFile)




def wekaProcess(inFile, datasetName, runinfo = None):
    outputFile = datasetOutFile(datasetName, WEKA_ALGO, runinfo = runinfo)

    command_parts = [JAVA_EXE, "-Xmx100g", "-classpath", JAVA_CLASSPATH, "HierarchicalWekaRun", inFile, outputFile]
    print(" ".join(command_parts))

    if os.path.exists(outputFile):
        print("weka skipped")
        return

    subprocess.call(command_parts)



def sklearnProcess(clustersNumber, dataLessTarget, datasetName, runinfo = None):
    import sklearn.cluster
    
    selectedAlgo = SKLEARN_ALGO
    outputFile = datasetOutFile(datasetName, selectedAlgo, runinfo=runinfo)

    if os.path.exists(outputFile):
        print("sklearn skipped")
        return

    builtModel = sklearn.cluster.AgglomerativeClustering(n_clusters=clustersNumber)
    builtModel.fit(dataLessTarget)

    with open(outputFile, 'w') as csvfile:
        filewriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

        for index, row in dataLessTarget.iterrows():
            filewriter.writerow([index, builtModel.labels_[index]])



#TODO Makes the pyhon process dies!!!???!!!
def shogunProcess(clustersNumber, dataLessTarget, datasetName, runinfo = None, initialClusters = None):
    import shogun

    outputFile = datasetOutFile(datasetName, SHOGUN_ALGO, runinfo=runinfo)

    if os.path.exists(outputFile):
        print("shogun skipped")
        return

    train_features = shogun.RealFeatures(dataLessTarget.values.astype("float64").transpose())
    # distance metric over feature matrix - Euclidean distance
    distance = shogun.EuclideanDistance(train_features, train_features)

    hierarchical = shogun.Hierarchical(clustersNumber, distance)

    #TODO Makes the pyhon process dies!!!???!!!

    d = hierarchical.get_merge_distances()
    cp = hierarchical.get_cluster_pairs()
    
    with open(outputFile, 'w') as csvfile:
        filewriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
    
        for index, row in dataLessTarget.iterrows():
            filewriter.writerow([index, result[index].item(0)])




def rProcess(srcFile, datasetName, runinfo = None):
    selectedAlgo = R_ALGO
    outputFile = datasetOutFile(datasetName, selectedAlgo, runinfo=runinfo)

    if os.path.exists(outputFile):
        print("R skipped")
        return

    command_parts = [R_BIN, "--no-save", "--quiet", os.join(R_SCRIPT_BASE_DIR, "hierarchical_test.R"), srcFile, outputFile]
    subprocess.call(command_parts)