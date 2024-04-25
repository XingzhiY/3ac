int printf(const char *format, ...);

int main(void){
  int a, b, c, d, e;

  b = 10;

  c = b;
  a = b + c;
  d = a - c;
  e = d << 1;

  printf("a:%d b:%d c:%d d:%d e:%d\n", a, b, c, d, e);
}
