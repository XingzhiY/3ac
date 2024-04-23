int printf(const char *format, ...);

void primefinder(int N, int *primes) {
  int np = 0;
  int is_prime = 0;
  int i, j;

  primes[0] = 2;
  np++;

  for(i = 3; i <= N; i++) {
    is_prime = 1;

    for(j = 0; j < np && primes[j] * primes[j] <= i; j++) {
      if(i % primes[j] == 0) {
		is_prime = 0;
		break;
      }
    }

    if(is_prime) {
      primes[np] = i;
      np++;
    }
  }

  for(i = 0; i < np; i++) {
    printf("%d: %d\n", i, primes[i]);
  }
}
