import unittest,json
from pathlib import Path
import numpy as np
from neuroassist.portable import PortableClassifier
from run_replay import ReplayEngine
ROOT=Path(__file__).resolve().parents[1]
class ReplayTests(unittest.TestCase):
    def test_saved_model_predictions(self):
        z=np.load(ROOT/'results/replay_S001.npz');m=PortableClassifier(ROOT/'models/S001.json')
        np.testing.assert_array_equal(m.predict(z['X']),z['pred'])
        np.testing.assert_allclose(m.predict_proba(z['X']).sum(1),1,atol=1e-12)
    def test_all_heldout_epochs_reach_keyboard_and_stop(self):
        e=ReplayEngine();e.start_demo()
        for _ in range(60):e.step()
        self.assertEqual(len(e.history),53);self.assertFalse(e.active)
        self.assertEqual(e.sent,sum(h['prediction']!=3 for h in e.history))
        self.assertEqual(e.state()['epoch'],53)
        self.assertEqual(e.state()['total'],53)
    def test_rest_produces_no_keypress(self):
        e=ReplayEngine();e.start_demo();e.clf.predict_proba=lambda _:np.array([[0,0,0,1]])
        before=e.scanner.state();e.step()
        self.assertEqual(e.scanner.state(),before);self.assertEqual(e.sent,0)
if __name__=='__main__':unittest.main()
