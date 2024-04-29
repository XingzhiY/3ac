int printf(const char *format, ...);
int main(void)
{
  int a;
  int b;
  int c;
  int d;
  int e;
  b = 10;
  is_equal(b, 10);
  c = b;
  is_equal(c, 10);
  int temp0;
  is_equal(b, 10);
  is_equal(c, 10);
  temp0 = b + c;
  a = temp0;
  is_equal(a, temp0);
  int temp1;
  is_equal(c, 10);
  temp1 = a - c;
  d = temp1;
  is_equal(d, temp1);
  int temp2;
  is_equal(1, 1);
  temp2 = d << 1;
  e = temp2;
  is_equal(e, temp2);
  int temp3;
  temp3 = printf("a:%d b:%d c:%d d:%d e:%d\n", a, b, c, d, e);
}

