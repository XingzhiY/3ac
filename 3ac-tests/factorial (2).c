unsigned int factorial(unsigned int n) {
  unsigned int i;
  unsigned int o;

  o = 1;
  for(i = 1; i <= n; i++) {
    o = o * i;
  }

  return o;
}
