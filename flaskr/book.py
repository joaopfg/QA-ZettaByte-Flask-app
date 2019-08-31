import functools

import warnings
warnings.filterwarnings('ignore')
import pickle
import numpy as np
import pandas as pd
import json
from textblob import TextBlob
import ast 
import nltk
nltk.download('punkt')
from scipy import spatial
import torch
import spacy
import PyPDF2 as PyPDF2
import tabula as tabula

import tika
tika.initVM()
from tika import parser
from models import InferSent

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('book', __name__, url_prefix='/book')

@bp.route('/initialpage', methods=('GET', 'POST'))
def initialpage():
    if request.method == 'POST':
        book_file = request.form['book']
        parsed = parser.from_file(book_file)
        book = parsed["content"]
        question = request.form['question']
        db = get_db()
        error = None

        if not book:
            error = 'Book is required.'
        elif not question:
            error = 'Question is required.'
 
        if error is None:
            if db.execute('SELECT book, question FROM bq').fetchone() is None:
                db.execute('INSERT INTO bq (book, question) VALUES (?, ?)',(book, question))
                db.commit()

            bq = db.execute('SELECT * FROM bq WHERE (book, question) = (?, ?)',(book, question)).fetchone()
            session.clear()
            session['bq_id'] = bq['id']
            return redirect(url_for('book.finalpage'))

        flash(error)

    return render_template('book/initialpage.html')


@bp.route('/finalpage')
def finalpage():
    bq_id = session.get('bq_id')

    if bq_id is None:
        g.bq = None
    else:
        g.bq = get_db().execute('SELECT * FROM bq WHERE id = ?', (bq_id,)).fetchone()

        context = g.bq['book']
        questions = []
        contexts = []
        questions.append(g.bq['question'])
        contexts.append(g.bq['book'])
        df = pd.DataFrame({"context":contexts, "question": questions})
        df.to_csv("flaskr/data/train.csv", index = None)
        blob = TextBlob(context)
        sentences = [item.raw for item in blob.sentences]

        from models import InferSent

        V = 1
        MODEL_PATH = 'flaskr/encoder/infersent%s.pkl' % V
        params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,'pool_type': 'max', 'dpout_model': 0.0, 'version': V}
        infersent = InferSent(params_model)
        infersent.load_state_dict(torch.load(MODEL_PATH))
        W2V_PATH = 'flaskr/GloVe/glove.840B.300d.txt'
        infersent.set_w2v_path(W2V_PATH)
        infersent.build_vocab(sentences, tokenize=True)

        dict_embeddings = {}
        for i in range(len(sentences)):
            dict_embeddings[sentences[i]] = infersent.encode([sentences[i]], tokenize=True)

        for i in range(len(questions)):
            dict_embeddings[questions[i]] = infersent.encode([questions[i]], tokenize=True)

        d1 = {key:dict_embeddings[key] for i, key in enumerate(dict_embeddings) if i % 2 == 0}
        d2 = {key:dict_embeddings[key] for i, key in enumerate(dict_embeddings) if i % 2 == 1}

        with open('flaskr/data/dict_embeddings1.pickle', 'wb') as handle:
            pickle.dump(d1, handle)

        with open('flaskr/data/dict_embeddings2.pickle', 'wb') as handle:
            pickle.dump(d2, handle)

        del dict_embeddings

        train = pd.read_csv("flaskr/data/train.csv")

        with open("flaskr/data/dict_embeddings1.pickle", "rb") as f:
            d1 = pickle.load(f)

        with open("flaskr/data/dict_embeddings2.pickle", "rb") as f:
            d2 = pickle.load(f)

        dict_emb = dict(d1)
        dict_emb.update(d2)

        del d1, d2

        train.dropna(inplace=True)

        train['sentences'] = train['context'].apply(lambda x: [item.raw for item in TextBlob(x).sentences])
        train['sent_emb'] = train['sentences'].apply(lambda x: [dict_emb[item][0] if item in dict_emb else np.zeros(4096) for item in x])
        train['quest_emb'] = train['question'].apply(lambda x: dict_emb[x] if x in dict_emb else np.zeros(4096) )

        li = []
    
        for i in range(len(train['question'])):
            laux = []
        
            for item in train["sent_emb"][i]:
                laux.append(spatial.distance.cosine(item,train["quest_emb"][i]))
        
            li.append(laux)

        train['cosine_sim'] = li
        train["pred_idx_cos"] = train["cosine_sim"].apply(lambda x: np.argmin(x))
        g.ans = train["sentences"][0][train['pred_idx_cos'][0]]
        get_db().execute('''DELETE FROM bq WHERE id = ? ''', (bq_id,))
        get_db().commit()

    return render_template('book/finalpage.html')