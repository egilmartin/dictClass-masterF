# -*- coding: utf-8 -*-
# @Author  : Kyusong Lee

from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
import os
import re
import string
import sys
from argparse import Namespace
from collections import defaultdict
from datetime import datetime

import nltk
from nltk.tokenize import RegexpTokenizer
# import torch
from nltk.tokenize.treebank import TreebankWordDetokenizer

INT = 0
LONG = 1
FLOAT = 2


class Pack(dict):
    def __getattr__(self, name):
        return self[name]

    def add(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v

    def copy(self):
        pack = Pack()
        for k, v in self.items():
            if type(v) is list:
                pack[k] = list(v)
            else:
                pack[k] = v
        return pack

    @staticmethod
    def msg_from_dict(dictionary, tokenize, speaker2id, bos_id, eos_id, include_domain=False):
        pack = Pack()
        for k, v in dictionary.items():
            pack[k] = v
        pack['speaker'] = speaker2id[pack.speaker]
        pack['conf'] = dictionary.get('conf', 1.0)
        utt = pack['utt']
        if 'QUERY' in utt or "RET" in utt:
            utt = str(utt)
            utt = utt.translate(None, ''.join([':', '"', "{", "}", "]", "["]))
            utt = unicode(utt)
        if include_domain:
            pack['utt'] = [bos_id, pack['speaker'], pack['domain']] + tokenize(utt) + [eos_id]
        else:
            pack['utt'] = [bos_id, pack['speaker']] + tokenize(utt) + [eos_id]
        return pack


def process_config(config):
    if config.forward_only:
        load_sess = config.load_sess
        backawrd = config.backward_size
        beam_size = config.beam_size
        gen_type = config.gen_type

        load_path = os.path.join(config.log_dir, load_sess, "params.json")
        config = load_config(load_path)
        config.forward_only = True
        config.load_sess = load_sess
        config.backward_size = backawrd
        config.beam_size = beam_size
        config.gen_type = gen_type
        # config.batch_size = 50
    return config


def prepare_dirs_loggers(config, script=""):
    logFormatter = logging.Formatter("%(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    if config.forward_only:
        return

    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir)

    dir_name = "{}-{}".format(get_time(), script) if script else get_time()
    config.session_dir = os.path.join(config.log_dir, dir_name)
    os.mkdir(config.session_dir)

    fileHandler = logging.FileHandler(os.path.join(config.session_dir,
                                                   'session.log'))
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    # save config
    param_path = os.path.join(config.session_dir, "params.json")
    with open(param_path, 'wb') as fp:
        json.dump(config.__dict__, fp, indent=4, sort_keys=True)


def load_config(load_path):
    data = json.load(open(load_path, "rb"))
    config = Namespace()
    config.__dict__ = data
    return config


def get_time():
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def str2bool(v):
    return v.lower() in ('true', '1')


def cast_type(var, dtype, use_gpu):
    if use_gpu:
        if dtype == INT:
            var = var.type(torch.cuda.IntTensor)
        elif dtype == LONG:
            var = var.type(torch.cuda.LongTensor)
        elif dtype == FLOAT:
            var = var.type(torch.cuda.FloatTensor)
        else:
            raise ValueError("Unknown dtype")
    else:
        if dtype == INT:
            var = var.type(torch.IntTensor)
        elif dtype == LONG:
            var = var.type(torch.LongTensor)
        elif dtype == FLOAT:
            var = var.type(torch.FloatTensor)
        else:
            raise ValueError("Unknown dtype")
    return var


def get_dekenize():
    return lambda x: TreebankWordDetokenizer().detokenize(x)


def get_char_detokenize():
    return lambda x: "".join(x)


def get_tokenize():
    return nltk.RegexpTokenizer(str(r'\w+|#\w+|<\w+>|%\w+|[^\w\s]+')).tokenize


def get_chat_tokenize():
    return nltk.RegexpTokenizer(str(r'\w+|<sil>|[^\w\s]+')).tokenize


def tokenize2char(sentence, max_utt_len=None):
    tokens = []
    deliminator = u'|||'
    PAUSE = u"<p>"

    tokenizer = RegexpTokenizer('[\u4E00-\u9FCC]|[0-9]+|[a-zA-Z]+|[%s]' % re.escape(string.punctuation))

    if type(sentence) is not unicode:
        sentence = unicode(sentence.decode('utf8'))

    sentence = re.sub('[?,~.‘’]', '', sentence)
    sentence = sentence.replace('基本功效是undefined', '')
    turns = sentence.split(PAUSE)
    if max_utt_len is not None:
        max_turn_len = int(max_utt_len/float(len(turns)))
    for t_id, turn in enumerate(turns):
        turn_segments = turn.split(deliminator)
        turn_tokens = []
        for s_id, seg in enumerate(turn_segments):
            if '...' == seg:
                turn_tokens.append(seg)
            elif u'http' in seg:
                turn_tokens.append(seg)
            else:
                turn_tokens.extend(tokenizer.tokenize(seg))

            if s_id < len(turn_segments) - 1:
                turn_tokens.append(deliminator)
        if max_utt_len is not None:
            turn_tokens = turn_tokens[0:max_turn_len]
        tokens.extend(turn_tokens)
        if t_id < len(turns) - 1:
            tokens.append(PAUSE)

    return tokens


class missingdict(defaultdict):
    def __missing__(self, key):
        return self.default_factory()


class InvalidUsage(Exception):
    status_code = 400
    """
    The exception contains:
    1. a dictionary containing message (required) and optional dictionary
    2. a status code (HTTP)
    """

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
