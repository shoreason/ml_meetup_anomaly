import matplotlib.pyplot as plt
import numpy as np
# %matplotlib inline

from numpy import genfromtxt
from scipy.stats import multivariate_normal
from sklearn.metrics import f1_score

'''
we usually don't have very large labelled dataset in anomaly detection
scenarios. That's why what we fit some distribution and try to learn anomaly
threshold value using small available labels. - Aaqib Saeed
https://aqibsaeed.github.io/2016-07-17-anomaly-detection/
'''

#read data
def read_dataset(filePath,delimiter=','):
    return genfromtxt(filePath, delimiter=delimiter)

def feature_normalize(dataset):
    mu = np.mean(dataset,axis=0)
    sigma = np.std(dataset,axis=0)
    return (dataset - mu)/sigma

def estimateGaussian(dataset):
    mu = np.mean(dataset, axis=0)
    sigma = np.cov(dataset.T)
    return mu, sigma

def multivariateGaussian(dataset,mu,sigma):
    p = multivariate_normal(mean=mu, cov=sigma)
    return p.pdf(dataset)

# function to find the optimal value for threshold (epsilon)
def selectThresholdByCV(probs,gt):
    best_epsilon = 0
    best_f1 = 0
    f = 0
    stepsize = (max(probs) - min(probs)) / 1000;
    epsilons = np.arange(min(probs),max(probs),stepsize)
    for epsilon in np.nditer(epsilons):
        predictions = (probs < epsilon)
        f = f1_score(gt, predictions, average = "binary")
        if f > best_f1:
            best_f1 = f
            best_epsilon = epsilon
    return best_f1, best_epsilon

tr_data = read_dataset('tr_server_data.csv') # tr_data is the new set for which we are trying to detect the anomalies
cv_data = read_dataset('cv_server_data.csv') # cv_data is the training set
gt_data = read_dataset('gt_server_data.csv') # gr_data is usually available for past anomalous records

n_training_samples = tr_data.shape[0]
n_dim = tr_data.shape[1]

plt.figure()
plt.xlabel("Latency (ms)")
plt.ylabel("Throughput (mb/s)")
plt.plot(tr_data[:,0],tr_data[:,1],"bx")
plt.show()

mu, sigma = estimateGaussian(tr_data)
p = multivariateGaussian(tr_data,mu,sigma)

p_cv = multivariateGaussian(cv_data,mu,sigma)
fscore, ep = selectThresholdByCV(p_cv,gt_data)
outliers = np.asarray(np.where(p < ep))

plt.figure()
plt.xlabel("Latency (ms)")
plt.ylabel("Throughput (mb/s)")
plt.plot(tr_data[:,0],tr_data[:,1],"bx")
plt.plot(tr_data[outliers,0],tr_data[outliers,1],"ro")
plt.show()
