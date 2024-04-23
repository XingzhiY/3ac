int printf(const char *format, ...);

int main(void)
{
  int n, s;

  n = 10;
  s = 0;
  
  while(n > 0) {
    s = s + n;
    n = n - 1;
  } 

  printf("n:%d s:%d\n", n, s);
}
