# antar/antrean/mlr_utils.py
import os
import pickle
import numpy as np
import pandas as pd
from django.utils import timezone
from .models import Layanan, Antrean

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model_storage', 'model.pkl')  # model trained
QTABLE_PATH = os.path.join(BASE_DIR, 'model_storage', 'SJF_q_table.pkl')  # user-provided

# Config: bobot (MLR, Q)
WEIGHT_MLR = 0.3
WEIGHT_Q = 0.7

_loaded = {
    'payload': None,
    'qtable': None
}

def _load_model():
    if _loaded['payload'] is not None:
        return _loaded['payload']
    if not os.path.exists(MODEL_PATH):
        _loaded['payload'] = None
        return None
    with open(MODEL_PATH, 'rb') as f:
        payload = pickle.load(f)
    _loaded['payload'] = payload
    return payload

def _load_qtable():
    if _loaded['qtable'] is not None:
        return _loaded['qtable']
    if not os.path.exists(QTABLE_PATH):
        _loaded['qtable'] = None
        return None
    with open(QTABLE_PATH, 'rb') as f:
        q = pickle.load(f)
    _loaded['qtable'] = q
    return q

def predict_mlr_for_row(layanan_id, tgl_daftar_ts, waktu_mulai_ts=None):
    payload = _load_model()
    if payload is None:
        return None
    model = payload['model']
    layanan_ids = payload.get('layanan_ids', [])
    # build feature vector same order as training features
    feats = {}
    for l in layanan_ids:
        feats[f'layanan_{l}'] = 1 if l == layanan_id else 0
    feats['tgl_daftar_ts'] = tgl_daftar_ts
    feats['waktu_mulai_ts'] = waktu_mulai_ts if waktu_mulai_ts is not None else tgl_daftar_ts
    # create DataFrame and align with model features
    X = pd.DataFrame([feats])
    # ensure all required columns exist
    for col in payload['features']:
        if col not in X.columns:
            X[col] = 0
    X = X[payload['features']]
    pred = model.predict(X)[0]
    try:
        # ensure positive
        return max(float(pred), 0.0)
    except:
        return None

def predict_qtable(layanan_obj):
    # Q-table expected to be dict of lists like provided Q2,Q3,...
    q = _load_qtable()
    if q is None:
        return None
    # Map layanan.layanan (name) or layanan.id to an index in Q-table.
    # We'll attempt to map by layanan.id -> "Q{layanan.id}" if exists, else fallback to average.
    key = f"Q{layanan_obj.id}"
    if key in q:
        arr = q[key]
        # use median of Q values as baseline (robust)
        return float(np.median(arr))
    else:
        # fallback: use layanan.proses if qtable not contain key
        return float(layanan_obj.proses)

def predict_combined_duration(layanan_obj, tgl_daftar_ts=None, waktu_mulai_ts=None):
    """
    Return predicted duration in same unit as model/qtable (we assume minutes).
    Uses: final = WEIGHT_MLR * mlr + WEIGHT_Q * q
    If one source missing, fallback to the other.
    """
    q_pred = predict_qtable(layanan_obj)
    mlr_pred = None
    if tgl_daftar_ts is None:
        tgl_daftar_ts = int(timezone.now().timestamp())
    if not _load_model() is None:
        mlr_pred = predict_mlr_for_row(layanan_obj.id, tgl_daftar_ts, waktu_mulai_ts)

    if mlr_pred is None and q_pred is None:
        # absolute fallback
        return float(layanan_obj.proses)

    if mlr_pred is None:
        return float(q_pred)
    if q_pred is None:
        return float(mlr_pred)

    return float(WEIGHT_MLR * mlr_pred + WEIGHT_Q * q_pred)
