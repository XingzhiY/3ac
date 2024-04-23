int main(void) {
  int guess;
  int x;

  guess = rand();

  do {
	printf("Enter number: ");
	scanf("%d", &x);

	if (x < guess) {
	  printf("higher!\n");
	} else if (x > guess) {
	  printf("lower!\n");
	} else {
	  printf("correct!\n");
	}
  } while(x != guess);
}
