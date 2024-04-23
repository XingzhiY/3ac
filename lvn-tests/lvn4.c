int printf(const char *format, ...);

void main(void) {
  int a, b;
  int x, y, z, c, d, e;

  a = 10;
  b = 37;

  x = a + b;
  y = a + b;
  z = y - b;

  c = a;
  d = 0;
  e = 0;

  if(y > 50) {
    c = x + z;
    d = a << 1;
    x = z;
  } else {
    c = y;
    e = a + b;
    y = e - b;
  }

  printf("a:%d, b:%d, c:%d, d:%d, x:%d, y:%d, z:%d\n", a, b, c, d, x, y, z);
}
