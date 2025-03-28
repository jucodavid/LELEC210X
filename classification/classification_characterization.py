import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pickle
import librosa

"Machine learning tools"
from seaborn import heatmap
from classification.datasets import Dataset
from classification.utils.audio_student import AudioUtil, Feature_vector_DS
from classification.utils.plots import (
    plot_decision_boundaries,
    plot_specgram,
    show_confusion_matrix,
)
from classification.utils.utils import accuracy

from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_circles, make_classification, make_moons
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix

max_str_length = 20

#program that will play all the sounds in the dataset in a row
def play_all_sounds(dataset):
    
    for i in range(len(dataset)//5):
        for j in ['background','fire','chainsaw', 'fireworks', 'gunshot']:
            print("Playing sound number ", i)
            dataset.play([j,i])
            time.sleep(5)
        
def load_dataset():
    dataset = Dataset()
    classnames = dataset.list_classes()
    myds = Feature_vector_DS(dataset, Nft=512, nmel=20, duration=950)
    return dataset, classnames, myds

def load_data(myds, classnames, dataset,distorsion_to_add = []):  
    index = np.arange(0,40) #liste des indexs qu'on veut augmenter 
    fm_dir = "data/feature_matrices/"  # where to save the features matrices 
    train_pct = 0.7

    featveclen = len(myds["fire", 0])  # number of items in a feature vector
    nitems = len(myds)  # number of sounds in the dataset
    naudio = dataset.naudio  # number of audio files in each class
    nclass = len(classnames)  # number of classes
    aug_factor = len(distorsion_to_add)+1
    nb_sample = len(index)
    X_aug = np.zeros((aug_factor * nclass * nb_sample, featveclen))
    y_aug = np.zeros((aug_factor * nclass * nb_sample ), dtype=f"<U{max_str_length}")
    print('a')
    for s in range(aug_factor):
        if s == 0:
            myds.mod_data_aug([])
        if s != 0:
            myds.mod_data_aug([distorsion_to_add[s - 1]])
        count = 0
        for idx in index:
            for class_idx, classname in enumerate(classnames):
                featvec = myds[classname, idx]
                X_aug[s * nclass * nb_sample + class_idx * nb_sample + count, :] = featvec
                y_aug[s * nclass * nb_sample + class_idx * nb_sample + count] = classname
                print('did it')
            count += 1
    # np.save(fm_dir + "feature_matrix_2D.npy", X_aug) #save the feature matrix
    # np.save(fm_dir + "labels.npy", y_aug) #save the labels
    return X_aug, y_aug

# def index_to_augmentation(index, distorsion_to_add = ["noise"]):
#     """
#     Take a list of indexes and return the corresponding augmented feature matrix
#     aug_factor : number of variation of a sample (1 = no variation)
#     """
#     aug_factor = len(distorsion_to_add)+1
#     nb_sample = len(index)
#     X_aug = np.zeros((aug_factor * nclass * nb_sample, featveclen))
#     y_aug = np.zeros((aug_factor * nclass * nb_sample ), dtype=f"<U{max_str_length}")
    
    
#     for s in range(aug_factor):
#         if s == 0:
#             myds.mod_data_aug([])
#         if s != 0:
#             myds.mod_data_aug([distorsion_to_add[s - 1]])
#         count = 0
#         for idx in index:
#             for class_idx, classname in enumerate(classnames):
#                 featvec = myds[classname, idx]
#                 X_aug[s * nclass * nb_sample + class_idx * nb_sample + count, :] = featvec
#                 y_aug[s * nclass * nb_sample + class_idx * nb_sample + count] = classname
#             count += 1
    
#     return X_aug, y_aug

def split_data(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y
    ) 
    fm_dir = "data/feature_matrices/"
    # np.save(fm_dir + "X_train.npy", X_train)
    # np.save(fm_dir + "X_test.npy", X_test)
    # np.save(fm_dir + "y_train.npy", y_train)
    # np.save(fm_dir + "y_test.npy", y_test)
    return X_train, X_test, y_train, y_test

def model_validation(X_train, y_train, X_test, y_test, best_est, best_depth, best_dims, classnames):
    model = RandomForestClassifier(n_estimators=best_est, max_depth=best_depth)
    print('ici')
    pca = PCA(n_components=best_dims, whiten=True)
    print('la')
    # X_train_reduced = pca.fit_transform(X_train)
    print('la')
    # X_test_reduced = pca.transform(X_test)
    print('la2')
    model.fit(X_train, y_train)
    #save the model in the pickle
    pickle.dump(model, open("classification/data/models/model_new_data_bg.pickle", "wb"))
    prediction = model.predict(X_test)
    print("Accuracy on test set: ", accuracy(prediction, y_test))
    acc = accuracy(prediction, y_test)
    conf = confusion_matrix(prediction, y_test)
    show_confusion_matrix(prediction, y_test, classnames)
    return model, acc, conf
print('go')
ds, cn, myds = load_dataset()
print('go1')
# print(len(myds))
X, y = load_data(myds, ['background','fire','chainsaw', 'fireworks', 'gunshot'], ds)
print('go2')
X_train, X_test, y_train, y_test = split_data(X, y)
print('go3')
model, acc, conf = model_validation(X_train, y_train, X_test, y_test, 100, 10, 11, ['background','fire','chainsaw', 'fireworks', 'gunshot'])
print('go4')
# print(len(y))
# print(len(ds))
# print(len(myds))
# play_all_sounds(myds)
# X = np.load("data/feature_matrices/feature_matrix_2D.npy")
# y = np.load("data/feature_matrices/labels.npy")

# def H(f, A, f1, f2):
#     return A * f / (np.sqrt(1 + (f / f1) ** 2) * np.sqrt(1 + (f / f2) ** 2))
# mel_freqs = librosa.mel_frequencies(n_mels=20, fmax= 11025)
# A = 3  # Gain factor
# f1 = 20  # Low cutoff frequency
# f2 = 5000  # High cutoff frequency
# H_values = H(mel_freqs, A, f1, f2)


# X_filt = np.zeros_like(X)
# for i in range(X.shape[0]):
#     X_filt[i] = X[i] * H_values
# #print melspectrogram of X[0] and then X_filt[0]
# plt.figure()
# plot_specgram(X[0])
# plt.title("Original")
# plt.figure()
# plot_specgram(X_filt[0])
# plt.title("Filtered")
# plt.show()

# kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
# acc = 0
# conf = np.zeros((5, 5))
# for idx_learn, idx_val in kf.split(X, y):
#     X_train, X_test, y_train, y_test = X[idx_learn], X[idx_val], y[idx_learn], y[idx_val]
# # X_train = np.load("data/feature_matrices/X_train.npy")
# # X_test = np.load("data/feature_matrices/X_test.npy")
# # y_train = np.load("data/feature_matrices/y_train.npy")
# # y_test = np.load("data/feature_matrices/y_test.npy")
# # print(len(y_train))
# # print(len(y_test))
#     mod, acc1, conf1 = model_validation(X_train, y_train, X_test, y_test, 100, 10, 11, ['birds', 'fire', 'chainsaw', 'handsaw', 'helicopter'])
#     acc += acc1
#     conf += conf1
# print("Average accuracy: ", acc / 5)
# for i in range (len(conf)):
#     for j in range(len(conf[0])):
#         conf[i][j] = conf[i][j] / 5


# plt.figure(figsize=(3, 3))
# heatmap(
#         conf.T,
#         square=True,
#         annot=True,
#         fmt="f",
#         cbar=False,
#         xticklabels=['birds', 'fire', 'chainsaw', 'handsaw', 'helicopter'],
#         yticklabels=['birds', 'fire', 'chainsaw', 'handsaw', 'helicopter'],
#         ax=plt.gca(),
#     )
# plt.xlabel("True label")
# plt.ylabel("Predicted label")
# plt.title('Average confusion matrix')
# plt.show()
# predictions = np.load('predictions.npy')
# # predictions = ['handsaw', 'handsaw', 'handsaw', 'birds', 'birds', 'handsaw', 'birds', 'birds', 'birds', 'chainsaw', 'fire', 'handsaw', 'fire', 'chainsaw', 'fire','birds', 'handsaw', 'birds', 'fire', 'birds', 'fire', 'birds', 'helicopter', 'fire', 'helicopeter', 'helicopter', 'chainsaw', 'fire', 'birds', 'fire', 'handsaw', 'birds', 'birds', 'birds', 'fire', 'birds', 'birds', 'chainsaw', 'birds', 'chainsaw', 'chainsaw', 'helicopter', 'birds', 'chainsaw', 'fire', 'chainsaw', 'handsaw', 'fire', 'birds', 'fire', 'chainsaw', 'fire', 'fire', 'fire', 'birds', 'handsaw', 'birds', 'fire', 'fire', 'fire', 'birds', 'birds', 'birds', 'fire', 'birds', 'birds', 'birds', 'fire', 'birds', 'chainsaw', 'fire', 'handsaw', 'helicopter', 'birds', 'chainsaw', 'handsaw', 'birds', 'helicopter', 'birds', 'birds', 'helicopter', 'handsaw', 'chainsaw', 'birds', 'handsaw', 'fire', 'birds', 'chainsaw', 'birds', 'handsaw', 'birds', 'birds', 'chainsaw', 'chainsaw', 'chainsaw', 'chainsaw', 'handsaw', 'birds', 'fire', 'chainsaw']
# print(len(predictions))
# print(predictions)
# true_labels = ['birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter', 'birds', 'fire', 'chainsaw', 'handsaw', 'helicopter','birds', 'fire', 'chainsaw', 'handsaw', 'helicopter']
# # print(len(true_labels))
# show_confusion_matrix(predictions, true_labels, ['birds', 'fire', 'chainsaw', 'handsaw', 'helicopter'])
# print(accuracy(predictions, true_labels))
