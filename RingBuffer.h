#ifndef RING_BUFFER_H
#define RING_BUFFER_H


struct RingBuffer {
  int i, len;
  double sum;
  int maxSize;
  double* buffer;
  
  RingBuffer(int ms): i(0), len(0), sum(0), maxSize(ms) {
    buffer = new double[maxSize];
  }
  ~RingBuffer() {
    delete[] buffer;
  }

  void insert(double v) {
    if (len == maxSize) {
      sum -= buffer[i];
    } else {
      len++;  
    }
    sum += v;
    buffer[i] = v;
    i = (i+1)%maxSize;
  }

  void clear() {
    sum = 0;
    i = 0;
    len = 0;  
  }

  void print() {
    Serial.print("i: ");Serial.print(i);
    Serial.print(", len: ");Serial.print(len);
    Serial.print(", sum: ");Serial.print(sum);
    Serial.print(", maxSize: ");Serial.println(maxSize);
  }
};

#endif
