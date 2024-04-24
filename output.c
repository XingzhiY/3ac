int printf(const char *format, ...);
void main(void)
{
  int a;
  int b;
  int x;
  int y;
  int z;
  int c;
  int d;
  int e;
  a = 10;
  b = 47;
  int temp0;
  temp0 = a + b;
  x = temp0;
  int temp1;
  temp1 = a + b;
  y = temp1;
  int temp2;
  temp2 = y - b;
  z = temp2;
  c = a;
  d = 0;
  e = 0;
  int temp3;
  temp3 = y > 50;
  if (temp3)
    goto label0;
  goto label1;
  label0:
  1;

  int temp4;
  temp4 = x + z;
  c = temp4;
  int temp5;
  temp5 = a << 1;
  d = temp5;
  x = z;
  goto label2;
  label1:
  1;

  c = y;
  int temp6;
  temp6 = a + b;
  e = temp6;
  int temp7;
  temp7 = e - b;
  y = temp7;
  label2:
  1;

  int temp8;
  temp8 = printf("a:%d, b:%d, c:%d, d:%d, x:%d, y:%d, z:%d\n", a, b, c, d, x, y, z);
}

