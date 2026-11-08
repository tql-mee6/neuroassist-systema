import numpy as np
from scipy import linalg, signal
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

class CSPOvR:
    """CSP «один против остальных» по каждому классу."""
    def __init__(self, n_filters=1):
        self.k = n_filters
    @staticmethod
    def _cov(X):
        c = np.mean([x @ x.T / np.trace(x @ x.T) for x in X], axis=0)
        return c
    def fit(self, X, y, classes):
        self.W = {}
        for c in classes:
            A, B = self._cov(X[y == c]), self._cov(X[y != c])
            w, V = linalg.eigh(A, A + B + 1e-6 * np.eye(len(A)))
            idx = list(range(self.k)) + list(range(-self.k, 0))
            self.W[c] = V[:, idx].T
        return self
    def transform(self, X):
        out = []
        for x in X:
            f = []
            for W in self.W.values():
                v = np.var(W @ x, axis=1); f.extend(np.log(v / v.sum() + 1e-9))
            out.append(f)
        return np.array(out)

class MIClassifier:
    def __init__(self, fs, bands=((8, 13), (13, 30)), classes=(0, 1, 2, 3), n_filters=1):
        self.fs, self.bands, self.classes, self.nf = fs, bands, classes, n_filters
    def _filt(self, X, band):
        b, a = signal.butter(3, band, btype="band", fs=self.fs)
        return signal.filtfilt(b, a, X, axis=-1)
    def _feats(self, X, fit_y=None):
        F = []
        for i, bd in enumerate(self.bands):
            Xb = self._filt(X, bd)
            if fit_y is not None:
                self.csp[i] = CSPOvR(self.nf).fit(Xb, fit_y, self.classes)
            F.append(self.csp[i].transform(Xb))
        return np.hstack(F)
    def fit(self, X, y):
        X, y = np.asarray(X), np.asarray(y)
        self.csp = [None] * len(self.bands)
        F = self._feats(X, y)
        self.lda = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto").fit(F, y)
        return self
    def predict_proba(self, X):
        return self.lda.predict_proba(self._feats(np.asarray(X)))
    def predict(self, X):
        return self.lda.classes_[self.predict_proba(X).argmax(1)]
