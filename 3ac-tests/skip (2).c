void skiptest(int n, int *skip) {
  int i;

  for(i = 0; i < n; i++) {
	if(skip[i]) continue;

	printf("processing %d\n", i);
  }
}
