# -*- coding: utf-8 -*-
"""
cgiモジュールの代替実装（Python 3.13対応）
cgi.FieldStorage()の互換実装を提供します。
"""

import os
import sys
import urllib.parse


class MiniFieldStorage:
  """フィールドの値を保持するクラス"""

  def __init__(self, name, value):
    self.name = name
    self.value = value


class FieldStorage:
  """cgi.FieldStorage()の代替実装"""

  def __init__(self):
    self._fields = {}
    self._load_data()

  def _load_data(self):
    """環境変数または標準入力からフォームデータを読み込む"""
    request_method = os.getenv("REQUEST_METHOD", "GET").upper()

    if request_method == "GET":
      query_string = os.getenv("QUERY_STRING", "")
      if query_string:
        parsed = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        for key, values in parsed.items():
          # 最初の値を.valueで取得できるようにする
          self._fields[key] = MiniFieldStorage(
              key, values[0] if values else ""
          )
    elif request_method == "POST":
      content_length_str = os.getenv("CONTENT_LENGTH", "0")
      try:
        content_length = int(content_length_str)
      except ValueError:
        content_length = 0

      if content_length > 0:
        # 標準入力から読み取り（バイナリモード）
        if hasattr(sys.stdin, "buffer"):
          data = sys.stdin.buffer.read(content_length)
        else:
          data = sys.stdin.read(content_length).encode("utf-8")
        query_string = data.decode("utf-8", errors="replace")
        parsed = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        for key, values in parsed.items():
          self._fields[key] = MiniFieldStorage(
            key, values[0] if values else ""
          )

  def __getitem__(self, key):
      """form["key"]でアクセスできるようにする"""
      if key not in self._fields:
        raise KeyError(key)
      return self._fields[key]

  def __contains__(self, key):
      """ "key" in form で存在チェックできるようにする"""
      return key in self._fields

  def getvalue(self, key, default=None):
      """値を取得する。存在しない場合はdefaultを返す"""
      if key in self._fields:
        return self._fields[key].value
      return default
