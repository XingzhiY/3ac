unsigned int gcd(unsigned int a, unsigned int b) {
  while(a > 0 && b > 0 && a != b) {
    if(a > b) a = a - b;
    if(b > a) b = b - a;
  }

  return a;
}
