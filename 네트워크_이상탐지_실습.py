# -*- coding: utf-8 -*-
"""네트워크 이상탐지 실습

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QByz4k7UP0Lr5T8G6gUENtzn3fYXvvnP

### **PCAP을 활용한 침입 탐지 및 이상탐지 예제 실습**
"""

!pip install dpkt

"""### 패키지 임포트"""

import dpkt
import socket

"""### PCAP 파일 업로드 후 읽기"""

# 파일 업로드
from google.colab import files
uploaded = files.upload()
for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

from dpkt.utils import compat_ord
# 파일 읽기
file = '2-2.icmp_flooding.pcap'
f = open(file, 'rb')
pcap_file = dpkt.pcap.Reader(f)

"""### 패킷 확인"""

# inet_to_str 
def inet_to_str(inet):
  try:
    return socket.inet_ntop(socket.AF_INET, inet)
  except ValueError:
    return socket.inet_ntop(socket.AF_INET6, inet)

# mac_addr
def mac_addr(address):
  return ':'.join('%02x' % compat_ord(mac) for mac in address)

cnt = 1
for timestamp, buf in pcap_file:
  if cnt == 5: break
  print("timestamp:{}, length:{}, buf:{}".format(timestamp, len(buf), buf))

  ## buf 데이터를 dkpt 라이브러리 eth 클래스에 입력값으로 넣음
  eth = dpkt.ethernet.Ethernet(buf)

  ## MAC Address 확인
  print(eth.dst, eth.src)
  # print("MAC Address - dst:{}, MAC Address - src:{}".format(mac_addr(eth.dst), mac_addr(eth.src)))

  ## eth, eth.data, eth.data.data  타입 확인
  print(type(eth), type(eth.data), type(eth.data.data))

  ## eth.data의 dst, src 확인
  print(eth.data.dst, eth.data.src)
  # print("IP Address - dst:{}, IP Address - src:{}".format(inet_to_str(eth.data.src), inet_to_str(eth.data.dst)))
  
  print(type(eth),eth.pack)
  print(type(eth.data),eth.data.pack)
  print(type(eth.data.data),eth.data.data.pack)
  cnt +=1

"""

### Feature - BPS 구하기"""

# 파일 다시 읽기
file = '2-2.icmp_flooding.pcap'
f = open(file, 'rb')
pcap_file = dpkt.pcap.Reader(f)

## 변수
cnt = 1         ## 패킷 카운트
start_ts = 0.0  ## 시작 시간 
TW_size = 1.0   ## 타임윈도우 크기
SW_size = 1.0   ## 슬라이딩 크기
Bytes = 0       ## 누적 바이트 값


for timestamp, buf in pcap_file:
  if cnt == 1:
    start_ts = timestamp

  ## 시간 체크
  if timestamp <= start_ts + TW_size:
    Bytes += len(buf)
  elif timestamp > start_ts + TW_size:
    print(Bytes/1024.0, timestamp, start_ts + TW_size)

    Bytes = len(buf)      ## 현재 패킷의 bytes를 저장
    start_ts += TW_size   ## start timestamp를 새로운 기준 시간으로 변경
  cnt += 1

"""### Feature - PPS구하기

"""

# 파일 다시 읽기
file = '2-2.icmp_flooding.pcap'
f = open(file, 'rb')
pcap_file = dpkt.pcap.Reader(f)

## 변수
cnt = 1         ## 패킷 카운트
start_ts = 0.0  ## 시작 시간 
TW_size = 1.0   ## 타임윈도우 크기
SW_size = 1.0   ## 슬라이딩 크기
c_pkt = 1       ## 누적 바이트 값


for timestamp, buf in pcap_file:
  if cnt == 1:
    start_ts = timestamp

  ## 시간 체크
  if timestamp <= start_ts + TW_size:
    c_pkt += 1
  elif timestamp > start_ts + TW_size:
    print(c_pkt, timestamp, start_ts + TW_size)

    c_pkt = 1             ## 패킷수 1을 저장
    start_ts += TW_size   ## start timestamp를 새로운 기준 시간으로 변경
  cnt += 1

"""### KDD 데이터셋 샘플링 파일 Colab 머신에 업로드


"""

# 파일 업로드
from google.colab import files
uploaded = files.upload()
for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

!pip install collection

"""### 트래픽 유형 조사"""

import pandas as pd
from collections import Counter

kdd_df = pd.read_csv("kddcup_dataset.csv", index_col = None)

y = kdd_df["label"].values
Counter(y).most_common()

"""### 대상 목표 레이블의 이진화 수행"""

def label_abnormal(text):
  ### 대상 목표 레이블을 정상(normal) 또는 이상(abnormal)로 이진화 수행
  if text == "normal":
    return 0
  else:
    return 1

kdd_df["label"] = kdd_df["label"].apply(label_abnormal)

"""### 정상 관측 대비 이상 비율 계산"""

y = kdd_df["label"].values
# y
counts = Counter(y).most_common()
# counts

# counts[1][1] => normal인 label을 제외한 label을 가지고 있는 레코드 수
# counts[0][1] => normal인 label을 가지고 있는 레코드 수

abnormal_rate = counts[1][1] / (counts[0][1] + counts[1][1])
# abnormal_rate

"""### 범주형 특성 -> 수치형 변환"""

from sklearn.preprocessing import LabelEncoder

encodings_dict = dict()

for column_name in kdd_df.columns:
  if kdd_df[column_name].dtype == "object":
    encodings_dict[column_name] = LabelEncoder()
    kdd_df[column_name] = encodings_dict[column_name].fit_transform(kdd_df[column_name])

"""### 정상 관측 개체 및 이상 관측 개체 분할"""

kdd_df_normal = kdd_df[kdd_df["label"] == 0]
kdd_df_abnormal = kdd_df[kdd_df["label"] == 1]

y_normal = kdd_df_normal.pop("label").values
x_normal = kdd_df_normal.values

y_abnormal = kdd_df_abnormal.pop("label").values
x_abnormal = kdd_df_abnormal.values

"""### Train / Test 데이터 분할"""

from sklearn.model_selection import train_test_split
x_normal_train, x_normal_test, y_normal_train, y_normal_test = \
train_test_split(x_normal, y_normal, test_size=0.3, random_state=11)

x_abnormal_train, x_abnormal_test, y_abnormal_train, y_abnormal_test = \
train_test_split(x_abnormal, y_abnormal, test_size=0.3, random_state=11)

import numpy as np
x_train = np.concatenate((x_normal_train, x_abnormal_train))
y_train = np.concatenate((y_normal_train, y_abnormal_train))
x_test = np.concatenate((x_normal_test, x_abnormal_test))
y_test = np.concatenate((y_normal_test, y_abnormal_test))

"""### IsolationForest 분류기 알고리즘 적용"""

from sklearn.ensemble import IsolationForest

IF = IsolationForest(contamination = abnormal_rate)
IF.fit(x_train, y_train)

"""### **결과**"""

decisionScores_train_normal = IF.decision_function(x_normal_train)
decisionScores_train_abnormal = IF.decision_function(x_abnormal_train)

"""### 정상 데이터셋 점수 그래프"""

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt

# %matplotlib inline
plt.figure(figsize=(7,5))
plt.title("Training score histogram for normal network objects")
plt.xlabel("Score")
plt.ylabel("Freqeuncy")
_ = plt.hist(decisionScores_train_normal, bins=50)

"""### 이상 데이터셋 점수 그래프"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
plt.figure(figsize=(7,5))
plt.title("Training score histogram for abnormal network objects")
plt.xlabel("Score")
plt.ylabel("Freqeuncy")
_ = plt.hist(decisionScores_train_abnormal, bins=50)

"""### 정상 및 이상 관측치 구분을 위한 임계값 선택"""

Cutoff = 0

normal_in_test = Counter(y_test)[0]
abnormal_in_test = Counter(y_test)[1]
print("차단값을 적용 안했을 때 테스트 세트에서의 정상 패킷 수 :{}, 비정상 패킷 수{}".format(normal_in_test, abnormal_in_test))

cutoff_normal_in_test = Counter(y_test[Cutoff > IF.decision_function(x_test)])[0]
cutoff_abnormal_in_test = Counter(y_test[Cutoff > IF.decision_function(x_test)])[1]
print("차단값을 적용 했을 때 테스트 세트에서의 정상 패킷 수 :{}, 비정상 패킷 수{}".format(cutoff_normal_in_test, cutoff_abnormal_in_test))